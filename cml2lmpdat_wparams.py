
from pathlib import Path

import networkx as nx
import numpy as np

from mofun import Atoms
from mofun.uff4mof import UFF4MOF
from mofun.atoms import find_unchanged_atom_pairs
import mofun.rough_uff as ruff

def delete_if_all_in_set(arr, s):
    deletion_list = []
    for i, tup in enumerate(arr):
        if len(set(tup) - s) == 0:
            deletion_list.append(i)
    return np.delete(arr, deletion_list, axis=0)

def atomoto2tup(param_dict):
    return {tuple(key.split("-")): val for key, val in param_dict.items()}

def tup2atomoto(tup):
    return "-".join(tup)

def angle2lammpsdat(params):
    if params[0] == "fourier":
        return '%s %10.6f %10.6f %10.6f %10.6f # %s' % params
    elif params[0] == "cosine/periodic":
        return '%s %10.6f %d %d # %s' % params
    else:
        raise Exception("Unhandled angle style '%s'" % params[0])

def order_types(tup):
    rev = list(tup)
    rev.reverse()
    if tuple(rev) <= tuple(tup):
        return tuple(rev)
    return tuple(tup)



def cml2lmpdat_typed_parameterized_for_new_atoms(linker_path, fnlinker_path, lmpdat_path):

    uff_rules = {
        "H": [
            ("H_b", dict(h=2)),
            ("H_", {})
        ],
        "N": [("N_1", dict(h=0))],
        "O": [("O_1", dict(h=0))],
        "C": [("C_R", dict(aromatic=True))]
    }

    linker = Atoms.from_cml(linker_path)
    fnlinker = Atoms.from_cml(fnlinker_path)

    # assign uff atom types using mofun.rough_uff
    g = nx.Graph()
    g.add_edges_from(fnlinker.bonds)
    uff_types = ruff.assign_uff_atom_types(g, fnlinker.elements, override_rules=uff_rules)
    fnlinker.retype_atoms_from_uff_types(uff_types)

    # calculate all possible many-body terms
    fnlinker.calc_angles()
    fnlinker.calc_dihedrals()

    # remove any dihedrals, angles and bonds that are unchanged from the original linker,
    # as we are only going to relax the new functional group, leaving everything else fixed.
    print("Num dihedrals, angles, bonds: %d, %d, %d" % (len(fnlinker.dihedrals), len(fnlinker.angles), len(fnlinker.bonds)))
    match_pairs = find_unchanged_atom_pairs(linker, fnlinker)
    if len(match_pairs) > 0:
        unchanged_atom_indices = set(list(zip(*match_pairs))[1])
        fnlinker.bonds = delete_if_all_in_set(fnlinker.bonds, unchanged_atom_indices)
        fnlinker.angles = delete_if_all_in_set(fnlinker.angles, unchanged_atom_indices)
        fnlinker.dihedrals = delete_if_all_in_set(fnlinker.dihedrals, unchanged_atom_indices)
    print("Num dihedrals, angles, bonds: %d, %d, %d" % (len(fnlinker.dihedrals), len(fnlinker.angles), len(fnlinker.bonds)))

    # calculate potential parameters using atomoto, and assign type #s to linker
    fnlinker.pair_params = ['%10.6f %10.6f # %s' % (*ruff.pair_params(a1), a1) for a1 in fnlinker.atom_type_labels]

    bond_types = [order_types([uff_types[b1], uff_types[b2]]) for b1, b2 in fnlinker.bonds]
    unique_bond_types = list(dict.fromkeys(bond_types).keys())
    fnlinker.bond_types = [unique_bond_types.index(bt) for bt in bond_types]
    bond_params = [(*ruff.bond_params(a1, a2), "%s %s" % (a1, a2)) for (a1, a2) in unique_bond_types]
    fnlinker.bond_type_params = ['%10.6f %10.6f # %s' % params for params in bond_params]

    angle_types = [order_types([uff_types[a] for a in atoms]) for atoms in fnlinker.angles]
    unique_angle_types = list(dict.fromkeys(angle_types).keys())
    fnlinker.angle_types = [unique_angle_types.index(a) for a in angle_types]
    angle_params = [(*ruff.angle_params(*a_ids), "%s %s %s" % a_ids) for a_ids in unique_angle_types]
    fnlinker.angle_type_params = [angle2lammpsdat(a) for a in angle_params]

    dihedral_types = [order_types([uff_types[a] for a in atoms]) for atoms in fnlinker.dihedrals]
    unique_dihedral_types = list(dict.fromkeys(dihedral_types).keys())
    fnlinker.dihedral_types = [unique_dihedral_types.index(a) for a in dihedral_types]
    dihedral_params = [(*ruff.dihedral_params(*a_ids), "%s %s %s %s" % a_ids) for a_ids in unique_dihedral_types]
    fnlinker.dihedral_type_params = ['%s %10.6f %d %d # %s' % params for params in dihedral_params]

    # assign atoms to molecules where 0 is original linker, 1 is for new functional group atoms
    fnlinker.atom_groups = [0 if i in unchanged_atom_indices else 1 for i in range(len(fnlinker))]

    # output lammps-data file
    with open(lmpdat_path, "w") as f:
        fnlinker.to_lammps_data(f)


# convert UIO-66 linkers
linker_path = Path("linkers-cml/uio66.cml")
lmp_base_path = Path("linkers-lmpdat")
for fnlinker_path in Path("linkers-cml").glob("uio66-*"):
    print("reading %s" %fnlinker_path)
    try:
        cml2lmpdat_typed_parameterized_for_new_atoms(linker_path, fnlinker_path, lmp_base_path.joinpath(fnlinker_path.stem + ".lmp-dat"))
    except Exception as e:
        print("ERROR! ", e.args)

# convert UIO-67 linkers
linker_path = Path("linkers-cml/uio67.cml")
lmp_base_path = Path("linkers-lmpdat")
for fnlinker_path in Path("linkers-cml").glob("uio67-*"):
    print("reading %s" %fnlinker_path)
    try:
        cml2lmpdat_typed_parameterized_for_new_atoms(linker_path, fnlinker_path, lmp_base_path.joinpath(fnlinker_path.stem + ".lmp-dat"))
    except Exception as e:
        print("ERROR! ", e.args)
