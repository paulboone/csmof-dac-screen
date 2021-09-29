
import ase.io
import click
import numpy as np
from scipy.spatial import distance

from mofun import Atoms

@click.command()
@click.argument('structure_lmpdat', type=click.File('r'))
# @click.argument('gas_lmpdat', type=click.File('r'))
@click.option('-v', '--verbose', default=True, is_flag=True)
def check_config(structure_lmpdat, gas_lmpdat=None, verbose=True):
    atoms = Atoms.load(structure_lmpdat, filetype="lmpdat")
    # gas_atoms = Atoms.load(gas_lmpdat, filetype="lmpdat")
    # check for charges
    num_zero_charges = np.count_nonzero(atoms.charges == 0.0)
    if num_zero_charges > 0:
        print("WARNING: %d/%d atoms in structure have 0 charges" % (num_zero_charges, len(atoms.charges)))

    # num_zero_charges = np.count_nonzero(gas_atoms.charges == 0.0)
    # if num_zero_charges > 0:
    #     print("WARNING: %d/%d atoms in gas have 0 charges" % (num_zero_charges, len(gas_atoms.charges)))

    # check for overlapped atom positions
    # atoms.extend(gas_atoms)
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



if __name__ == '__main__':
    check_config()
