"""
Take existing functionalized mof lmpdat file, update the positions from a lammps dump, and
output a cif.

"""

import ase.io
import click
import numpy as np

from mofun import Atoms

@click.command()
@click.argument('lmpdatpath', type=click.Path())
@click.option('--dumppath', type=click.Path())
@click.option('--outpath', '-o', type=click.Path())
def lmpdat2cif(lmpdatpath, dumppath=None, outpath=None):
    atoms = Atoms.from_lammps_data(open(lmpdatpath, "r"))
    if dumppath is not None:
        # update positions in original atoms file with new positions
        dumpatoms = ase.io.read(dumppath, format="lammps-dump-text")
        assert len(dumpatoms.positions) == len(atoms.positions)
        atoms.positions = dumpatoms.positions

    dumpatoms.set_pbc(True)
    bonddists = np.array([dumpatoms.get_distance(b1,b2, mic=True)for b1, b2 in atoms.bonds])
    if (bonddists > dumpatoms.cell.lengths().min() / 2).any():
        print("WARNING: some bonds appear to have lengths > 1/2 the smallest UC dimension.")
        print(bonddists)
    else:
        print("INFO: all bonds have lengths < 1/2 the smallest UC dimension.")
        print("maximum bond length is %.2f Å" % max(bonddists))

    aseatoms = atoms.to_ase()
    aseatoms.set_pbc(True)
    if outpath is None:
        aseatoms.write('-', format="cif")
    else:
        aseatoms.write(outpath)

if __name__ == '__main__':
    lmpdat2cif()
