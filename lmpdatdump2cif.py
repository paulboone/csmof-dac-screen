"""
Take existing functionalized mof lmpdat file, update the positions from a lammps dump, and
output a cif.

"""

import ase.io
import click
import numpy as np
from scipy.spatial import distance

from mofun import Atoms

@click.command()
@click.argument('lmpdatpath', type=click.Path())
@click.option('--dumppath', type=click.Path())
@click.option('--outpath', '-o', type=click.Path())
@click.option('--framework-element', type=str, help="convert all atoms that are in group 0, the framework group to a specific atom type to make vizualizing the structure easier")
def lmpdat2cif(lmpdatpath, dumppath=None, outpath=None, framework_element=None):
    atoms = Atoms.from_lammps_data(open(lmpdatpath, "r"), use_comment_for_type_labels=True)
    if dumppath is not None:
        # update positions in original atoms file with new positions
        dumpatoms = ase.io.read(dumppath, format="lammps-dump-text")
        assert len(dumpatoms.positions) == len(atoms.positions)
        atoms.positions = dumpatoms.positions

    aseatoms = atoms.to_ase()
    if framework_element is not None:
        aseatoms.symbols[atoms.atom_groups == 0] = framework_element

    aseatoms.set_pbc(True)
    if outpath is None:
        aseatoms.write('-', format="cif")
    else:
        aseatoms.write(outpath)

if __name__ == '__main__':
    lmpdat2cif()
