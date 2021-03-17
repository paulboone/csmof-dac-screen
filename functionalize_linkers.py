from collections import Counter
from pathlib import Path

from lammps_tools.forcefields.uff.parameterize import get_pair_potential
import numpy as np

from mofun import Atoms, replace_pattern_in_structure
from mofun.uff4mof import uff_key_starts_with

def functionalize_structure_with_linkers(structure, linker, fnlinkerglob):
    for fnlinker_path in fnlinkerglob:
        print("reading %s" %fnlinker_path)
        fnlinker = Atoms.from_lammps_data(open(fnlinker_path,"r"), use_comment_for_type_labels=True)
        try:
            new_structure = replace_pattern_in_structure(structure, linker, fnlinker)
            with open(lmp_base_path.joinpath(fnlinker_path.stem + ".lmp-dat"), "w") as fd:
                new_structure.to_lammps_data(fd)
        except Exception as e:
            print("ERROR! ", e.args)

def assign_pair_params_to_structure(structure):
    # NOTE: in UFF, pair params should always be the same for atoms of the same element, regardless of type
    pair_uff_keys = [uff_key_starts_with(el.ljust(2, "_"))[0] for el in structure.atom_type_elements]
    structure.atom_type_labels = pair_uff_keys
    pair_params = get_pair_potential(pair_uff_keys)
    structure.pair_params = ['%10.6f %10.6f # %s' % (*pair_params[label], label) for label in pair_uff_keys]

lmp_base_path = Path("mofs-functionalized")

linker = Atoms.from_cml(Path("linkers-cml/uio66.cml"))
structure = Atoms.from_cif("mofs/uio-66.cif")
assign_pair_params_to_structure(structure)
functionalize_structure_with_linkers(structure, linker, Path("linkers-lmpdat").glob("uio66-*"))

linker = Atoms.from_cml(Path("linkers-cml/uio67.cml"))
structure = Atoms.from_cif("mofs/uio-67.cif")
assign_pair_params_to_structure(structure)
functionalize_structure_with_linkers(structure, linker, Path("linkers-lmpdat").glob("uio67-*"))
