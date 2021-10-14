
import csv
from pathlib import Path
import sys

import click

from mofun.raspa_output import parse_gas_loading

@click.command()
@click.argument('glob')
@click.option('--pa2bar', default=False, is_flag=True, help="Pressure units are assumed to be in Pa, but can be converted to bar, if this flag is set.")
@click.option('--units', '-u', type=str, default='vv', help="units of loading: can be 'vv', 'cc_g', or 'molkg'.")
@click.option('--isothermruns', default=False, is_flag=True, help="If isothermruns=False, then the \
    mof, gas, and pressure are extracted from the highest level directory name, split by           \
    underscores. For example, './UIO66_CO2_1000/' or './UIO66_CO2_STP/'. If isothermruns=True, then\
    the mof is the highest-level directory, and the gas and pressure are split from the next       \
    directory, e.g. './UIO67/CO2_1000/'.")
def extract_loadings(glob, units='vv', pa2bar=False, isothermruns=False):
    loadingcsv = csv.writer(sys.stdout)
    if pa2bar:
        pressure_suffix = "bar"
    else:
        pressure_suffix = "Pa"

    loadingcsv.writerow(["mof", "gas", "pressure_%s" % pressure_suffix, "loading_%s" % units, "loading err",
                        "block1", "block2", "block3", "block4", "block5", "molecules/uc->V/V", "mol/kg->V/V"])

    for outputpath in Path("./").glob(glob):
        if isothermruns:
            mof = outputpath.parts[0]
            gas, pressure = outputpath.parts[1].split("-")
        else:
            mof, gas, pressure = outputpath.parts[0].split("_")

        alldata = parse_gas_loading(outputpath, units=units)
        loading, loading_error = alldata[0:2]
        if pa2bar:
            pressure = float(pressure) / 100000
        loadingcsv.writerow([mof, gas, pressure, *alldata])
