
import math

import click
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas as pd


rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# rc('text', usetex=True)

fsl = fs = 9



@click.command()
@click.argument('csv-path', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="loadings.png")
def loadings(csv_path, outputpath="loadings.png"):
    fig = plt.figure(figsize=(6,10))

    data = pd.read_csv(csv_path)
    uio66 = data[data.mof.str.startswith("UIO-66")]
    uio67 = data[data.mof.str.startswith("UIO-67")]
    moflabels = list(data.mof.str.replace("UIO-6[67] ", ""))

    ax = fig.subplots(ncols=1)

    break_indices = [0, 6, 12, 18, 24] + list(np.array([0, 6, 12, 18, 24]) + 28)
    adjusted_break_indices = [x + i for i, x in enumerate(break_indices)]

    # mof labels go from bottom to top
    moflabels.reverse()
    for i in adjusted_break_indices:
        moflabels.insert(i, "")

    # y_indices need to skip the break_indices we've added for visual formatting
    y_indices = [x for x in range(len(moflabels)) if x not in adjusted_break_indices]
    y_indices.reverse()

    uio66y = np.array(y_indices[0:28])
    uio67y = np.array(y_indices[28:56])

    ax.set_ylim(0, len(moflabels))

    sc1 = ax.plot(np.log10(uio66.loading_co2), uio66y, color="orange", zorder=20, markersize=3, marker="v", label="UIO-66 CO$_2$", linestyle='None')
    sc1 = ax.plot(np.log10(uio67.loading_co2), uio67y, color="orange", zorder=20, markersize=5, marker=r'$\bowtie$', label="UIO-67 CO$_2$", linestyle='None')

    sc1 = ax.plot(np.log10(uio66.loading_n2),  uio66y, color="grey", zorder=20, markersize=3, marker="v", label="UIO-66 N$_2$", linestyle='None')
    sc1 = ax.plot(np.log10(uio67.loading_n2),  uio67y, color="grey", zorder=20, markersize=5, marker= r'$\bowtie$', label="UIO-67 N$_2$", linestyle='None')

    sc1 = ax.plot(np.log10(uio66.loading_h2o), uio66y, color="blue", zorder=20, markersize=3, marker="v", label="UIO-66 H$_2$O", linestyle='None')
    sc1 = ax.plot(np.log10(uio67.loading_h2o), uio67y, color="blue", zorder=20, markersize=5, marker= r'$\bowtie$', label="UIO-67 H$_2$O", linestyle='None')


    ax.set_xlabel('log10 loading [cm3 gas STP / cm3 framework]', fontsize=fsl)

    ax.set_yticks(adjusted_break_indices)
    ax.set_yticklabels(["" for _ in adjusted_break_indices])
    ax.set_yticks(range(0,len(moflabels)), minor=True)
    ax.set_yticklabels(moflabels, fontsize=fs, minor=True)

    ax.grid(which='major', axis='x', linestyle='-', color='0.9', zorder=10)
    ax.grid(which='major', axis='y', linestyle='-', color='0.6', zorder=5)
    ax.grid(which='minor', axis='y', linestyle='--', color='0.9', zorder=0)

    ax.axhline(33, lw=0.75, color='black', zorder=30)

    ax.axvline(math.log10(0.8), lw=1, color="grey", zorder=11)
    ax.axvline(math.log10(2050 / 100000), lw=1, color="blue", zorder=11)
    ax.axvline(math.log10(400 / 1000000), lw=1, color="orange", zorder=11)

    ax.legend()
    fig.savefig(outputpath, dpi=300, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    loadings()
