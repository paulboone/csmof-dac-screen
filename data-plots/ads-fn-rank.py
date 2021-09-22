
import click
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas as pd

rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

fsl = fs = 9

@click.command()
@click.argument('csv-path', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="ads-fn-rank.png")
def ads_fnrank(csv_path, outputpath="ads-fn-rank.png"):
    fig = plt.figure(figsize=(6, 6))

    data = pd.read_csv(csv_path)
    data["log_CO2_H2O"] = np.log10(data["co2/h2o selectivity"])
    data["log_CO2_N2"] = np.log10(data["co2/n2 selectivity"])
    data["log_combined_selectivity"] = data["log_CO2_H2O"] + data["log_CO2_N2"]
    data["moflabels"] = list(data.mof.str.replace("UIO-6[67] ", ""))
    uio66 = data[data.mof.str.startswith("UIO-66")].copy()
    uio66["mof"] = list(uio66.mof.str.replace("UIO-6[67] ", ""))
    uio67 = data[data.mof.str.startswith("UIO-67")].copy()
    uio67["mof"] = list(uio67.mof.str.replace("UIO-6[67] ", ""))

    ranked = uio66[["mof", "log_combined_selectivity"]].copy()
    ranked.rename(columns={'log_combined_selectivity':'uio66'}, inplace=True)
    ranked["uio66"].fillna(-5, inplace=True)
    ranked["uio67"] = list(uio67["log_combined_selectivity"])
    ranked["mof2"] = list(uio67["mof"])
    ranked["mof"] == ranked["mof2"]
    ranked = ranked.sort_values("uio66")
    ranked["uio66_rank"] = np.arange(len(ranked))
    ranked = ranked.sort_values("uio67")
    ranked["uio67_rank"] = np.arange(len(ranked))
    ranked = ranked.sort_values("uio66")

    ax = fig.subplots(ncols=1)
    ax.set_xticks(np.arange(len(ranked)))
    ax.set_xticklabels(ranked["mof"], rotation='vertical', fontsize=fs)

    sc1 = ax.scatter(ranked.uio66_rank, ranked.uio67_rank)

    fig.savefig(outputpath, dpi=300, bbox_inches='tight')#, transparent=True)
    plt.close(fig)


if __name__ == '__main__':
    ads_fnrank()
