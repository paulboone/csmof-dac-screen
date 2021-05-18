
import click
import matplotlib.pyplot as plt
from matplotlib import rc
import numpy as np
import pandas as pd


rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# rc('text', usetex=True)

fsl = fs = 8

@click.command()
@click.argument('csv-path', type=click.File())
@click.option('--outputpath', '-o', type=click.Path(), default="loadings.png")
def ads_selectivity(csv_path, outputpath="loadings.png"):

    fig = plt.figure(figsize=(8,8))

    # cm = matplotlib.cm.get_cmap("viridis")
    data = pd.read_csv(csv_path)

    uio66 = data[data.mof.str.startswith("uio66")]
    uio67 = data[data.mof.str.startswith("uio67")]
    labels = uio66.mof.str.slice(6)

    ax = fig.subplots(ncols=1)

    # ax.set_xscale('log')
    # ax.set_yscale('log')

    # ax.set_xlim(1, 2.75)
    # ax.set_ylim(0.75, 2.75)
    #
    sc1 = ax.plot(np.log10(uio66.CO2), color="orange", zorder=2, markersize=3, marker="v", label="uio-66 CO2", linestyle='None')
    sc1 = ax.plot(np.log10(uio67.CO2), color="orange", zorder=2, markersize=5, marker=r'$\bowtie$', label="uio-67 CO2", linestyle='None')

    sc1 = ax.plot(np.log10(uio66.N2), color="grey", zorder=2, markersize=3, marker="v", label="uio-66 N2", linestyle='None')
    sc1 = ax.plot(np.log10(uio67.N2), color="grey", zorder=2, markersize=5, marker= r'$\bowtie$', label="uio-67 N2", linestyle='None')

    sc1 = ax.plot(np.log10(uio66.H2O), color="blue", zorder=2, markersize=3, marker="v", label="uio-66 H2O", linestyle='None')
    sc1 = ax.plot(np.log10(uio67.H2O), color="blue", zorder=2, markersize=5, marker= r'$\bowtie$', label="uio-67 H2O", linestyle='None')

    ax.set_xticks(range(0,len(data.mof)))
    ax.set_xticklabels(data.mof, rotation='vertical', fontsize=7)
    ax.set_xlabel('MOF', fontsize=fsl)
    ax.set_ylabel('log10 adsorption [mol gas / kg framework] @ stp', fontsize=fsl)


    # # loadings where uio66/67 on same x to compare functional groups
    # sc1 = ax.plot(range(0,len(labels)), np.log10(uio66.CO2), color="orange", zorder=2, markersize=3, marker="v", label="uio-66 CO2", linestyle='None')
    # sc1 = ax.plot(range(0,len(labels)), np.log10(uio67.CO2), color="orange", zorder=2, markersize=5, marker=r'$\bowtie$', label="uio-67 CO2", linestyle='None')
    #
    # sc1 = ax.plot(range(0,len(labels)), np.log10(uio66.N2), color="grey", zorder=2, markersize=3, marker="v", label="uio-66 N2", linestyle='None')
    # sc1 = ax.plot(range(0,len(labels)), np.log10(uio67.N2), color="grey", zorder=2, markersize=5, marker= r'$\bowtie$', label="uio-67 N2", linestyle='None')
    #
    # sc1 = ax.plot(range(0,len(labels)), np.log10(uio66.H2O), color="blue", zorder=2, markersize=3, marker="v", label="uio-66 H2O", linestyle='None')
    # sc1 = ax.plot(range(0,len(labels)), np.log10(uio67.H2O), color="blue", zorder=2, markersize=5, marker= r'$\bowtie$', label="uio-67 H2O", linestyle='None')
    #
    # ax.set_xticks(range(0,len(labels)))
    # ax.set_xticklabels(labels, rotation='vertical', fontsize=7)
    #
    # ax.set_xlabel('functional group', fontsize=fsl)
    # ax.set_ylabel('log10 adsorption [mol gas / kg framework] @ stp', fontsize=fsl)



#
# sc1 = ax.plot(range(0, len(uio66.mof)), np.log10(uio66.CO2), color="orange", zorder=2, marker="D", label="uio-66 CO2", linestyle='None')
# sc1 = ax.plot(range(0, len(uio66.mof)), np.log10(uio67.CO2), color="orange", zorder=2, marker=r'$\bowtie$', label="uio-67 CO2", linestyle='None')
#
# sc1 = ax.plot(range(0, len(uio66.mof)), np.log10(uio66.N2), color="grey", zorder=2, marker="D", label="uio-66 N2", linestyle='None')
# sc1 = ax.plot(range(0, len(uio66.mof)), np.log10(uio67.N2), color="grey", zorder=2, marker= r'$\bowtie$', label="uio-67 N2", linestyle='None')
#
# sc1 = ax.plot(range(0, len(uio66.mof)), np.log10(uio66.H2O), color="blue", zorder=2, marker="D", label="uio-66 H2O", linestyle='None')
# sc1 = ax.plot(range(0, len(uio66.mof)), np.log10(uio67.H2O), color="blue", zorder=2, marker= r'$\bowtie$', label="uio-67 H2O", linestyle='None')


    # ax.set_yticks(prop2range[1] * np.array(range(0,num_bins + 1))/num_bins, minor=True)
    # sc2 = ax.scatter(uio67["log_CO2_H2O"], uio67["log_CO2_N2"], s=uio67.sizes, zorder=2, marker="s", label="uio-67")

    # # ax.set_xticks(prop1range[1] * np.array([0.0, 0.25, 0.5, 0.75, 1.0]))
    # ax.set_yticks(prop2range[1] * np.array([0.0, 0.25, 0.5, 0.75, 1.0]))
    # ax.set_xticks(prop1range[1] * np.array(range(0,num_bins + 1))/num_bins, minor=True)

    #
    # ax.tick_params(axis='x', which='major', labelsize=fs)
    # ax.tick_params(axis='y', which='major', labelsize=fs)
    #
    ax.grid(which='major', axis='both', linestyle='-', color='0.9', zorder=0)
    ax.grid(which='minor', axis='x', linestyle='-', color='0.9', zorder=0)


    # for i, (_, label) in enumerate(labels):
    #     print(label, (data["CO2/H2O"][i], data["CO2/N2"][i]))
    #     ax.annotate(label, (data["CO2/H2O"][i], data["CO2/N2"][i]), size=6)


    # for i, mof in enumerate(data.mof):
    #     print(mof, (data["log_CO2_H2O"][i], data["log_CO2_N2"][i]))
    #     # if data["log_CO2_H2O"][i] > 1 and data["log_CO2_N2"][i] > 0.5:
    #     x, y = (data["log_CO2_H2O"][i], data["log_CO2_N2"][i])

        # # desorption
        # # if not ((0.5 < x < 2) and (0.8 < y < 2.)):
        # ax.annotate(mof, (x, y), size=5, xytext=(x+0.02,y-0.02))

        # # adsorption
        # if not ((0.5 < x < 2) and (0.8 < y < 2.)):
        #     ax.annotate(mof, (x, y), size=5, xytext=(x+0.03,y-0.03))

        # # adsorption zoom
        # if (1 < x < 2.75) and (0.75 < y < 2.75):
        #     ax.annotate(mof, (x, y), size=5, xytext=(x+0.01,y-0.01))


    ax.legend()
    # fig.subplots_adjust(wspace=0.05, hspace=0.05)
    fig.savefig(outputpath, dpi=300, bbox_inches='tight')
    plt.close(fig)

if __name__ == '__main__':
    ads_selectivity()
