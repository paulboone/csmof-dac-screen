import math
import sys

import click
import numpy as np
import pandas as pd

@click.command()
@click.argument('inputpath', type=click.Path())
@click.option('--metric', '-m', type=str, default="cs_score_1a")
def highest_cs_score_table(inputpath, metric="cs_score_1a"):

    cs = pd.read_csv(inputpath, usecols=["mof_core", "mof_shell", "fails_diffusion_test", metric])
    cs = cs[["mof_core", "mof_shell", "fails_diffusion_test", metric]] # ensure order we want
    cs = cs[cs.mof_shell.str.contains("67")]
    # print(cs[cs.mof_shell == "UIO-67 2x CF$_3$"])
    # any scores that fail the diffusion test are replaced by zero
    cs[metric].mask(cs.fails_diffusion_test, 0, inplace=True)
    cs.fillna(0, inplace=True)


    # improved_score = []
    core_only_score = []
    shell_only_score  = []
    for row in cs.itertuples():
        core_only_score.append(float(cs[(cs.mof_shell == row.mof_core) & (cs.mof_core == row.mof_core)][metric]))
        shell_only_score.append(float(cs[(cs.mof_shell == row.mof_shell) & (cs.mof_core == row.mof_shell)][metric]))
        # print(row.mof_core, row.mof_shell, core_only_score[-1], shell_only_score[-1])

    cs['core_only_score'] = core_only_score
    cs['shell_only_score'] = shell_only_score
    cs['improved_score'] = cs[metric] / cs[["core_only_score", "shell_only_score"]].max(axis=1)
    # cs = cs[(cs[core_only_score] > 0.0) & (cs[shell_only_score] > 0.0) ]
    cs.sort_values(by='improved_score', ascending=False, inplace=True)

    cs.to_csv(sys.stdout)

if __name__ == '__main__':
    highest_cs_score_table()
