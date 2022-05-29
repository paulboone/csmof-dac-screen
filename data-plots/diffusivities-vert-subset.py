
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
@click.option('--outputpath', '-o', type=click.Path(), default="diffusivities-subset.png")
def diffusivities(csv_path, outputpath="diffusivities.png"):

    fig = plt.figure(figsize=(3.3,2), constrained_layout=True)
    data = pd.read_csv(csv_path)

    # convert to log10
    data.d_lower_co2_a2_fs.clip(lower=0, inplace=True)
    data.d_lower_n2_a2_fs.clip(lower=0, inplace=True)
    data.d_lower_h2o_a2_fs.clip(lower=0, inplace=True)

    logd_min = -7
    d_min = 1.2e-7
    data['d_co2'] = np.log10(data.d_co2_a2_fs.clip(lower=d_min))
    data['d_n2'] = np.log10(data.d_n2_a2_fs.clip(lower=d_min))
    data['d_h2o'] = np.log10(data.d_h2o_a2_fs.clip(lower=d_min))

    data['d_co2_deltl'] = data.d_co2 - np.log10(data.d_lower_co2_a2_fs).clip(lower=logd_min)
    data['d_co2_deltu'] = np.log10(data.d_upper_co2_a2_fs) - data.d_co2
    data['d_n2_deltl'] = data.d_n2 - np.log10(data.d_lower_n2_a2_fs).clip(lower=logd_min)
    data['d_n2_deltu'] = np.log10(data.d_upper_n2_a2_fs) - data.d_n2
    data['d_h2o_deltl'] = data.d_h2o - np.log10(data.d_lower_h2o_a2_fs).clip(lower=logd_min)
    data['d_h2o_deltu'] = np.log10(data.d_upper_h2o_a2_fs) - data.d_h2o

    data.mof = data.mof.str.replace("UIO", "UiO")
    uio67 = data[data.mof.str.startswith("UiO-67")].copy()
    uio67['moflabel'] = uio67.mof.str.replace("UiO-6[67] ", "")

    subset = ['UiO-67', '8x F', '2x CF$_3$', '2x OH', 'NH$_2$', '2x NH$_2$', '2x N$_3$', 'ring-HNC$_6$', '2x ring-HNC$_6$', '2x NC$_4$']
    print("subset: ", subset)
    subset.reverse()
    mofs = uio67[uio67.moflabel.isin(subset)]
    print("subset: ", subset)
    print(mofs)
    mofs = mofs.set_index('moflabel')
    mofs = mofs.reindex(index=subset)
    print(mofs)
    # moflabels = list(mofs.mof.str.replace("UiO-6[67] ", ""))

    ax = fig.subplots(ncols=1)

    # mof labels go from bottom to top
    # moflabels.reverse()


    # y_indices need to skip the break_indices we've added for visual formatting
    y_indices = np.array(range(len(mofs))) + 1

    ax.set_ylim(0, max(y_indices) + 2.4)
    ax.set_xlim(-7, -2)

    sc1 = ax.errorbar(mofs.d_co2, y_indices + 0.1, xerr=mofs[["d_co2_deltl", "d_co2_deltu"]].to_numpy().T, color="orange", zorder=20, linestyle='None', lw=1, markersize=5, marker='.',  label="CO$_2$")
    sc1 = ax.errorbar(mofs.d_n2,  y_indices, xerr=mofs[["d_n2_deltl", "d_n2_deltu"]].to_numpy().T, color="grey",           zorder=20, linestyle='None', lw=1, markersize=5, marker='.', label="N$_2$")
    sc1 = ax.errorbar(mofs.d_h2o, y_indices - 0.1, xerr=mofs[["d_h2o_deltl", "d_h2o_deltu"]].to_numpy().T, color="blue",   zorder=20, linestyle='None', lw=1, markersize=5, marker='.', label="H$_2$O")
    # ax..et_yticks(adjusted_break_indices)
    # ax.set_yticklabels(["" for _ in adjusted_break_indices])
    print(mofs.index)
    ax.set_yticks([], minor=False)
    ax.set_yticks(y_indices, minor=True)
    ax.set_yticklabels(mofs.index, minor=True, fontsize=fs)

    ax.set_xlabel('log10 diffusivity [Å$^2$ / fs] @ STP', fontsize=fs)

    ax.grid(which='major', axis='x', linestyle='-', color='0.9', zorder=10)
    ax.grid(which='major', axis='y', linestyle='-', color='0.6', zorder=5)
    ax.grid(which='minor', axis='y', linestyle='--', color='0.9', zorder=0)

    ax.axhline(35, lw=0.75, color='black', zorder=30)

    ax.legend(loc="upper center", ncol=3, columnspacing=1, handlelength=1, handletextpad=0.4)
    fig.savefig(outputpath, dpi=600, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    diffusivities()
