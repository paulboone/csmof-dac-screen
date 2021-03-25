"""
Take existing functionalized mof lmpdat file, update the positions from a lammps dump, and resave.
"""
# import ase.io
import click
import numpy as np
from mofun import Atoms

from functionalize_linkers import assign_pair_params_to_structure

@click.command()
@click.argument('ciffile', type=click.File('r'))
@click.argument('chargefile', type=click.File('r'))
@click.argument('outputfile', type=click.File('w'))
def generate_lammps_diffusion(ciffile, chargefile, outputfile):
    atoms = Atoms.from_cif(ciffile)

    # update charges
    charges = np.array([float(line.strip()) for line in chargefile if line.strip() != ''])
    assert len(charges) == len(atoms.positions)
    atoms.charges = charges

    assign_pair_params_to_structure(atoms)
    atoms.to_lammps_data(outputfile)

if __name__ == '__main__':
    generate_lammps_diffusion()
