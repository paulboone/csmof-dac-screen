
import click
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas as pd

rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})

fsl = fs = 9

@click.command()
@click.argument('csv-path', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="ads-selectivity.png")
@click.option('--plotnum', '-n', type=int, default=0)
def ads_selectivity(csv_path, outputpath="ads-selectivity.png", plotnum=0):
    fig = plt.figure(figsize=(6, 6))

    data = pd.read_csv(csv_path) # index_col=["mof"]
    data["log_CO2_H2O"] = np.log10(data["co2/h2o selectivity"])
    data["log_CO2_N2"] = np.log10(data["co2/n2 selectivity"])
    data["moflabels"] = list(data.mof.str.replace("UIO-6[67] ", ""))
    uio66 = data[data.mof.str.startswith("UIO-66")]
    uio67 = data[data.mof.str.startswith("UIO-67")]


    ax = fig.subplots(ncols=1)
    ax.grid(which='major', axis='both', linestyle='-', color='0.9', zorder=10)
    ax.set_xlabel('log$_{10}$ CO$_2$/H$_2$O adsorption selectivity', fontsize=fsl)
    ax.set_ylabel('log$_{10}$ CO$_2$/N$_2$ adsorption selectivity', fontsize=fsl)

    def anno(idx, alignment='left', xytextoffset=(0,0), fontsize=7):
        x, y = (data.log_CO2_H2O[idx], data.log_CO2_N2[idx])
        if alignment=='left':
            xytext = (4, -0.5)
        else:
            xytext = (-4, -0.5)
        ax.annotate(data.moflabels[idx] + " - %3.2f" % (float(data.loading_co2[idx])), (x, y), size=5,
            xytext=(xytext[0] + xytextoffset[0], xytext[1] + xytextoffset[1]), textcoords='offset points', horizontalalignment=alignment, verticalalignment='center', fontsize=fontsize)

    if plotnum == 0:
        sc1 = ax.scatter(uio66.log_CO2_H2O, uio66.log_CO2_N2, zorder=2, s=10, marker=">", label="UIO-66", c="sienna")
        sc2 = ax.scatter(uio67.log_CO2_H2O, uio67.log_CO2_N2, zorder=2, s=20, marker= r'$\bowtie$', label="UIO-67", c="mediumseagreen")
        ax.set_xlim(-3, 3)
        ax.set_xticks([-2., -1, 0., 1, 2])
        ax.set_ylim(-1, 3)
        ax.set_yticks([0., 1., 2.])

    elif plotnum == 1:
        sc1 = ax.scatter(uio66.log_CO2_H2O, uio66.log_CO2_N2, zorder=2, s=10, marker=">", label="UIO-66", c="sienna")
        sc2 = ax.scatter(uio67.log_CO2_H2O, uio67.log_CO2_N2, zorder=2, s=20, marker= r'$\bowtie$', label="UIO-67", c="mediumseagreen")
        ax.set_xlim(0.5, 3.)
        ax.set_xticks([1., 2.])
        ax.set_ylim(0.5, 3.)
        ax.set_yticks([1., 2.])

        subplot=2
        for idx in data.index:
            mof = data.mof[idx]
            x, y = (data.log_CO2_H2O[idx], data.log_CO2_N2[idx])
            if subplot==0:
                if mof in ["UIO-66 branched-HNC$_5$", "UIO-66 2x ring-HNC$_5$"]:
                    anno(idx, 'left')
                elif mof in ["UIO-66 2x NC$_4$", "UIO-66 2x alkane-OC$_4$"]:
                    anno(idx, 'right')
            elif subplot==1:
                if (0.5 < x < 3.) and (0.5 < y < 3.):
                    anno(idx, "left", fontsize=5)
            elif subplot==2:
                if mof in ["UIO-67 2x NC$_4$", "UIO-67 branched-HNC$_5$"]:
                    anno(idx, 'right')
                elif mof in [ "UIO-66", "UIO-67",
                            "UIO-66 2x NC$_4$",
                            "UIO-66 branched-HNC$_5$",
                            "UIO-66 2x N$_3$", "UIO-67 2x N$_3$",
                            "UIO-66 2x NH$_2$", "UIO-67 2x NH$_2$"]:
                    anno(idx, "left")
    elif plotnum == 2:
        sc2 = ax.scatter(uio67.log_CO2_H2O, uio67.log_CO2_N2, zorder=2, s=20, marker= r'$\bowtie$', label="UIO-67", c="mediumseagreen")
        ax.set_xlim(0.75, 1.6)
        ax.set_xticks([1., 1.5,])
        ax.set_ylim(0.75, 1.6)
        ax.set_yticks([1., 1.5])
        uio67_inplot = uio67[uio67.log_CO2_H2O.between(0.75, 1.6) & uio67.log_CO2_N2.between(0.75, 1.6)]

        for idx in uio67_inplot.index:
            mof = uio67_inplot.mof[idx]
            if mof == 'UIO-67 alkane-HNC$_3$':
                anno(idx, "left", (0,-2))
            elif mof == 'UIO-67 alkane-OC$_4$':
                anno(idx, "right", (0,-3))
            elif mof == 'UIO-67 NH$_2$':
                anno(idx, "left", (0,-1))
            elif mof == 'UIO-67 OH':
                anno(idx, "center", (4,6))
            elif mof in ['UIO-67 2x alkane-HNC$_3$', 'UIO-67 alkane-HNC$_5$', 'UIO-67 ring-HNC$_5$', 'UIO-67 N$_3$', 'UIO-67 alkane-HNC$_4$']:
                anno(idx)
            else:
                anno(idx, "right")

    ax.legend()
    fig.savefig(outputpath, dpi=300, bbox_inches='tight', transparent=True)
    plt.close(fig)


if __name__ == '__main__':
    ads_selectivity()
