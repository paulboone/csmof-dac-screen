
from pathlib import Path

import click
import networkx as nx
import numpy as np

from mofun import Atoms
from mofun.uff4mof import UFF4MOF
from mofun.atoms import find_unchanged_atom_pairs
import mofun.rough_uff as ruff

def cml2lmpdat_typed_parameterized_for_new_atoms(fnlinker_path, linker_path=None, outpath="-"):

    uff_rules = {
        "H": [
            ("H_b", dict(n=2)),
            ("H_", {})
        ],
        "N": [
            ("N_R", dict(n=3, aromatic=True)),
            ("N_1", dict(neighbors=("N","N")))
        ],
        "O": [("O_1", dict(n=1))],
        "C": [("C_R", dict(n=3, aromatic=True))]
    }
    bond_order_rules = [({'N_1'}, 2), ({'N_1', 'N_2'}, 2)]

    fnlinker = Atoms.load(fnlinker_path)

    unchanged_atom_indices = []
    if linker_path is not None:
        # remove any dihedrals, angles and bonds that are unchanged from the original linker,
        # as we are only going to relax the new functional group, leaving everything else fixed.
        linker = Atoms.load(linker_path)

        match_pairs = find_unchanged_atom_pairs(linker, fnlinker)
        unchanged_atom_indices = set()
        if len(match_pairs) > 0:
            unchanged_atom_indices = set(list(zip(*match_pairs))[1])

        # assign atoms to molecules where 0 is original linker, 1 is for new functional group atoms
        fnlinker.groups = [0 if i in unchanged_atom_indices else 1 for i in range(len(fnlinker))]

    # calculate all possible many-body terms
    fnlinker.angles = ruff.calc_angles(fnlinker.bonds)
    fnlinker.dihedrals = ruff.calc_dihedrals(fnlinker.bonds)

    uff_types = ruff.calc_uff_atom_types(fnlinker.bonds, fnlinker.elements, override_rules=uff_rules)
    ruff.retype_atoms_from_uff_types(fnlinker, uff_types)

    print("Num dihedrals, angles, bonds: %d, %d, %d" % (len(fnlinker.dihedrals), len(fnlinker.angles), len(fnlinker.bonds)))
    ruff.assign_pair_coeffs(fnlinker)
    ruff.assign_bond_types(fnlinker, uff_types, bond_order_rules, exclude=unchanged_atom_indices)
    ruff.assign_angle_types(fnlinker, uff_types, bond_order_rules, exclude=unchanged_atom_indices)
    ruff.assign_dihedral_types(fnlinker, uff_types, bond_order_rules, exclude=unchanged_atom_indices)
    print("Num dihedrals, angles, bonds: %d, %d, %d" % (len(fnlinker.dihedrals), len(fnlinker.angles), len(fnlinker.bonds)))

    # output lammps-data file
    with open(outpath, "w") as f:
        fnlinker.save_lmpdat(f)

@click.command()
@click.argument('fnlinkers', nargs=-1, type=click.Path())
@click.option('--linker-path', type=click.Path())
@click.option('--outpath', '-o', type=click.Path())
def cml2lmpdat_wparams(fnlinkers, linker_path=None, outpath=Path()):
    outpath = Path(outpath)
    print(outpath)
    for fnlinker_path in fnlinkers:
        fnlinker_path = Path(fnlinker_path)
        print("\nreading %s" % fnlinker_path)
        try:
            print(linker_path, fnlinker_path)
            cml2lmpdat_typed_parameterized_for_new_atoms(fnlinker_path, linker_path, outpath.joinpath(fnlinker_path.stem + ".lmpdat"))
        except Exception as e:
            print("ERROR! ", e.args)


if __name__ == '__main__':
    cml2lmpdat_wparams()
