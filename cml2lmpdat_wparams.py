
from pathlib import Path


import networkx as nx
import numpy as np

from lammps_tools.forcefields.uff.parameterize import get_pair_potential, get_bond_parameters, \
    get_angle_parameters #, get_dihedral_parameters

from mofun import Atoms
from mofun.uff4mof import UFF4MOF
from mofun.atoms import find_unchanged_atom_pairs
from mofun.rough_uff import assign_uff_atom_types, default_uff_rules

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

def atomoto2lammpscoeff(angle_params):
    coeffs = []
    for atom_types, params in angle_params.items():
        if params[0] == "fourier":
            coeffs.append('%s %10.6f %10.6f %10.6f %10.6f # %s' % (*params, " ".join(atom_types)))
        elif params[0] == "cosine/periodic":
            coeffs.append('%s %10.6f %d %d # %s' % (*params, " ".join(atom_types)))
        else:
            raise Exception("Unhandled angle style '%s'" % params[0])
    return coeffs

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
    uff_types = assign_uff_atom_types(g, fnlinker.elements, override_rules=uff_rules)
    fnlinker.retype_atoms_from_uff_types(uff_types)

    # calculate all possible many-body terms
    fnlinker.calc_angles()
    # fnlinker.calc_dihedrals()

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
    pair_params = get_pair_potential(uff_types)
    fnlinker.pair_params = ['%10.6f %10.6f # %s' % (*pair_params[label], label) for label in fnlinker.atom_type_labels]

    bond_types = [tuple(sorted([uff_types[b1], uff_types[b2]])) for b1, b2 in fnlinker.bonds]
    bond_params = atomoto2tup(get_bond_parameters([tup2atomoto(b) for b in set(bond_types)]))
    fnlinker.bond_types = [list(bond_params).index(bt) for bt in bond_types]
    fnlinker.bond_type_params = ['%10.6f %10.6f # %s' % (*params, " ".join(atom_types)) for (atom_types, params) in bond_params.items()]

    angle_types = [tuple(sorted([uff_types[a] for a in atoms])) for atoms in fnlinker.angles]
    angle_values = [UFF4MOF[uff_types[a]][1] for _, a, _ in fnlinker.angles]
    angle_value_dict = {tup2atomoto(angle_type): [angle_values[i]] for i, angle_type in enumerate(angle_types)}
    angle_params = atomoto2tup(get_angle_parameters([tup2atomoto(a) for a in set(angle_types)], angle_value_dict))
    fnlinker.angle_type_params = atomoto2lammpscoeff(angle_params)
    fnlinker.angle_types = [list(angle_params).index(a) for a in angle_types]

    # TODO: need dihedral parameters from atomoto to do dihedrals

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
