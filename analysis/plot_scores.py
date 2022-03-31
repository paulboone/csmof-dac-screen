import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


score_metric = "cs_score_2"
score_name = {'cs_score': 'fraction CO2 output stream / 400ppm',
              'cs_score_2': '(fraction CO2 output stream / 400ppm) x CO2 adsorbed',}
cs = pd.read_csv("scores-out.csv", usecols=["mof_shell", "mof_core", score_metric])


grid = cs.pivot(index="mof_shell", columns="mof_core", values=score_metric)
print(grid.to_numpy())
print(grid)
all_mofnames = grid.columns

fig = plt.figure(figsize=(8,8), constrained_layout=True)
ax = fig.subplots()
grid_np = grid.to_numpy()
im = ax.imshow(grid_np, origin='lower')
cbar = ax.figure.colorbar(im, ax=ax)

ax.set_title(score_name[score_metric])
ax.set_xticks(range(0,len(all_mofnames)))
ax.set_xticklabels(all_mofnames, rotation='vertical', fontsize=9)
ax.set_yticks(range(0,len(all_mofnames))) #, minor=True
ax.set_yticklabels(all_mofnames, fontsize=9)
ax.set_ylabel("SHELL")
ax.set_xlabel("CORE")

for (y,x), v in np.ndenumerate(grid_np):
    if 1000 * v > 2.:
        text = ax.text(x, y, "%2.1f" % (1000 * v), ha="center", va="center", color="black")

# cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

fig.savefig("size-normalized-%s.png" % score_metric, dpi=144)

