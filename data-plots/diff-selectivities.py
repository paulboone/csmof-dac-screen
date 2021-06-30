
import click
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas as pd


rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# rc('text', usetex=True)

fsl = fs = 9

@click.command()
@click.argument('csv-path', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="diff-selectivity.png")
@click.option('--plotnum', '-n', type=int, default=1)
def d_selectivity(csv_path, outputpath="diff-selectivity.png", plotnum=0):
    fig = plt.figure(figsize=(6, 6))

    data = pd.read_csv(csv_path)
    data["log_CO2_H2O"] = np.log10(data["CO2 / H2O"])
    data["log_CO2_N2"] = np.log10(data["CO2 / N2"])
    uio66 = data[data.mof.str.startswith("UIO-66")]
    uio67 = data[data.mof.str.startswith("UIO-67")]
    moflabels = list(data.mof.str.replace("UIO-6[67] ", ""))

    ax = fig.subplots(ncols=1)
    sc1 = ax.scatter(uio66.log_CO2_H2O, uio66.log_CO2_N2, zorder=2, s=10, marker=">", label="UIO-66", c="sienna")
    sc2 = ax.scatter(uio67.log_CO2_H2O, uio67.log_CO2_N2, zorder=2, s=20, marker= r'$\bowtie$', label="UIO-67", c="mediumseagreen")
    ax.grid(which='major', axis='both', linestyle='-', color='0.9', zorder=10)
    ax.set_xlabel('log$_{10}$ CO$_2$/H$_2$O diffusion selectivity', fontsize=fsl)
    ax.set_ylabel('log$_{10}$ CO$_2$/N$_2$ diffusion selectivity', fontsize=fsl)

    if plotnum == 0:
        ax.set_xlim(-0.8, 3.3)
        ax.set_ylim(-1.6, .1)
        ax.set_yticks([-1., 0.])
        ax.set_xticks([0., 1., 2., 3.])
        for i, mof in enumerate(data.mof):
            x, y = (data.log_CO2_H2O[i], data.log_CO2_N2[i])
            if mof in ["UIO-67", "UIO-66"]:
                ax.annotate(moflabels[i], (x, y), size=5, xytext=(x-0.045,y - 0.002), horizontalalignment='right', verticalalignment='center', fontsize=fs)

    elif plotnum == 1:
        ax.set_xlim(1.1, 3.3)
        ax.set_ylim(-0.6, .1)
        ax.set_yticks([-0.5, 0.])
        ax.set_xticks([1.5, 2., 2.5, 3.])
        for i, mof in enumerate(data.mof):
            x, y = (data.log_CO2_H2O[i], data.log_CO2_N2[i])
            if (1.1 < x < 3.3) and (-0.6 < y < 0.1):
                if mof in ["UIO-67", "UIO-67 2x alkane-OC$_4$", "UIO-67 branched-HNC$_5$", "UIO-67 alkane-HNC$_4$"]:
                    ax.annotate(moflabels[i] + " - %3.1f" % (float(data.CO2[i]) * 1e4), (x, y), size=5, xytext=(x-0.03,y - 0.), horizontalalignment='right', verticalalignment='center', fontsize=7)
                else:
                    ax.annotate(moflabels[i] + " - %3.1f" % (float(data.CO2[i]) * 1e4), (x, y), size=5, xytext=(x+0.03,y - 0.), horizontalalignment='left', verticalalignment='center', fontsize=7)

    ax.legend()
    # fig.subplots_adjust(wspace=0.05, hspace=0.05)
    fig.savefig(outputpath, dpi=300, bbox_inches='tight', transparent=True)
    plt.close(fig)

if __name__ == '__main__':
    d_selectivity()
