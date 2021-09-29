

from glob import glob
from os import path

import click
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas as pd

rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

fsl = fs = 9

@click.command()
@click.argument('csvfileglob', type=str)
@click.option('--outputpath', '-o', type=click.Path(), default="isotherms.png")
# @click.option('--plotnum', '-n', type=int, default=0)
def isotherms(csvfileglob, outputpath="isotherms.png"):
    fig = plt.figure(figsize=(7., 7.))
    ax = fig.subplots(ncols=1)

    cm = plt.cm.get_cmap("tab10")

    csvpaths = sorted(glob(csvfileglob))
    alldata = [pd.read_csv(csv) for csv in csvpaths]
    datanames = [path.basename(csv).removesuffix(".csv") for csv in csvpaths]

    fngroups = sorted({k.split("_")[0] for k in datanames})
    fn2cm = {k:i for i, k in enumerate(fngroups)}

    # ax.set_xlim(0, 1/1000)
    # ax.set_ylim(0, 0.6)

    for i, isodata in enumerate(alldata):
        isoname = datanames[i]
        marker = "s" if "CO2" in isoname else "o"
        ax.plot(isodata.pressure_bar, isodata.loading_cc_g, color=cm(fn2cm[isoname.split("_")[0]]), label=isoname, marker=marker, ms=4., zorder=10)

    ax.axvline(0.79, label="atmospheric N2", ls="--", lw=1, color=".1", zorder=5)
    ax.axvline(0.0004, label="atmospheric CO2", ls="--", lw=1, color=".1", zorder=5)

    ax.set_xlabel('Pressure (bar)', fontsize=fsl)
    ax.set_ylabel('Adsorption (CC/g)', fontsize=fsl)

    ax.grid(which='major', axis='both', linestyle='-', color='0.9', zorder=1)


    ax.legend()
    fig.savefig(outputpath, dpi=300, bbox_inches='tight') # , transparent=True
    plt.close(fig)




if __name__ == '__main__':
    isotherms()
