"""
Take existing functionalized mof lmpdat file, update the positions from a lammps dump, and resave.
"""
# import ase.io
import click
import numpy as np

from mofun import Atoms

@click.command()
@click.argument('ciffile', type=click.File('r'))
@click.argument('chargefile', type=click.File('r'))
@click.argument('outputfile', type=click.File('w'))
def generate_raspa_mol(ciffile, chargefile, outputfile):
    atoms = Atoms.from_cif(ciffile)

    # update charges
    charges = np.array([float(line.strip()) for line in chargefile if line.strip() != ''])
    assert len(charges) == len(atoms.positions)
    atoms.charges = charges

    atoms.to_mol(outputfile)

if __name__ == '__main__':
    generate_raspa_mol()
