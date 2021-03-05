from collections import Counter
from pathlib import Path

import numpy as np

from lammps_tools.forcefields.uff.parameterize import get_pair_potential

from mofun import Atoms, replace_pattern_in_structure
from mofun.uff4mof import uff_key_starts_with

structure_path = "mofs/uio-66.cif"
linker_path = "linkers-cml/uio66.cml"
fnlinker_path = "linkers-lmpdat/uio66-F.lmp-dat"

structure = Atoms.from_cif(structure_path)
linker = Atoms.from_cml(linker_path)
fnlinker = Atoms.from_lammps_data(open(fnlinker_path,"r"))

# NOTE: in UFF, pair params should always be the same for atoms of the same element, regardless of type
pair_uff_keys = [uff_key_starts_with(el.ljust(2, "_"))[0] for el in structure.atom_type_elements]
pair_params = get_pair_potential(pair_uff_keys)
structure.pair_params = ['%10.6f %10.6f # %s' % (*pair_params[label], label) for label in pair_uff_keys]

# structure.angles

new_structure = replace_pattern_in_structure(structure, linker, fnlinker)


#checks
Counter(structure.elements)
Counter(new_structure.elements)

set(new_structure.elements)
fnlinker.atom_types
fnlinker.pair_params
structure.atom_types
new_structure.pair_params
new_structure.bond_type_params
new_structure.angle_type_params
