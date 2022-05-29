
import click
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

fsl = fs = 9

@click.command()
@click.argument('experimental_csv', type=click.File())
@click.argument('simulated_eps_csv', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="simeps-vs-exp.png")
def sim_eps_vs_exp(experimental_csv, simulated_eps_csv, outputpath="simeps-vs-exp.png"):
    exp = pd.read_csv(experimental_csv, skipinitialspace=True, comment="#")
    epssims = pd.read_csv(simulated_eps_csv, skipinitialspace=True, comment="#")

    epssims['mof'], epssims['eps'] = zip(*epssims['mof'].str.rsplit('_', n=1))
    epssims['eps'] = epssims['eps'].str.replace('EPS', '')
    # epssims.drop(epssims[epssims.eps == "100x"].index, inplace=True)

    cm = plt.cm.get_cmap("tab20")
    fngcm = {
        'uio67':14, 'uio66':15,
        'uio67-NH2-2':2, 'uio67-NH2': 3,
        'CH3-2':4, 'CH3': 5,
        'CyNH-2':16, 'CyNH': 17,
    }

    fig = plt.figure(figsize=(3.3, 3.3), constrained_layout=True)
    ax = fig.subplots()

    mofs = epssims["mof"].unique()
    mofs = ["uio67-NH2-2", "uio67-NH2"]
    moflabels = {
        "uio67-HNC6-ring-2": "CyNH-2",
        "uio67-HNC6-ring": "CyNH",
        "uio67-NH2-2": "2x NH$_2$",
        "uio67-NH2": "NH$_2$"
    }

    ax.set_ylim(0.00, 0.06)
    ax.set_xlim(0.5, 2.5)
    ax.set_xticks([0.5, 1, 2, 2.5])
    ax.set_xticklabels(["", "UiO-67-(2x NH$_2$)", "UiO-67-NH$_2$", ""])
    # ax.set_xticklabels([""] + [moflabels[m] for m in mofs] + [""], fontsize=fs, minor=False)
    # ax.set_xlabel("MOF")
    ax.set_ylabel("CO$_2$ Loading [CC/g]")
    for i, mof in enumerate(mofs):
        df = epssims[epssims.mof == mof]
        sc1 = ax.plot([i + 1 ] * len(df.loading_cc_g), df.loading_cc_g, marker='_', linewidth=0, color=cm(fngcm[mof]))
        for loading, eps in df[['loading_cc_g', 'eps']].itertuples(index=False, name=None):
            if eps == "1x":
                kwargs = dict(xytext=(-4,0), horizontalalignment="right")
            else:
                kwargs = dict(xytext=(4,0), horizontalalignment="left")
            ax.annotate(eps , (i + 1, loading), textcoords='offset points', verticalalignment='center', fontsize=fsl, **kwargs)
        if (exp.mof == mof).any():
            sc2 = ax.plot([i + 1], exp[exp.mof == mof].loading_cc_g, color=cm(fngcm[mof]), marker='o', linewidth=0, zorder=10)

    ax.grid(which='major', axis='y', linestyle='-', color='0.9', zorder=1)

    legend = []
    for mof, color in zip(mofs, [cm(fngcm[m]) for m in mofs]):
        legend.append(Line2D([0], [0], color=color, marker='o', linewidth=0, label="%s (exp) " % moflabels[mof]))
        legend.append(Line2D([0], [0], color=color, marker='_', linewidth=0, label="%s (sim) " % moflabels[mof]))
    ax.legend(handles=legend, ncol=2, loc="lower center", columnspacing=2, handlelength=1, handletextpad=0.4) # bbox_to_anchor=(0.2, 0.2, 0.6, 0.6)

    fig.savefig(outputpath, dpi=300, bbox_inches='tight')#, transparent=True)
    plt.close(fig)


if __name__ == '__main__':
    sim_eps_vs_exp()
