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
def lmpdat2cif(lmpdatpath, dumppath=None, outpath=None):
    atoms = Atoms.from_lammps_data(open(lmpdatpath, "r"), use_comment_for_type_labels=True)
    if dumppath is not None:
        # update positions in original atoms file with new positions
        dumpatoms = ase.io.read(dumppath, format="lammps-dump-text")
        assert len(dumpatoms.positions) == len(atoms.positions)
        atoms.positions = dumpatoms.positions
        atoms.to_lammps_data(open("test.lmpdat", "w"))

    # Overlapped atom position check
    s_ss = distance.cdist(atoms.positions, atoms.positions, "sqeuclidean")
    zero_indices = [(i1,i2) for i1, i2 in np.argwhere(s_ss < 0.1) if i1 < i2]
    for i1, i2 in zero_indices:
        print("WARNING: some atoms look like they are overlapped: %d %d dist=%6.4f" % (i1+1, i2+1, s_ss[i1,i2] ** 0.5))

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
