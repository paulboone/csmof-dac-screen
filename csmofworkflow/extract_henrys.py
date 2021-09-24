
import csv
from pathlib import Path
import sys

import click

from mofun.raspa_output import parse_henrys

@click.command()
@click.argument('glob')
def extract_henrys(glob):
    loadingcsv = csv.writer(sys.stdout)
    loadingcsv.writerow(["mof", "gas", "henrys_mol_kg_pa", "henrys_err", "gas", "henrys_mol_kg_pa", "henrys_err", "gas", "henrys_mol_kg_pa", "henrys_err", "molecules/uc->V/V", "mol/kg->V/V"])
    for outputpath in Path("./").glob(glob):
        simname = outputpath.parts[0]
        mof, _ = simname.split("_")
        alldata, molecules_uc_to_vv, molkg_to_vv = parse_henrys(outputpath)
        # loading, loading_error = alldata[0:2]
        loadingcsv.writerow([mof, *[x for y in alldata for x in y ], molecules_uc_to_vv, molkg_to_vv])

if __name__ == '__main__':
    extract_henrys()
