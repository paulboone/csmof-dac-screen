"""
Take CIF file, optionally update with charges from chargefile, replicate to meet MIC, assign pair
potentials and output to a working LAMMPS Data file.
"""

import pathlib

import click
import numpy as np
from mofun import Atoms
from mofun.rough_uff import pair_coeffs
from mofun.uff4mof import uff_key_starts_with

@click.command()
@click.argument('inputpath', type=click.Path(path_type=pathlib.Path))
@click.argument('outputpath', type=click.Path(path_type=pathlib.Path))
@click.option('--dumppath', type=click.Path(path_type=pathlib.Path))
@click.option('-q', '--chargefile', type=click.File('r'))
@click.option('--mic', type=float, help="enforce minimum image convention using a cutoff of mic")
@click.option('--framework-element', type=str, help="convert all atoms that are in group 0, the framework group to a specific atom type to make vizualizing the structure easier")
@click.option('--pp', is_flag=True, default=False, help="Assign UFF pair potentials to atoms (sufficient for fixed force-field calculations)")
def mofun_converter(inputpath, outputpath, dumppath=None, chargefile=None, mic=None, framework_element=None, pp=False):
    atoms = Atoms.load(inputpath)

    # upate positions from lammps dump file
    if dumppath is not None:
        # update positions in original atoms file with new positions
        dumpatoms = ase.io.read(dumppath, format="lammps-dump-text")
        assert len(dumpatoms.positions) == len(atoms.positions)
        atoms.positions = dumpatoms.positions

    # update charges
    if chargefile is not None:
        charges = np.array([float(line.strip()) for line in chargefile if line.strip() != ''])
        assert len(charges) == len(atoms.positions)
        atoms.charges = charges

    # replicate to meet minimum image convention, if necessary
    if mic is not None:
        repls = np.array(np.ceil(2*mic / np.diag(atoms.cell)), dtype=int)
        atoms = atoms.replicate(repls)

    if pp:
        assign_pair_params_to_structure(atoms)

    # set framework elements to specified element-only works on ASE exports
    if framework_element is not None:
        atoms.symbols[atoms.atom_groups == 0] = framework_element

    if outputpath.suffix in ['.lmpdat', '.mol']:
        atoms.save(outputpath)
    else:
        print("INFO: Trying output using ASE")
        aseatoms = atoms.to_ase()
        if framework_element is not None:
            aseatoms.symbols[atoms.atom_groups == 0] = framework_element

        aseatoms.set_pbc(True)
        aseatoms.write(outputpath)

def assign_pair_params_to_structure(structure):
    # NOTE: in UFF, pair params should always be the same for atoms of the same element, regardless of type
    # DUPLICATE in functionalize_linkers.py: should be refactored
    uff_keys = [uff_key_starts_with(el.ljust(2, "_"))[0] for el in structure.atom_type_elements]
    structure.pair_coeffs = ['%10.6f %10.6f # %s' % (*pair_coeffs(k), k) for k in uff_keys]
    structure.atom_type_labels = uff_keys

if __name__ == '__main__':
    mofun_converter()
