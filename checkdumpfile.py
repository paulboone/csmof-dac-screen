"""
check dump file

"""

import ase.io
import click
import numpy as np
from scipy.spatial import distance

from mofun import Atoms

@click.command()
@click.argument('lmpdatpath', type=click.Path())
@click.argument('dumppath', type=click.Path())
def checkdumpfile(lmpdatpath, dumppath):
    atoms = Atoms.from_lammps_data(open(lmpdatpath, "r"), use_comment_for_type_labels=True)
    dumpatoms = ase.io.read(dumppath, format="lammps-dump-text")
    assert len(dumpatoms.positions) == len(atoms.positions)
    atoms.positions = dumpatoms.positions

    # check for overlapped atom positions
    s_ss = distance.cdist(atoms.positions, atoms.positions, "sqeuclidean")
    minimum_dist = s_ss[np.triu_indices_from(s_ss, k=1)].min()
    print("Minimum distance between atoms: %6.4f" % minimum_dist**0.5)
    zero_indices = [(i1,i2) for i1, i2 in np.argwhere(s_ss < 0.1) if i1 < i2]
    for i1, i2 in zero_indices:
        print("WARNING: some atoms look like they are overlapped: %d %d dist=%6.4f" % (i1+1, i2+1, s_ss[i1,i2] ** 0.5))

    # check for bond distances
    dumpatoms.set_pbc(True)
    bonddists = np.array([dumpatoms.get_distance(b1,b2, mic=True) for b1, b2 in atoms.bonds])
    if (bonddists > dumpatoms.cell.lengths().min() / 2).any():
        print("WARNING: some bonds appear to have lengths > 1/2 the smallest UC dimension.")
        print(bonddists)
    else:
        print("INFO: all bonds have lengths < 1/2 the smallest UC dimension.")
    print("maximum bond length is %.2f Å" % max(bonddists))
    print("minimum bond length is %.2f Å" % min(bonddists))

if __name__ == '__main__':
    checkdumpfile()
