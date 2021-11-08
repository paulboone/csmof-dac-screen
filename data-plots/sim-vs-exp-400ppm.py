
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
@click.argument('simulated_csv', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="sim-vs-exp.png")
def sim_vs_exp(experimental_csv, simulated_csv, outputpath="sim-vs-exp.png"):
    exp = pd.read_csv(experimental_csv, skipinitialspace=True, comment="#", usecols=["mof", "gas", "pressure_bar", "loading_cc_g"])
    sim = pd.read_csv(simulated_csv, skipinitialspace=True, comment="#", usecols=["mof", "gas", "pressure_bar", "loading_cc_g"])
    df = pd.merge(exp, sim, how="outer", on=["mof", "gas", "pressure_bar"], suffixes=["_exp", "_sim"])
    df.sort_values("loading_cc_g_sim", inplace=True)
    df.mof = df.mof.str.replace("uio67-", "")
    df.mof = df.mof.str.replace("HNC6-ring-", "CyNH")
    print(df)

    cm = plt.cm.get_cmap("tab20")
    fngcm = {
        'uio67':14, 'uio66':15,
        'NH2-2':2, 'NH2': 3,
        'CH3-2':4, 'CH3': 5,
        'CyNH-2':16, 'CyNH': 17,
    }

    fig = plt.figure(figsize=(6, 6))
    ax = fig.subplots()
    mof_nums = list(range(1, len(df) + 1))
    ax.set_xlim(0, len(df) + 1)
    ax.set_xticklabels([""] + list(df.mof) + [""], fontsize=fs, minor=False)
    ax.set_xlabel("Functional Group")
    ax.set_ylabel("Loading CC/g")
    ax.scatter(mof_nums, df.loading_cc_g_exp, marker='o', zorder=10, label="Experimental")
    ax.scatter(mof_nums, df.loading_cc_g_sim, marker='x', zorder=10, label="Simulated")
    ax.legend()

    fig.savefig(outputpath, dpi=300, bbox_inches='tight')#, transparent=True)
    plt.close(fig)

if __name__ == '__main__':
    sim_vs_exp()
