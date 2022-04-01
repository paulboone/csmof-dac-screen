import math

import click
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

@click.command()
@click.argument('inputpath', type=click.Path())
@click.argument('outputpath', type=click.Path())
@click.option('--metric', '-m', type=str, default="cs_score_2")
def plot_scores(inputpath, outputpath, metric="cs_score_2"):
    score_name = {'cs_score': 'CO2 output stream ppm / 400 ppm',
                  'cs_score_2': '[CO2 output stream ppm / 400 ppm - 1] x CO2 adsorbed [mol / cm3]',
                  'cs_score_3': '[CO2 output stream ppm / 400 ppm - 1] x CO2 adsorbed / [same calc for UIO-67]',
                  'cs_score_4': 'score 4'}

    cs = pd.read_csv(inputpath, usecols=["mof_shell", "mof_core", metric])
    grid = cs.pivot(index="mof_shell", columns="mof_core", values=metric)
    all_mofnames = grid.columns

    fig = plt.figure(figsize=(8,8), constrained_layout=True)
    ax = fig.subplots()
    grid_np = grid.to_numpy()
    im = ax.imshow(grid_np, origin='lower')
    cbar = ax.figure.colorbar(im, ax=ax)

    ax.set_title(score_name[metric])
    ax.set_xticks(range(0,len(all_mofnames)))
    ax.set_xticklabels(all_mofnames, rotation='vertical', fontsize=9)
    ax.set_yticks(range(0,len(all_mofnames))) #, minor=True
    ax.set_yticklabels(all_mofnames, fontsize=9)
    ax.set_ylabel("SHELL")
    ax.set_xlabel("CORE")

    # label_threshold =
    # print(np.flip(np.argsort(grid_np, axis=None)))
    # print(np.ravel(grid_np).shape)
    # print(np.ravel(grid_np)[34])
    label_threshold = np.nanmean(grid_np) + 2 * np.nanstd(grid_np)
    label_multiplier = 10**math.ceil(math.log10(1 / label_threshold) + 1)
    print(label_threshold, label_multiplier)
    for (y,x), v in np.ndenumerate(grid_np):
        if v > label_threshold:
            text = ax.text(x, y, "%2d" % (label_multiplier * v), ha="center", va="center", color="black")

    fig.savefig(outputpath, dpi=144)

if __name__ == '__main__':
    plot_scores()
