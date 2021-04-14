from pathlib import Path

import numpy as np

from mofun import Atoms
from mofun.atoms import find_unchanged_atom_pairs


def check_cml_files(paths, linker, num_linkers, position_check_indices=[]):
    """ checks if more coordinates were changed in functionalized linker than just the newly added
    functional group atoms
    """
    for fnlinker_path in paths:
        fnlinker = Atoms.from_cml(fnlinker_path)
        match_pairs = find_unchanged_atom_pairs(linker, fnlinker)
        if len(match_pairs) == (len(linker) - num_linkers):
            marker = ""
        else:
            marker = "*"
            bad_indices = set(np.argwhere(fnlinker.positions[0:len(linker), :] != linker.positions[0:len(linker), :])[:,0])
            marker += ".".join([str(i + 1) for i in bad_indices])

        if (fnlinker[position_check_indices].positions != linker[position_check_indices].positions).any():
            position_marker = "P"
        else:
            position_marker = ""
        print("%s%s %s: unchanged %d/%d" % (marker, position_marker, fnlinker_path, len(match_pairs), len(fnlinker)))


# check UIO-66 linkers
linker_path = Path("linkers-cml/uio66.cml")
linker = Atoms.from_cml(linker_path)
all_linkers = list(Path("linkers-cml").glob("uio66-*.cml"))
double_linkers = list(Path("linkers-cml").glob("uio66-*-2.cml"))
non_double_linkers = set(all_linkers) - set(double_linkers)


print("\nUIO-66 two linkers")
check_cml_files(double_linkers, linker, 2, (0,14))
print("\nUIO-66 one linker (and more than two linkers)")
check_cml_files(non_double_linkers, linker, 1, (0,14))


# check UIO-67 linkers
linker_path = Path("linkers-cml/uio67.cml")
linker = Atoms.from_cml(linker_path)
all_linkers = list(Path("linkers-cml").glob("uio67-*.cml"))
double_linkers = list(Path("linkers-cml").glob("uio67-*-2.cml"))
non_double_linkers = set(all_linkers) - set(double_linkers)

print("\nUIO-67 two linkers")
check_cml_files(double_linkers, linker, 2, (1,21))
print("\nUIO-67 one linker (and more than two linkers)")
check_cml_files(non_double_linkers, linker, 1, (1,21))
