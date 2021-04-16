"""
Take existing functionalized mof lmpdat file, update the positions from a lammps dump, and resave.
"""

import click
import numpy as np
from mofun import Atoms
from mofun.rough_uff import pair_params
from mofun.uff4mof import uff_key_starts_with

@click.command()
@click.argument('ciffile', type=click.File('r'))
@click.argument('chargefile', type=click.File('r'))
@click.argument('outputfile', type=click.File('w'))
def cif2lmpdat_wcharges(ciffile, chargefile, outputfile):
    atoms = Atoms.from_cif(ciffile)

    # update charges
    charges = np.array([float(line.strip()) for line in chargefile if line.strip() != ''])
    assert len(charges) == len(atoms.positions)
    atoms.charges = charges

    assign_pair_params_to_structure(atoms)
    atoms.to_lammps_data(outputfile)

def assign_pair_params_to_structure(structure):
    # NOTE: in UFF, pair params should always be the same for atoms of the same element, regardless of type
    # DUPLICATE in functionalize_linkers.py: should be refactored
    uff_keys = [uff_key_starts_with(el.ljust(2, "_"))[0] for el in structure.atom_type_elements]
    structure.pair_params = ['%10.6f %10.6f # %s' % (*pair_params(k), k) for k in uff_keys]
    structure.atom_type_labels = uff_keys

if __name__ == '__main__':
    cif2lmpdat_wcharges()
