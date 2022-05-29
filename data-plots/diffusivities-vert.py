
import click
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas as pd

fsl = fs = 8
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
rc('font', size=fs)

@click.command()
@click.argument('csv-path', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="diffusivities.png")
def diffusivities(csv_path, outputpath="diffusivities.png"):

    fig = plt.figure(figsize=(6,10))
    data = pd.read_csv(csv_path)

    # convert to log10
    data.d_lower_co2_a2_fs.clip(lower=0, inplace=True)
    data.d_lower_n2_a2_fs.clip(lower=0, inplace=True)
    data.d_lower_h2o_a2_fs.clip(lower=0, inplace=True)

    logd_min = -7
    data['d_co2'] = np.log10(data.d_co2_a2_fs).clip(lower=logd_min + 0.1)
    data['d_n2'] = np.log10(data.d_n2_a2_fs).clip(lower=logd_min + 0.1)
    data['d_h2o'] = np.log10(data.d_h2o_a2_fs).clip(lower=logd_min + 0.1)

    data['d_co2_deltl'] = data.d_co2 - np.log10(data.d_lower_co2_a2_fs).clip(lower=logd_min)
    data['d_co2_deltu'] = np.log10(data.d_upper_co2_a2_fs) - data.d_co2
    data['d_n2_deltl'] = data.d_n2 - np.log10(data.d_lower_n2_a2_fs).clip(lower=logd_min)
    data['d_n2_deltu'] = np.log10(data.d_upper_n2_a2_fs) - data.d_n2
    data['d_h2o_deltl'] = data.d_h2o - np.log10(data.d_lower_h2o_a2_fs).clip(lower=logd_min)
    data['d_h2o_deltu'] = np.log10(data.d_upper_h2o_a2_fs) - data.d_h2o

    data.mof = data.mof.str.replace("UIO", "UiO")
    uio66 = data[data.mof.str.startswith("UiO-66")]
    uio67 = data[data.mof.str.startswith("UiO-67")]
    moflabels = list(data.mof.str.replace("UiO-6[67] ", ""))

    ax = fig.subplots(ncols=1)

    break_indices = [0, 6, 12, 18, 24] + list(np.array([0, 6, 12, 18, 24]) + 30)
    adjusted_break_indices = [x + i for i, x in enumerate(break_indices)]

    # mof labels go from bottom to top
    moflabels.reverse()
    for i in adjusted_break_indices:
        moflabels.insert(i, "")

    # y_indices need to skip the break_indices we've added for visual formatting
    y_indices = [x for x in range(len(moflabels)) if x not in adjusted_break_indices]
    y_indices.reverse()

    uio66y = np.array(y_indices[0:28])
    uio67y = np.array(y_indices[28:60])

    ax.set_ylim(0, len(moflabels))
    ax.set_xlim(-7, -2)

    sc1 = ax.errorbar(uio66.d_co2, uio66y + 0.1, xerr=uio66[["d_co2_deltl", "d_co2_deltu"]].to_numpy().T, color="orange", zorder=20, linestyle='None', lw=1, markersize=3, marker="v",           label="UIO-66 CO$_2$")
    sc1 = ax.errorbar(uio67.d_co2, uio67y + 0.1, xerr=uio67[["d_co2_deltl", "d_co2_deltu"]].to_numpy().T, color="orange", zorder=20, linestyle='None', lw=1, markersize=5, marker=r'$\bowtie$',  label="UIO-67 CO$_2$")
    sc1 = ax.errorbar(uio66.d_n2,  uio66y, xerr=uio66[["d_n2_deltl", "d_n2_deltu"]].to_numpy().T, color="grey",           zorder=20, linestyle='None', lw=1, markersize=3, marker="v",           label="UIO-66 N$_2$")
    sc1 = ax.errorbar(uio67.d_n2,  uio67y, xerr=uio67[["d_n2_deltl", "d_n2_deltu"]].to_numpy().T, color="grey",           zorder=20, linestyle='None', lw=1, markersize=5, marker= r'$\bowtie$', label="UIO-67 N$_2$")
    sc1 = ax.errorbar(uio66.d_h2o, uio66y - 0.1, xerr=uio66[["d_h2o_deltl", "d_h2o_deltu"]].to_numpy().T, color="blue",   zorder=20, linestyle='None', lw=1, markersize=3, marker="v",           label="UIO-66 H$_2$O")
    sc1 = ax.errorbar(uio67.d_h2o, uio67y - 0.1, xerr=uio67[["d_h2o_deltl", "d_h2o_deltu"]].to_numpy().T, color="blue",   zorder=20, linestyle='None', lw=1, markersize=5, marker= r'$\bowtie$', label="UIO-67 H$_2$O")

    ax.set_yticks(adjusted_break_indices)
    ax.set_yticklabels(["" for _ in adjusted_break_indices])
    ax.set_yticks(range(0,len(moflabels)), minor=True)
    ax.set_yticklabels(moflabels, minor=True, fontsize=fs)

    ax.set_xlabel('log10 diffusivity [Å$^2$ / fs] @ STP', fontsize=fs)

    ax.grid(which='major', axis='x', linestyle='-', color='0.9', zorder=10)
    ax.grid(which='major', axis='y', linestyle='-', color='0.6', zorder=5)
    ax.grid(which='minor', axis='y', linestyle='--', color='0.9', zorder=0)

    ax.axhline(35, lw=0.75, color='black', zorder=30)

    ax.legend()
    fig.savefig(outputpath, dpi=600, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    diffusivities()
