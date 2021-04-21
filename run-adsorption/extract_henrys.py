
import csv
from pathlib import Path
import sys

from mofun.raspa_output import parse_henrys


loadingcsv = csv.writer(sys.stdout)
loadingcsv.writerow(["mof", "gas", "henrys", "henrys_err", "gas", "henrys", "henrys_err", "gas", "henrys", "henrys_err"])

for outputpath in Path("../2021-04-15-ads/").glob("uio*_henrys/results/Output/System_0/*.data"):
    simname = outputpath.parts[2]
    mof, _ = simname.split("_")
    alldata = parse_henrys(outputpath)
    # loading, loading_error = alldata[0:2]
    loadingcsv.writerow([mof, *[x for y in alldata for x in y ]])
