
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
    epssims.drop(epssims[epssims.eps == "100x"].index, inplace=True)

    cm = plt.cm.get_cmap("tab20")
    fngcm = {
        'uio67':14, 'uio66':15,
        'NH2-2':2, 'NH2': 3,
        'CH3-2':4, 'CH3': 5,
        'CyNH-2':16, 'CyNH': 17,
    }

    fig = plt.figure(figsize=(6, 6))
    ax = fig.subplots()

    mofs = epssims["mof"].unique()
    moflabels = {
        "uio67-HNC6-ring-2": "CyNH-2",
        "uio67-HNC6-ring": "CyNH",
        "uio67-NH2-2": "NH2-2",
        "uio67-NH2": "NH2"
    }

    ax.set_xlim(0, len(mofs) + 1)
    ax.set_xticklabels([""] + [moflabels[m] for m in mofs] + [""], fontsize=fs, minor=False)
    ax.set_xlabel("Functional Group")
    ax.set_ylabel("Loading CC/g")
    for i, mof in enumerate(mofs):
        df = epssims[epssims.mof == mof]
        sc1 = ax.scatter([i + 1 ] * len(df.loading_cc_g), df.loading_cc_g, marker='_', zorder=10, color=cm(fngcm[moflabels[mof]]))
        for loading, eps in df[['loading_cc_g', 'eps']].itertuples(index=False, name=None):
            if eps == "1x":
                kwargs = dict(xytext=(-4,0), horizontalalignment="right")
            else:
                kwargs = dict(xytext=(4,0), horizontalalignment="left")
            ax.annotate(eps, (i + 1, loading), textcoords='offset points', verticalalignment='center', fontsize=fsl, **kwargs)
        if (exp.mof == mof).any():
            sc2 = ax.scatter([i + 1], exp[exp.mof == mof].loading_cc_g, color=cm(fngcm[moflabels[mof]]), marker='o')

    ax.grid(which='major', axis='y', linestyle='-', color='0.9', zorder=1)

    legend = []
    for mof, color in zip(mofs, [cm(fngcm[moflabels[m]]) for m in mofs]):
        legend.append(Line2D([0], [0], color=color, marker='o', label="%s (exp) " % mof))
        legend.append(Line2D([0], [0], color=color, marker='_', label="%s (sim) " % mof))
    ax.legend(handles=legend)

    fig.savefig(outputpath, dpi=300, bbox_inches='tight')#, transparent=True)
    plt.close(fig)


if __name__ == '__main__':
    sim_eps_vs_exp()
