"""
Take existing functionalized mof lmpdat file, update the positions from a lammps dump, and resave.
"""

import ase.io
import click

from mofun import Atoms

@click.command()
@click.argument('lmpdatpath', type=click.Path())
@click.argument('dumppath', type=click.Path())
@click.argument('outputfile', type=click.File('w'))
def updatelmpdatpositions(lmpdatpath, dumppath, outputfile):
    atoms = Atoms.from_lammps_data(open(lmpdatpath, "r"), use_comment_for_type_labels=True)

    # update positions in original atoms file with new positions
    dumpatoms = ase.io.read(dumppath, format="lammps-dump-text")
    assert len(dumpatoms.positions) == len(atoms.positions)
    atoms.positions = dumpatoms.positions

    atoms.to_lammps_data(outputfile)

if __name__ == '__main__':
    updatelmpdatpositions()
