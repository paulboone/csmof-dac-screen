
import math

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
@click.option('--outputpath', '-o', type=click.Path(), default="loadings-subset.png")
def loadings(csv_path, outputpath="loadings.png"):
    fig = plt.figure(figsize=(3.3,2), constrained_layout=True)
    data = pd.read_csv(csv_path)

    logd_min = -7
    d_min = 1.2e-7
    data['a_co2'] = np.log10(data.a_co2_vv.clip(lower=d_min))
    data['a_n2'] = np.log10(data.a_n2_vv.clip(lower=d_min))
    data['a_h2o'] = np.log10(data.a_h2o_vv.clip(lower=d_min))

    data['a_co2_deltl'] = data.a_co2 - np.log10(data.a_co2_vv - data.a_co2_err_vv).clip(lower=logd_min)
    data['a_co2_deltu'] = np.log10(data.a_co2_vv + data.a_co2_err_vv) - data.a_co2
    data['a_n2_deltl'] = data.a_n2 - np.log10(data.a_n2_vv - data.a_n2_err_vv).clip(lower=logd_min)
    data['a_n2_deltu'] = np.log10(data.a_n2_vv + data.a_n2_err_vv) - data.a_n2
    data['a_h2o_deltl'] = data.a_h2o - np.log10(data.a_h2o_vv - data.a_h2o_err_vv).clip(lower=logd_min)
    data['a_h2o_deltu'] = np.log10(data.a_h2o_vv + data.a_h2o_err_vv) - data.a_h2o

    data.mof = data.mof.str.replace("UIO", "UiO")
    uio67 = data[data.mof.str.startswith("UiO-67")].copy()
    uio67['moflabel'] = uio67.mof.str.replace("UiO-6[67] ", "")

    subset = ['UiO-67', '8x F', '2x CF$_3$', '2x OH', 'NH$_2$', '2x NH$_2$', '2x N$_3$', 'ring-HNC$_6$', '2x ring-HNC$_6$', '2x NC$_4$']
    subset.reverse()
    mofs = uio67[uio67.moflabel.isin(subset)]
    mofs = mofs.set_index('moflabel')
    mofs = mofs.reindex(index=subset)

    ax = fig.subplots(ncols=1)
    y_indices = np.array(range(len(mofs))) + 1
    ax.set_ylim(0, max(y_indices) + 2.7)
    # ax.set_xlim(-3.5, 3)

    sc1 = ax.errorbar(np.log10(mofs.a_co2_vv), y_indices, xerr=mofs[["a_co2_deltl", "a_co2_deltu"]].to_numpy().T, color="orange", zorder=20, markersize=5, marker='.', label="CO$_2$", linestyle='None')
    sc1 = ax.errorbar(np.log10(mofs.a_n2_vv),  y_indices, xerr=mofs[["a_n2_deltl", "a_n2_deltu"]].to_numpy().T, color="grey", zorder=20, markersize=5, marker='.', label="N$_2$", linestyle='None')
    sc1 = ax.errorbar(np.log10(mofs.a_h2o_vv), y_indices, xerr=mofs[["a_h2o_deltl", "a_h2o_deltu"]].to_numpy().T, color="blue", zorder=20, markersize=5, marker='.', label="H$_2$O", linestyle='None')

    # ax.set_xticks([])
    ax.set_yticks([], minor=False)
    ax.set_yticks(y_indices, minor=True)
    ax.set_yticklabels(mofs.index, minor=True, fontsize=fs)

    ax.set_xlabel('log$_{10}$ loading [cm$^3$ gas STP / cm$^3$ framework]', fontsize=fsl)

    ax.grid(which='major', axis='x', linestyle='-', color='0.9', zorder=10)
    ax.grid(which='major', axis='y', linestyle='-', color='0.6', zorder=5)
    ax.grid(which='minor', axis='y', linestyle='--', color='0.9', zorder=0)

    ax.axvline(math.log10(0.8), lw=1, color="grey", zorder=5)
    ax.axvline(math.log10(2050 / 100000), lw=1, color="blue", zorder=5)
    ax.axvline(math.log10(400 / 1000000), lw=1, color="orange", zorder=5)

    ax.legend(loc="upper center", ncol=3, columnspacing=1, handlelength=1, handletextpad=0.4, framealpha=1.0)
    fig.savefig(outputpath, dpi=600, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    loadings()
