
import csv
from pathlib import Path
import sys

import click

from csmofworkflow.parse_raspa import parse_henrys

@click.command()
@click.argument('glob')
def extract_henrys(glob):
    loadingcsv = csv.writer(sys.stdout)
    loadingcsv.writerow(["mof", "gas", "henrys_mol_kg_pa", "henrys_err", "gas", "henrys_mol_kg_pa", "henrys_err", "gas",
        "henrys_mol_kg_pa", "henrys_err", "vv_per_m_uc", "vv_per_molkg", "molkg_per_m_uc", "uc_volume_a3"])
    for outputpath in Path("./").glob(glob):
        simname = outputpath.parts[0]
        mof, _ = simname.split("_")
        alldata, molecules_uc_to_vv, molkg_to_vv, molecules_uc_to_molkg, cell_volume_a3 = parse_henrys(outputpath)
        # loading, loading_error = alldata[0:2]
        loadingcsv.writerow([mof, *[x for y in alldata for x in y ], molecules_uc_to_vv, molkg_to_vv, molecules_uc_to_molkg, cell_volume_a3])

if __name__ == '__main__':
    extract_henrys()
