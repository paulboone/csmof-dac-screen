
import click
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas as pd


fsl = fs = 8
rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
rc('font', size=fs)

# a_h2o_m_a3 a_co2_m_a3  a_n2_m_a3   msd_a2_co2  msd_a2_n2   msd_a2_tip4p    d_co2_a2_fs d_n2_a2_fs  d_h2o_a2_fs




@click.command()
@click.argument('csv-path', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="perm-ads-selectivity.png")
# @click.option('--plotnum', '-n', type=int, default=1)
def perm_ads_selectivity(csv_path, outputpath="perm-ads-selectivity.png", plotnum=0):

    def anno(idx, x, y, alignment='left', xytextoffset=(0,0), fontsize=fsl):
        if alignment=='left':
            xytext = (4, -0.0)
        else:
            xytext = (-3, -0.0)
        ax.annotate(data.mof[idx], (x, y), size=5,
            xytext=(xytext[0] + xytextoffset[0], xytext[1] + xytextoffset[1]), textcoords='offset points', horizontalalignment=alignment, verticalalignment='center')

    n2_pa = 79033.50
    h2o_pa = 2050
    co2_pa = 42.18

    data = pd.read_csv(csv_path)
    data["log_diff_selectivity"] = np.log10(data.d_co2_a2_fs / data.d_h2o_a2_fs)
    data["log_perm_selectivity"] = np.log10((data.d_co2_a2_fs * data.a_co2_m_a3) / (data.d_h2o_a2_fs * data.a_h2o_m_a3))
    data["log_ads_selectivity"] = np.log10((n2_pa * data.a_co2_m_a3) / (co2_pa * data.a_n2_m_a3))
    data = data[data.mof.str.startswith("UIO-67")]
    data['mof'] = list(data.mof.str.replace("UIO-6[67] ", ""))
    data = data[data.d_co2_a2_fs > 2e-5]

    fig = plt.figure(figsize=(3.3, 3.3), constrained_layout=True)
    ax = fig.subplots(ncols=1)
    # sc2 = ax.scatter(data.log_ads_selectivity, data.log_diff_selectivity, zorder=2, s=20, marker= r'$\bowtie$', label="UIO-67")
    sc2 = ax.scatter(data.log_ads_selectivity, data.log_perm_selectivity, zorder=2, s=20, marker= r'$\bowtie$', label="UIO-67")
    ax.grid(which='major', axis='both', linestyle='-', color='0.9', zorder=10)
    ax.set_xlabel('log$_{10}$ CO$_2$/N$_2$ adsorption selectivity')
    # ax.set_ylabel('log$_{10}$ CO$_2$/H$_2$O diff-selectivity')
    ax.set_ylabel('log$_{10}$ CO$_2$/H$_2$O perm-selectivity')

    # ax.set_xlim(2.4, 3.3)
    # ax.set_ylim(-0.2, 1.6)
    # ax.set_yticks([-1., 0.])
    # ax.set_xticks([0., 1., 2., 3.])

    for idx in data.index:
        mof = data.mof[idx]
        # x, y = (data.log_ads_selectivity[idx], data.log_diff_selectivity[idx])
        x, y = (data.log_ads_selectivity[idx], data.log_perm_selectivity[idx])
        if mof == "UIO-67":
            anno(idx, x, y, 'left', xytextoffset=(-1,-3.5))
        elif mof == "2x OH":
            anno(idx, x, y, 'right', xytextoffset=(6,4.2))
        elif mof == "ring-HNC$_5$":
            anno(idx, x, y, 'left', xytextoffset=(-2,-4))
        elif mof == "2x alkane-OC$_4$":
            anno(idx, x, y, 'right', xytextoffset=(1,-3))
        elif mof == "alkane-OC$_4$":
            anno(idx, x, y, 'right', xytextoffset=(0.5,2.5))
        elif mof in ["OH",  "CH$_3$", "NH$_2$", "2x NH$_2$", "alkane-HNC$_5$", "branched-HNC$_5$",
            "alkane-OC$_5$", "UIO-67", "alkane-HNC$_3$"]:
            anno(idx, x, y, 'left')
        else: # "alkane-HNC$_4$", "alkane-OC$_3$"
            anno(idx, x,y, 'right')


    # ax.legend()
    # fig.subplots_adjust(wspace=0.05, hspace=0.05)
    fig.savefig(outputpath, dpi=300, bbox_inches='tight') # , transparent=True
    plt.close(fig)

if __name__ == '__main__':
    perm_ads_selectivity()
