"""
convert all linkers to cif files, so our lammps-data file can be compared to the pete-boyd code

You will need to run
```
gsed -i -e 's/_atom_site_Cartn_/_atom_site_/g' *.cif
```
afterwards so that the cif has the labels that Lammps-interface requires

```fish
for x in ../linkers-cif/*.cif
    lammps-interface --molecule-ff=UFF $x
end
```
"""

from pathlib import Path

import numpy as np

from mofun import Atoms

out_path = Path("linkers-cif")
for fnlinker_path in Path("linkers-cml").glob("*.cml"):
    print("reading %s" %fnlinker_path)
    fnlinker = Atoms.from_cml(fnlinker_path)
    fnlinker.cell = cell=50*np.identity(3)
    fnlinker.to_ase().write(out_path.joinpath(fnlinker_path.stem + ".cif"))
