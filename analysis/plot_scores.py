import math

import click
import matplotlib.pyplot as plt
from matplotlib.collections import PatchCollection
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1 import make_axes_locatable
import numpy as np
import pandas as pd

from csmofworkflow.calc_selectivities import mof_order

@click.command()
@click.argument('inputpath', type=click.Path())
@click.argument('outputpath', type=click.Path())
@click.option('--metric', '-m', type=str, default="cs_score_2")
def plot_scores(inputpath, outputpath, metric="cs_score_2"):
    score_name = {'cs_score': 'CO2 output stream ppm / 400 ppm',
                  'cs_score_1a': 'fraction CO2 output stream / fraction CO2 output stream UiO-67',
                  'cs_score_2': '[CO2 output stream ppm / 400 ppm - 1] x CO2 adsorbed [mol / cm3]',
                  'cs_score_3': '[CO2 output stream ppm x CO2 adsorbed / [same calc for UiO-67]',
                  'cs_score_4': 'C-S MOF CO2 adsorbed / C-S UiO-67 adsorbed'}

    cs = pd.read_csv(inputpath, usecols=["mof_shell", "mof_core", "fails_diffusion_test", metric])
    cs = cs[cs.mof_shell.str.contains("67")]

    # any scores that fail the diffusion test are replaced by zero
    cs[metric].mask(cs.fails_diffusion_test, 0, inplace=True)

    # drop from plot if all values are zero for mof
    dropm = [m for m in cs.mof_core.unique() if (cs[metric][((cs.mof_shell == m) | (cs.mof_core == m))] <= 0.9).all()]
    cs = cs[(~cs.mof_core.isin(dropm)) & (~cs.mof_shell.isin(dropm))]

    uio67_order = [m for m in mof_order if m in cs.mof_core.unique()]
    grid = cs.pivot(index="mof_shell", columns="mof_core", values=metric)
    grid = grid.reindex(index=uio67_order, columns=uio67_order)

    all_mofnames = grid.columns
    all_mofnames = all_mofnames.str.replace("UIO-67 ", "")
    all_mofnames = all_mofnames.str.replace("UIO-67", "UiO-67")

    fig = plt.figure(figsize=(6.7,5.9), constrained_layout=True)
    ax = fig.subplots()
    grid_np = np.maximum(grid.to_numpy(na_value=0), 0)

    im = ax.imshow(grid_np, origin='lower')

    # ax.set_title(score_name[metric])
    ax.set_xticks(range(0,len(all_mofnames)))
    ax.set_xticklabels(all_mofnames, rotation='vertical', fontsize=9)
    ax.set_yticks(range(0,len(all_mofnames))) #, minor=True
    ax.set_yticklabels(all_mofnames, fontsize=9)
    ax.set_ylabel("Shell MOF", fontsize=10, fontweight="bold")
    ax.set_xlabel("Core MOF", fontsize=10, fontweight="bold")

    label_threshold = np.nanmean(grid_np) + 1.5 * np.nanstd(grid_np)
    label_multiplier = 10**math.ceil(math.log10(1 / label_threshold) + 1)
    print(label_threshold, label_multiplier)
    for (y,x), v in np.ndenumerate(grid_np):
        if (x ==y and v > 0.5) or (v > grid_np[y,y] and v > grid_np[x,x]):
            if v > 1.25 * grid_np[y,y] and v > 1.25 * grid_np[x,x]:
                weight = "bold"
            else:
                weight = "normal"

            if v < 1.0:
                label = "%1.1f" % v
            else:
                label = "%.2g" % v
        # if v > label_threshold or x == y:
            text = ax.text(x, y, label, ha="center", va="center", color="black", fontsize=7.5, fontweight=weight)

    rects = [Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False) for i in range(len(uio67_order))]
    pc = PatchCollection(rects, facecolor="none", edgecolor='#000', lw=1.5)
    ax.add_collection(pc)

    divider = make_axes_locatable(ax)
    colorbar_ax = divider.append_axes("right", size="5%", pad=0.2)
    colorbar_ax.tick_params(labelsize=9)
    cbar = fig.colorbar(im, cax=colorbar_ax)

    fig.savefig(outputpath, dpi=300)

if __name__ == '__main__':
    plot_scores()
