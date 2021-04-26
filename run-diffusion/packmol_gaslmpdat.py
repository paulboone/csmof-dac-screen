
import io
# import os
from pathlib import Path
import random
import subprocess

import click
import numpy as np
from angstrom.molecule import Cell
from angstrom.geometry import Plane

from mofun import Atoms

def packmol_config(structure_path, gas_path, output_path, num_molecules, boundary_tolerance, a2a_tolerance, supercell):
    """
    Two tolerances: (1) boundary_tolerance is the minimum distance between a gas molecule and one of
    the planes defining the boundary, (2) a2a_tolerance is the atom-to-atom tolerance defining the
    minimum distance between any two atoms.
    """

    cell = Cell(supercell)
    cell.calculate_vertices()
    pts = cell.vertices

    # would typically use vertices of (0,1,3), (2,4,5), (0,3,2), (1,6,4), (0,1,2), (3,5,6)
    # but only need the second in each pair because the planes are parallel. Since the first plane
    # will always have d = 0, we only need the second plane to define the triclinic bounds.
    # We can then bound the box using each plane twice, one where the plane > 0 and one where
    # the plane < d. Since we are normalizing the plane coefficients so that d is equal to the
    # appropriate unit cell lengths, d should be in units of angstroms. We can then add a tolerance
    # by just using plane > 1 or plane < d - 1 (for a one angstrom tolerance).

    plane_coefficients = []

    p = Plane(pts[2], pts[4], pts[5])
    n = p.d / cell.b # normalize by length of b
    a, b, c, d = (p.a / n, p.b / n, p.c / n, p.d / n)
    print("Using plane: %+.2fx %+.2fy %+.2fz = %.2f" % (a, b, c, d))
    plane_coefficients += [a, b, c, 0 + boundary_tolerance, a, b, c, d - boundary_tolerance]

    p = Plane(pts[1], pts[6], pts[4])
    n = p.d / cell.a # normalize by length of a
    a, b, c, d = (p.a / n, p.b / n, p.c / n, p.d / n)
    print("Using plane: %+.2fx %+.2fy %+.2fz = %.2f" % (a, b, c, d))
    plane_coefficients += [a, b, c, 0 + boundary_tolerance, a, b, c, d - boundary_tolerance]

    p = Plane(pts[3], pts[5], pts[6])
    n = p.d / cell.c # normalize by length of c
    a, b, c, d = (p.a / n, p.b / n, p.c / n, p.d / n)
    print("Using plane: %+.2fx %+.2fy %+.2fz = %.2f" % (a, b, c, d))
    plane_coefficients += [a, b, c, 0 + boundary_tolerance, a, b, c, d - boundary_tolerance]
    random_seed = random.randint(0,999999999)

    s = """
    tolerance %10.5f
    seed %d

    output %s
    filetype xyz

    structure %s
      filetype xyz
      number 1
      fixed 0 0 0 0 0 0
    end structure

    structure %s
      number %d

      over plane %10.5f %10.5f %10.5f %10.5f
      below plane %10.5f %10.5f %10.5f %10.5f

      over plane %10.5f %10.5f %10.5f %10.5f
      below plane %10.5f %10.5f %10.5f %10.5f

      over plane %10.5f %10.5f %10.5f %10.5f
      below plane %10.5f %10.5f %10.5f %10.5f
    end structure
    """ % (a2a_tolerance, random_seed, output_path, structure_path, gas_path, num_molecules, *plane_coefficients)

    return s

def extract_gas_atoms_from_packmol_xyz(packmol_xyz):
    """
    by _convention_ we are numbering atom types in the packmol input xyz as 101, 102, etc so that
    they do not conflict with atom types belonging to the structure (which should be fewer than
    100). Some XYZ readers do not like non-sequential atom types, so this is a very simple parser
    that filters an XYZ file for only lines with types > 100, and then subtracts the 100 to get
    expected types from 1-N.
    """
    with open(packmol_xyz, 'r') as f:
        f.readline()
        f.readline()
        xyz_data = []
        for row in f:
            row_list = row.strip().split()
            try:
                if int(row_list[0]) > 100:
                    row_list[0] = int(row_list[0]) - 100
                    xyz_data.append(row_list)
            except ValueError:
                pass
    return xyz_data


@click.command()

@click.argument('structure_lmpdat', type=click.File('r'))
@click.argument('structure_xyz', type=click.Path())
@click.argument('gas_lmpdat', type=click.Path())
@click.argument('gas_xyz', type=click.Path())
@click.option('-n', '--num-molecules', type=int, default=1)
def packmol_gaslmpdat(structure_lmpdat, structure_xyz, gas_lmpdat, gas_xyz, num_molecules=1):
    """ packs gas into structure using packmol and converts the result into a LAMMPS lmpdat file.

    The resulting lmpdat file has only the gas molecules in it, according to the geometry and coeffs
    of the gas_lmpdat file. Note that it is redundant to have both an XYZ file input and LAMMPS
    file input but we have it this way because this method is used in large-scale screenings and
    both these files are generated at the beginning of the run.

    Args:
        structure_lmpdat: lmpdat file of structure; this is used to get the unit cell for packmol.
        structure_xyz: Path to xyz file of structure to pack the gas into.
        gas_lmpdat: lmpdat file with geometry and coeffs for gas we are packing.
        gas_xyz: xyz file of gas corresponding to the the gas_lmpdat. Atoms must be in the same order!
        num_molecules (int): number of gas molecules to pack into structure.

    """
    gas_name = Path(gas_lmpdat).stem
    structure_name = Path(structure_xyz).stem

    satoms = Atoms.from_lammps_data(structure_lmpdat, use_comment_for_type_labels=True)

    output_gas_xyz = "%s_%s_packed.xyz" % (structure_name, gas_name)
    packmol_input = packmol_config(structure_xyz, gas_xyz, output_gas_xyz, num_molecules=num_molecules,
        boundary_tolerance=0, a2a_tolerance=1.5, supercell=[*np.diag(satoms.cell), 90, 90, 90])

    with open("packmol.input", 'w') as f:
        f.write(packmol_input)
    subprocess.run("/Users/pboone/workspace/_prereqs/packmol/packmol < packmol.input", shell=True, check=True)
    gas_data = np.array(extract_gas_atoms_from_packmol_xyz(output_gas_xyz))

    # update the dummy positions in the template gas lmpdat file with real positions from packmol
    # and save in the current directory. Note that this should NOT overwrite the template, since you
    # should be in a different directory at this point.
    atoms = Atoms.from_lammps_data(open(gas_lmpdat,'r'), use_comment_for_type_labels=True)
    atoms.positions = np.array(gas_data[:, 1:], dtype=float)
    atoms.atom_types = np.tile(atoms.atom_types, num_molecules)
    atoms.charges = np.tile(atoms.charges, num_molecules)
    atoms.atom_groups = np.repeat(np.arange(num_molecules), len(gas_data) / num_molecules)
    atoms.cell = satoms.cell

    atoms.to_lammps_data(open("%s.lmpdat" % gas_name, 'w'))
    Path("tmp").mkdir(exist_ok=True)
    Path("packmol.input").rename("tmp/packmol.input")
    Path(output_gas_xyz).rename(Path("tmp/") / output_gas_xyz)
    # atoms = Atoms(positions=np.array(gas_data[:,1:], dtype=float),
    #              atom_types=np.array(gas_data[:,0], dtype=int) - 1)

if __name__ == '__main__':
    packmol_gaslmpdat()

# #     ### output LAMMPS modification script
# #     with open("modify_lammps.sh", 'w') as f:
# #         random_seed = random.randint(0, 999999999)
# #         modify_lammps_script = """#!/bin/bash
# # if [ -z "$1" ]; then echo "USAGE: ./modify_lammps.sh <config.lammps>" && exit 1; fi
# # sed -i orig -e 's|^variable frameworkDataFile string .*$|variable frameworkDataFile string %s|' $1
# # sed -i ''   -e 's|^variable gasDataFile string .*$|variable gasDataFile string %s|' $1
# # sed -i ''   -e 's|^variable mofAtoms equal \d*.*$|variable mofAtoms equal %d|' $1
# # sed -i ''   -e 's|^variable mofBonds equal \d*.*$|variable mofBonds equal %d|' $1
# # sed -i ''   -e 's|^variable mofAngles equal \d*.*$|variable mofAngles equal %d|' $1
# # sed -i ''   -e 's|^variable mofDihedrals equal \d*.*$|variable mofDihedrals equal %d|' $1
# # sed -i ''   -e 's|^variable mofImpropers equal \d*.*$|variable mofImpropers equal %d|' $1
# # sed -i ''   -e 's|^variable randomSeed equal \d*.*$|variable randomSeed equal %d|' $1
# # """ % tuple([mof_lammps_data_file, gas_lammps_data_file] + num_types + [random_seed])
# #         f.write(modify_lammps_script)
#
