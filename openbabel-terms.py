"""
Building OpenBabel on Ubuntu 18.04:

```
mkdir ob-build
cd ob-build
cmake -DPYTHON_EXECUTABLE=/Library/Frameworks/Python.framework/Versions/3.9/bin/python3 -DRUN_SWIG=ON -DPYTHON_BINDINGS=ON ..
make
make install
```
Installs in /usr/local/lib/python3.6/site-packages.

Likely you need the import below for adding this to your python3 run.

In OpenBabel, forcefielduff.cpp has the code we are interested in and can be modified to return the
parameters n and cos nphi:

```
OBFFLog("----ATOM TYPES-----    FORCE                     TORSION\n");
OBFFLog(" I    J    K    L     CONSTANT   n    ncosphi     ANGLE         ENERGY\n");
OBFFLog("--------------------------------------------------------------------\n");

// ...
snprintf(_logbuf, BUFF_SIZE, "%-5s %-5s %-5s %-5s%6.3f  %d  %6.3f      %8.3f     %8.3f\n",
        (*i).a->GetType(), (*i).b->GetType(),
        (*i).c->GetType(), (*i).d->GetType(), (*i).V, (*i).n, (*i).cosNPhi0,
        (*i).tor * RAD_TO_DEG, (*i).energy);
```
"""
import sys; sys.path.insert(0, "/usr/local/lib/python3.6/site-packages")

import os

from openbabel import OBMol, OBConversion, OBMolAtomIter, OBForceField

mof = "csdac-linkers-cml/uio66-HNC3-alkane.cml"

obconversion = OBConversion()
obconversion.SetInAndOutFormats("cml", "cml")
obmol = OBMol()
obconversion.ReadFile(obmol, mof)
ff = OBForceField.FindForceField("UFF")
ff.SetLogToStdOut()
ff.SetLogLevel(3)

if not ff.Setup(obmol):
    print("Error: could not setup force field")
ff.GetAtomTypes(obmol)

for atom_idx, obatom in enumerate(OBMolAtomIter(obmol)):
    ff_atom_type = obatom.GetData("FFAtomType").GetValue()
    print(ff_atom_type)

print(ff.Energy(True))
print(ff.E_Torsion())
print(obmol.GetEnergy())
