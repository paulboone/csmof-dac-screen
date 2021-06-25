
import click
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas as pd


rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

fsl = fs = 9

@click.command()
@click.argument('csv-path', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="diffusivities.png")
def diffusivities(csv_path, outputpath="diffusivities.png"):

    fig = plt.figure(figsize=(12,6))

    # cm = matplotlib.cm.get_cmap("viridis")
    data = pd.read_csv(csv_path)

    uio66 = data[data.mof.str.startswith("UIO-66")]
    uio67 = data[data.mof.str.startswith("UIO-67")]
    moflabels = list(data.mof.str.replace("UIO-6[67] ", ""))

    ax = fig.subplots(ncols=1)

    break_indices = [0, 4, 10, 16, 22] + list(np.array([0, 4, 10, 16, 22]) + 28)
    adjusted_break_indices = [x + i for i, x in enumerate(break_indices)]
    for i in adjusted_break_indices:
        moflabels.insert(i, "")
    x_indices = list(range(len(moflabels)))
    for i in adjusted_break_indices:
        x_indices.remove(i)

    uio66x = x_indices[0:28]
    uio67x = x_indices[28:56]

    ax.set_xlim(0, len(moflabels))
    ax.set_ylim(-7, -2)

    sc1 = ax.plot(uio66x, np.log10(uio66.CO2), color="orange", zorder=2, markersize=3, marker="v", label="UIO-66 CO$_2$", linestyle='None')
    sc1 = ax.plot(uio67x, np.log10(uio67.CO2), color="orange", zorder=2, markersize=5, marker=r'$\bowtie$', label="UIO-67 CO$_2$", linestyle='None')

    sc1 = ax.plot(uio66x, np.log10(uio66.N2), color="grey", zorder=2, markersize=3, marker="v", label="UIO-66 N$_2$", linestyle='None')
    sc1 = ax.plot(uio67x, np.log10(uio67.N2), color="grey", zorder=2, markersize=5, marker= r'$\bowtie$', label="UIO-67 N$_2$", linestyle='None')

    sc1 = ax.plot(uio66x, np.log10(uio66.H2O), color="blue", zorder=2, markersize=3, marker="v", label="UIO-66 H$_2$O", linestyle='None')
    sc1 = ax.plot(uio67x, np.log10(uio67.H2O), color="blue", zorder=2, markersize=5, marker= r'$\bowtie$', label="UIO-67 H$_2$O", linestyle='None')

    ax.set_xticks(adjusted_break_indices)
    ax.set_xticklabels(["" for _ in adjusted_break_indices])
    ax.set_xticks(range(0,len(moflabels)), minor=True)
    ax.set_xticklabels(moflabels, rotation='vertical', fontsize=fs, minor=True)
    ax.set_ylabel('log10 diffusivity [Å$^2$ / fs] @ STP', fontsize=fsl)

    ax.grid(which='major', axis='y', linestyle='-', color='0.9', zorder=10)
    ax.grid(which='major', axis='x', linestyle='-', color='0.6', zorder=5)
    ax.grid(which='minor', axis='x', linestyle='--', color='0.9', zorder=0)

    ax.axvline(33, lw=0.75, color='black', zorder=30)

    ax.legend()
    fig.savefig(outputpath, dpi=300, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    diffusivities()
