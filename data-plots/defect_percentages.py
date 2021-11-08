
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
@click.argument('simulated_defects_csv', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="defect_percentages.png")
def defect_percentages(experimental_csv, simulated_defects_csv, outputpath="defect_percentages.png"):
    exp = pd.read_csv(experimental_csv, skipinitialspace=True, comment="#")
    exp.mof = exp.mof.str.replace("uio67-", "")

    sims = pd.read_csv(simulated_defects_csv, skipinitialspace=True, comment="#")
    sims['defect_percent'] = sims['mof'].replace(r'.*defective00.*', '0', regex=True)
    sims['defect_percent'].replace(r'.*defective05.*', '5', regex=True, inplace=True)
    sims['defect_percent'].replace(r'.*defective10.*', '10', regex=True, inplace=True)
    sims['defect_percent'].replace(r'.*defective15.*', '15', regex=True, inplace=True)
    sims['defect_percent'].replace(r'.*defective20.*', '20', regex=True, inplace=True)
    sims['mof'].replace(r'-defective..', '', regex=True, inplace=True)
    sims.mof = sims.mof.str.replace("uio67-", "")
    sims.mof = sims.mof.str.replace("HNC6-ring", "CyNH")

    cm = plt.cm.get_cmap("tab20")
    fngcm = {
        'uio67':14, 'uio66':15,
        'NH2-2':2, 'NH2': 3,
        'CH3-2':4, 'CH3': 5,
        'CyNH-2':16, 'CyNH': 17,
    }
    print(sims)

    mofs = sims["mof"].unique()
    fig = plt.figure(figsize=(9, 6))
    ax = fig.subplots()
    ax.set_xlim(0, len(mofs) + 1)
    ax.set_xticklabels([""] + list(mofs) + [""], fontsize=fs, minor=False)
    # ax.set_xticklabels(moflabels, rotation='vertical', fontsize=fs, minor=True)
    # ax.set_ylim(0, 3500)
    ax.set_xlabel("Functional Group")
    ax.set_ylabel("Loading CC/g")
    for i, mof in enumerate(mofs):
        df = sims[sims.mof == mof]
        sc1 = ax.scatter([i + 1 ] * len(df.loading_cc_g), df.loading_cc_g, marker='_', zorder=10, color=cm(fngcm[mof]))
        for loading, defect_percent in df[['loading_cc_g', 'defect_percent']].itertuples(index=False, name=None):
            if int(defect_percent) in [5, 15]:
                kwargs = dict(xytext=(-4,0), horizontalalignment="right")
            else:
                kwargs = dict(xytext=(4,0), horizontalalignment="left")
            ax.annotate(str(defect_percent) + "%", (i + 1, loading), textcoords='offset points', verticalalignment='center', fontsize=fsl, **kwargs)
        if (exp.mof == mof).any():
            sc2 = ax.scatter([i + 1], exp[exp.mof == mof].loading_cc_g, color=cm(fngcm[mof]), marker='o')
            kwargs = dict(xytext=(4,0), horizontalalignment="left")
            ax.annotate(str(list(exp[exp.mof == mof].defect_percent)[0]) + "%", (i + 1, exp[exp.mof == mof].loading_cc_g), textcoords='offset points', verticalalignment='center', fontsize=fsl, **kwargs)

    ax.grid(which='major', axis='y', linestyle='-', color='0.9', zorder=1)

    legend = []
    legend.append(Line2D([0], [0], color="black", marker='o', label="exp "))
    legend.append(Line2D([0], [0], color="black", marker='_', label="sim"))
    ax.legend(handles=legend)

    fig.savefig(outputpath, dpi=300, bbox_inches='tight')#, transparent=True)
    plt.close(fig)


if __name__ == '__main__':
    defect_percentages()
