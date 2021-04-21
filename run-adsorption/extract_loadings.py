
import csv
from pathlib import Path
import sys

from mofun.raspa_output import parse_gas_loading


loadingcsv = csv.writer(sys.stdout)
loadingcsv.writerow(["mof", "gas", "pressure", "loading", "loading err",
                    "block1", "block2", "block3", "block4", "block5", "conv"])

for outputpath in Path("../2021-04-15-ads/").glob("uio*_stp/results/Output/System_0/*.data"):
    simname = outputpath.parts[2]
    mof, gas, pressure = simname.split("_")
    alldata = parse_gas_loading(outputpath)
    loading, loading_error = alldata[0:2]
    loadingcsv.writerow([mof, gas, pressure, *alldata])

for outputpath in Path("../2021-04-15-ads/").glob("uio*_desorb/results/Output/System_0/*.data"):
    simname = outputpath.parts[2]
    mof, gas, pressure = simname.split("_")
    alldata = parse_gas_loading(outputpath)
    loading, loading_error = alldata[0:2]
    loadingcsv.writerow([mof, gas, pressure, *alldata])
