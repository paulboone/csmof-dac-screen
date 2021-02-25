
import os
# import ase

from ase.visualize import view
from lammps_tools.forcefields.uff.parameterize import *

from mofun import Atoms, replace_pattern_in_structure



uio66 = Atoms.from_cif("mofs/uio-66.cif")
uio66_linker = Atoms.from_cml(os.path.join("linkers-cml", "uio66.cml"))

uio66_linker_cyclopentane = Atoms.from_cml(os.path.join("linkers-cml", "uio66-cyclopentane.cml"))
final_structure = replace_pattern_in_structure(uio66, uio66_linker, uio66_linker_cyclopentane)
final_structure.to_ase().write("uio66-cyclopentane.cif")


# uio66_linker_hydroxy = Atoms.from_cml(os.path.join("linkers-cml", "uio66-hydroxy.cml"))
# final_structure = replace_pattern_in_structure(uio66, uio66_linker, uio66_linker_hydroxy)
# final_structure.to_ase().write("uio66-hydroxys.cif")


# view(final_structure.to_ase())

# final_structure.to_ase().write("uio66-hydroxys.cif")
# final_structure.to_ase().write("uio66-hydroxys.xyz")




# uio67 = Atoms.from_cif("mofs/uio-67.cif")
# uio67_linker = Atoms.from_cml(os.path.join("linkers-cml", "uio67.cml"))
# uio67_linker_cyclopentane = Atoms.from_cml(os.path.join("linkers-cml", "uio67-cyclopentane.cml"))
#
# final_structure = replace_pattern_in_structure(uio67, uio67_linker, uio67_linker_cyclopentane)
#
# view(uio67.to_ase())
# view(final_structure.to_ase())
#
# view(uio66.to_ase())
#
# uio66.to_ase().symbols
#
# final_structure = replace_pattern_in_structure(uio66, uio66_linker, uio66_linker_cyclopentane)
#
# view(final_structure.to_ase())
