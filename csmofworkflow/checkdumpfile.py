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
@click.option('--warns/--nowarns', default=True)
@click.option('-v', '--verbose', default=False, is_flag=True)
def checkdumpfile(lmpdatpath, dumppath, warns=True, verbose=False):
    atoms = Atoms.load(lmpdatpath)
    dumpatoms = ase.io.read(dumppath, format="lammps-dump-text")
    assert len(dumpatoms.positions) == len(atoms.positions)
    atoms.positions = dumpatoms.positions

    # check for overlapped atom positions
    s_ss = distance.cdist(atoms.positions, atoms.positions, "sqeuclidean")
    min_dist_sq = s_ss[np.triu_indices_from(s_ss, k=1)].min()
    min_dist_indices = list(zip(*np.where(s_ss == min_dist_sq)))
    min_dist = min_dist_sq ** 0.5
    if verbose:
        print("min distance between atoms: %6.4f" % min_dist)

    if verbose:
        zero_indices = [(i1,i2) for i1, i2 in np.argwhere(s_ss < 0.1) if i1 < i2]
        for i1, i2 in zero_indices:
            print("WARNING: some atoms look like they are overlapped: %d %d (%s-%s) dist=%6.4f" %
                (i1+1, i2+1, atoms.elements[i1], atoms.elements[i2], s_ss[i1,i2] ** 0.5))

    # check for bond distances
    dumpatoms.set_pbc(True)
    bonddists = np.array([dumpatoms.get_distance(b1,b2, mic=True) for b1, b2 in atoms.bonds])
    bonds_half_uc = (bonddists > dumpatoms.cell.lengths().min() / 2).any()
    if verbose:
        if bonds_half_uc:
            print("WARNING: some bonds appear to have lengths > 1/2 the smallest UC dimension.")
            print(bonddists)
        else:
            print("INFO: all bonds have lengths < 1/2 the smallest UC dimension.")
            print("maximum bond length is %.2f Å" % max(bonddists))
            print("min bond length is %.2f Å" % min(bonddists))
    else:
        if len(min_dist_indices) > 0:
            min_dist_indices_s = "(%4d %4d %2s - %-2s)" % (min_dist_indices[0][0] + 1, min_dist_indices[0][1] + 1,
                atoms.elements[min_dist_indices[0][0]], atoms.elements[min_dist_indices[0][1]])
        else:
            min_dist_indices_s = "(---- ----)"

        print("min_dist: %.2f %s; bonds: %.2f-%.2f" % (min_dist, min_dist_indices_s, min(bonddists), max(bonddists)), end='')
        if warns:
            if bonds_half_uc:
                print("; WARN: bonds > 1/2 UC", end='')
            if min_dist < 0.92 and min_dist < min(bonddists) - 1e-2:
                print("; WARN: atoms closer than shortest bond", end='')

if __name__ == '__main__':
    checkdumpfile()
