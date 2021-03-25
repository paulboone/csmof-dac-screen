"""
Take existing functionalized mof lmpdat file, update the positions from a lammps dump, and resave.
"""

# on macosx, openbabel installs here by default, and my attempts to move it have so far failed.
import site
site.addsitedir("/usr/local/lib/python3.9/site-packages/")

import ase.io
import click
from openbabel import openbabel, pybel

from mofun import Atoms, ATOMIC_MASSES

def atoms2obmol(atoms):
    atomic_num = lambda el: list(ATOMIC_MASSES.keys()).index(el) + 1
    mol = openbabel.OBMol()
    for i in range(len(atoms)):
        a = mol.NewAtom()
        a.SetVector(*atoms.positions[i])
        a.SetAtomicNum(atomic_num(atoms.elements[i]))
    return mol

@click.command()
@click.argument('lmpdatpath', type=click.Path())
@click.argument('dumppath', type=click.Path())
@click.argument('outputfile', type=click.File('w'))
def generate_raspa_mol(lmpdatpath, dumppath, outputfile):
    atoms = Atoms.from_lammps_data(open(lmpdatpath, "r"), use_comment_for_type_labels=True)

    # update positions in original atoms file with new positions
    dumpatoms = ase.io.read(dumppath, format="lammps-dump-text")
    assert len(dumpatoms.positions) == len(atoms.positions)
    atoms.positions = dumpatoms.positions

    pmol = pybel.Molecule(atoms2obmol(atoms))
    pmol.calccharges('eqeq')
    atoms.charges = np.array([a.partialcharge for a in pmol])

    atoms.to_mol(outputfile)

if __name__ == '__main__':
    generate_raspa_mol()
