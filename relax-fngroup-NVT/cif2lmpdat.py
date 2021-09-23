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
@click.argument('outputfile', type=click.File('w'))
@click.option('-q', '--chargefile', type=click.File('r'))
@click.option('--mic', type=float, help="enforce minimum image convention using a cutoff of mic")
def cif2lmpdat(ciffile, outputfile, chargefile=None, mic=None):
    atoms = Atoms.from_cif(ciffile)

    # update charges
    if chargefile is not None:
        charges = np.array([float(line.strip()) for line in chargefile if line.strip() != ''])
        assert len(charges) == len(atoms.positions)
        atoms.charges = charges

    # replicate to meet minimum image convention, if necessary
    if mic is not None:
        repls = np.array(np.ceil(2*mic / np.diag(atoms.cell)), dtype=int)
        atoms = atoms.replicate(repls)

    assign_pair_params_to_structure(atoms)
    atoms.to_lammps_data(outputfile)

def assign_pair_params_to_structure(structure):
    # NOTE: in UFF, pair params should always be the same for atoms of the same element, regardless of type
    # DUPLICATE in functionalize_linkers.py: should be refactored
    uff_keys = [uff_key_starts_with(el.ljust(2, "_"))[0] for el in structure.atom_type_elements]
    structure.pair_params = ['%10.6f %10.6f # %s' % (*pair_params(k), k) for k in uff_keys]
    structure.atom_type_labels = uff_keys

if __name__ == '__main__':
    cif2lmpdat()
