
import csv
from pathlib import Path
import sys

import click

from mofun.raspa_output import parse_gas_loading

@click.command()
@click.argument('glob')
def extract_loadings(glob):
    loadingcsv = csv.writer(sys.stdout)
    loadingcsv.writerow(["mof", "gas", "pressure", "loading", "loading err",
                        "block1", "block2", "block3", "block4", "block5", "molecules/uc->V/V", "mol/kg->V/V"])

    for outputpath in Path("./").glob(glob):
        simname = outputpath.parts[0]
        mof, gas, pressure = simname.split("_")
        alldata = parse_gas_loading(outputpath, units='vv')
        loading, loading_error = alldata[0:2]
        loadingcsv.writerow([mof, gas, pressure, *alldata])

if __name__ == '__main__':
    extract_loadings()
