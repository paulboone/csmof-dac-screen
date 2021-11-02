

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
@click.option('--xlim', type=float, default=None)
@click.option('--ylim', type=float, default=None)
def isotherms(csvfileglob, outputpath="isotherms.png", xlim=None, ylim=None):
    fig = plt.figure(figsize=(7., 7.))
    ax = fig.subplots(ncols=1)

    cm = plt.cm.get_cmap("tab20")
    fngcm = {
        'uio67':14, 'uio66':15,
        'NH2-2':2, 'NH2': 3,
        'CH3-2':4, 'CH3': 5,
    }

    csvpaths = sorted(glob(csvfileglob))
    alldata = [pd.read_csv(csv) for csv in csvpaths]
    datanames = [path.basename(csv).removesuffix(".csv") for csv in csvpaths]
    fngroups = sorted({k.split("_")[0] for k in datanames})
    legendnames = [d.replace("uio67-", "").replace("_N2@77K_", " N2@77K ") for d in datanames]
    legendnames = [d.replace("uio67-", "").replace("_CO2_", " CO2 ") for d in legendnames]
    legendnames = [d.replace("uio67-", "").replace("_N2_", " N2 ") for d in legendnames]

    fn2cm = {k:i for i, k in enumerate(fngroups)}

    if xlim is not None:
        ax.set_xlim(0, xlim)
    if ylim is not None:
        ax.set_ylim(0, ylim)



    for i, isodata in enumerate(alldata):
        isoname = datanames[i]
        legendname = legendnames[i]
        marker = "$\\backslash\\backslash$" if "-2_" in isoname else "$\\backslash$"

        if "_hyd" in isoname:
            linestyle = "--"
        elif "_deh" in isoname:
            linestyle = "dashdot"
        elif "_sim100K" in isoname:
            linestyle = "dashdot"
        elif "_sim" in isoname:
            linestyle = "--"
        else:
            linestyle = "-"

        if 'loading_err' in isodata:
            errbars = isodata.loading_err
            marker = None
        else:
            errbars = None
            marker = 'o'
        ax.errorbar(isodata.pressure_bar, isodata.loading_cc_g, errbars, color=cm(fngcm[legendname.split(" ")[0]]), lw=1.0, linestyle=linestyle, label=legendname, zorder=10, capsize=2, marker=marker, ms=2) # capthick=0.5

    ax.axvline(0.79, label="atmospheric N2", ls="--", lw=1.0, color=".1", zorder=5)
    ax.axvline(0.0004, label="atmospheric CO2", ls="--", lw=1.0, color=".1", zorder=5)

    ax.set_xlabel('Pressure (bar)', fontsize=fsl)
    ax.set_ylabel('Adsorption (CC/g)', fontsize=fsl)

    ax.grid(which='major', axis='both', linestyle='-', color='0.9', zorder=1)

    ax.legend()
    fig.savefig(outputpath, dpi=300, bbox_inches='tight') # , transparent=True
    plt.close(fig)

if __name__ == '__main__':
    isotherms()
