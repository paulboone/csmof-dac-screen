import pandas as pd
import matplotlib.pyplot as plt

score_metric = "cs_score_2"
score_name = {'cs_score': 'fraction CO2 output stream / 400ppm',
              'cs_score_2': '(fraction CO2 output stream / 400ppm) x CO2 adsorbed',}
cs = pd.read_csv("scores.csv", usecols=["mof_shell", "mof_core", score_metric])


grid = cs.pivot(index="mof_shell", columns="mof_core", values=score_metric)
print(grid.to_numpy())
print(grid)
all_mofnames = grid.columns

fig = plt.figure(figsize=(8,8), constrained_layout=True)
ax = fig.subplots()
im = ax.imshow(grid.to_numpy(), origin='lower')
cbar = ax.figure.colorbar(im, ax=ax)

ax.set_title(score_name[score_metric])
ax.set_xticks(range(0,len(all_mofnames)))
ax.set_xticklabels(all_mofnames, rotation='vertical', fontsize=9)
ax.set_yticks(range(0,len(all_mofnames))) #, minor=True
ax.set_yticklabels(all_mofnames, fontsize=9)
ax.set_ylabel("SHELL")
ax.set_xlabel("CORE")
# cbar.ax.set_ylabel(cbarlabel, rotation=-90, va="bottom")

fig.savefig("%s.png" % score_metric, dpi=144)

