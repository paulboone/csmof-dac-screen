
import click
import matplotlib.pyplot as plt
from matplotlib import rc
from matplotlib.lines import Line2D
import numpy as np
import pandas as pd

rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

fsl = fs = 9

@click.command()
@click.argument('betsas', type=click.File())
@click.argument('raspasas', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="surface-area-comparison.png")
def surface_area_comparison(betsas, raspasas, outputpath="surface-area-comparison.png"):
    bet_df = pd.read_csv(betsas, skipinitialspace=True)
    rsa_df = pd.read_csv(raspasas, skipinitialspace=True)
    rsa_df = rsa_df[rsa_df.mof.isin(bet_df.mof)]
    rsa_df['sim'] = "raspa"
    rsa_df.rename(columns={'surfacearea': 'area'}, inplace=True)
    all_df = bet_df.append(rsa_df)
    all_df = all_df.pivot(index="mof", columns="sim", values=["area"])
    all_df.columns = ["_".join(a) for a in all_df.columns.to_flat_index()]
    all_df.reset_index(inplace=True)

    cm = plt.cm.get_cmap("tab20")
    fngcm = {
        'uio67':14, 'uio66':15,
        'uio67-NH2-2':2, 'uio67-NH2': 3,
        'uio67-CH3-2':4, 'uio67-CH3': 5,
    }
    all_df["color"] = [cm(fngcm[m]) for m in all_df.mof]

    fig = plt.figure(figsize=(6, 6))
    ax = fig.subplots()
    ax.set_xlim(0, 3500)
    ax.set_ylim(0, 3500)
    ax.set_xlabel("Experimental Surface Area: BET")
    ax.set_ylabel("Simulated Surface Area: BET or Raspa")
    sc1 = ax.scatter(all_df.area_exp, all_df.area_sim, c=all_df.color, marker='o', label="BET", zorder=10)
    sc1 = ax.scatter(all_df.area_exp, all_df.area_raspa, c=all_df.color, marker='s', label="raspa", zorder=10)
    ax.plot([0,3500], [0,3500])

    ax.grid(which='major', axis='both', linestyle='-', color='0.9', zorder=1)

    legend = []
    for mof, color in zip(all_df.mof, all_df.color):
        legend.append(Line2D([0], [0], color=color, marker='o', label="%s BET " % mof))
        legend.append(Line2D([0], [0], color=color, marker='s', label="%s raspa " % mof))

    ax.legend(handles=legend)

    fig.savefig(outputpath, dpi=300, bbox_inches='tight')#, transparent=True)
    plt.close(fig)


if __name__ == '__main__':
    surface_area_comparison()
