
import itertools
import os

import ase
import networkx as nx

from lammps_tools.forcefields.uff.parameterize import *

from mofun import Atoms
from mofun.atoms import find_unchanged_atom_pairs

linker = Atoms.from_cml(os.path.join("linkers-cml","uio66.cml"))
fnlinker = Atoms.from_cml(os.path.join("linkers-cml","uio66-hydroxy.cml"))

match_pairs = find_unchanged_atom_pairs(linker, fnlinker)
unchanged_atom_indices = set(list(zip(*match_pairs))[1])

fnlinker.calc_angles()
fnlinker.calc_dihedrals()

print("Num dihedrals, angles, bonds: %d, %d, %d" % (len(fnlinker.dihedrals), len(fnlinker.angles), len(fnlinker.bonds)))

def delete_if_all_in_set(arr, s):
    deletion_list = []
    for i, tup in enumerate(arr):
        if len(set(tup) - s) == 0:
            deletion_list.append(i)
    return np.delete(arr, deletion_list, axis=0)

fnlinker.bonds = delete_if_all_in_set(fnlinker.bonds, unchanged_atom_indices)
fnlinker.angles = delete_if_all_in_set(fnlinker.angles, unchanged_atom_indices)
fnlinker.dihedrals = delete_if_all_in_set(fnlinker.dihedrals, unchanged_atom_indices)

print("Num dihedrals, angles, bonds: %d, %d, %d" % (len(fnlinker.dihedrals), len(fnlinker.angles), len(fnlinker.bonds)))

bonds_with = [[] for _ in range(len(fnlinker))]
for (i1, i2) in fnlinker.bonds:
    bonds_with[i1].append(i2)
    bonds_with[i2].append(i1)


# g = nx.Graph()
# g.add_edges_from(fnlinker.bonds)
# g
# g.edges
# g.adj[6]
fnlinker.symbols
fnlinker.to_ase()

ase_atoms = ase.Atoms(fnlinker.elements, positions=fnlinker.positions)

assign_forcefield_atom_types(ase_atoms, bonds_with)
#
#
#
#
# get_pair_potential(["C_2", "O2", "H_", "F_"])
# get_bond_parameters(["C_2-H_"])
# get_bond_parameters(["C_R-H_"])
# get_angle_parameters(["C_2-C_2-F_"], {"C_2-C_2-F_":[120]})
#
#
# # ase.Atoms.
# #
#
# #
# # aatoms = ase.Atoms(atoms.map_atom_types(lammps_atom_type_map), positions=atoms.positions)
# # aatoms.translate((5,5,5))
# # aatoms.positions %= 50
# # aatoms.write("uio66-linker-2.cif")
