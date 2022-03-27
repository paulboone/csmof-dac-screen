from scipy.optimize import root_scalar

import csv
import math

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def format_time(f):
    if f == -1:
        return "-1"
    else:
        return "%.2f" % f

def format_sci(f):
    return "%.2e" % f

def calculate_bn_constants(num_bn=100):
    """returns bn constants, NOT multiplied by initial concentration"""
    return [-4 / (math.pi * (2*n - 1))
        for n in range(1, num_bn + 1)]

def calculate_lan_constants(a, num_lan=100):
    return [math.pi * (2*n - 1) / (2*a) for n in range(1, num_lan + 1)]

def conc(t, x, ads, diff, offset=0.):
    """returns units of adsorption"""
    if t == 0:
        return offset
    return ads + offset + sum([ ads * bn * math.sin(lan * x) * math.exp(-lan**2 * diff * t) for bn, lan in zip(allbn, alllan)])

def find_breakthrough_time(conc_args):
    co2_bt = root_scalar(conc, conc_args, bracket=(0, 1e20))
    return co2_bt.root

def add_plots_for_mof(axes, mof, x_all, t, ads_co2, diff_co2, ads_h2o, diff_h2o, x_csdiv):
    print(axes)
    co2_conc = [conc(t, x, ads_co2, diff_co2) for x in x_all]
    h2o_conc = [conc(t, x, ads_h2o, diff_h2o) for x in x_all]

    axes.set_title(mof, loc="left", pad=20)
    axes.set_title("conc vs x @ t=%ds" % t, loc="right")
    axes.plot(x_all, co2_conc, label="co2 x 10", c='orange')
    # axes.plot(x_all, n2_conc,  label="n2", c='grey')
    axes.plot(x_all, h2o_conc, label="h2o x 10", c='blue')
    axes.set_xlabel("x [cm]")
    axes.set_ylabel("moles / cm3")
    axes.set_xlim(0.)
    axes.set_ylim(0., 0.00025)
    axes.axvline(x_csdiv, ls="--", color="gray", lw=2)
    axes.legend()


mofs = pd.read_csv("data-all-mofs.csv")
mofs_that_need_more_time = mofs[(mofs.d_co2_a2_fs > 0.0) & (mofs.d_h2o_a2_fs == 0.0)]
print("mofs that need more time: ")
print(mofs_that_need_more_time)
mofs = mofs[(mofs.d_co2_a2_fs > 0.0) & (mofs.d_h2o_a2_fs > 0.0) & (mofs.mof.str.contains("UIO-67"))]

csmof_size = 0.3 # cm
nx = 500
dx = csmof_size / nx
x_all = np.linspace(0, csmof_size, nx + 1)

allbn = calculate_bn_constants(100)
alllan = calculate_lan_constants(csmof_size, 100)


mol_cm3_per_m_a3 = (1e8)**3 * 6.022e-23
num_mofs = len(mofs)

graph_rows = math.ceil(num_mofs / 4)
fig = plt.figure(figsize=(4 * 4, 4 * graph_rows), constrained_layout=True)
axes = fig.subplots(graph_rows, 4, squeeze=False)
axes = [a2 for a1 in axes for a2 in a1]

break_sat_times = []
for i, mof in enumerate(mofs.itertuples()):
    if i >= num_mofs:
        break
    print(mof.mof)

    ads_co2 = mol_cm3_per_m_a3 * float(mof.a_co2_m_a3) # convert units to mol / cm3
    diff_co2 = float(mof.d_co2_a2_fs) / 10 # convert units from a2 / fs -> cm2 / s


    co2threshold = -ads_co2 / 100 # we define the "breakthrough" threshold to be 0.01 * the equilibrium adsorption of CO2
    conc_args = (csmof_size / 2, ads_co2, diff_co2, co2threshold)
    co2_breakthrough = find_breakthrough_time(conc_args)

    ads_h2o = mol_cm3_per_m_a3 * float(mof.a_h2o_m_a3) # convert units to mol / cm3
    diff_h2o = float(mof.d_h2o_a2_fs) / 10 # convert units from a2 / fs -> cm2 / s
    conc_args = (csmof_size / 2, ads_h2o, diff_h2o, co2threshold)
    h2o_breakthrough = find_breakthrough_time(conc_args)

    add_plots_for_mof(axes[i], mof.mof, x_all, h2o_breakthrough, ads_co2, diff_co2, ads_h2o, diff_h2o, x_csdiv=nx*dx/2)

    times = [format_time(co2_breakthrough), format_time(h2o_breakthrough),
        format_sci(ads_co2), format_sci(ads_h2o), format_sci(diff_co2), format_sci(diff_h2o)]
    break_sat_times.append([mof.mof, *times])

with open('breakthrough-times-analytical.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["mof", "co2_breakthrough_s", "h2o_breakthrough_s", "a_co2_mol_cm3", "a_h2o_mol_cm3", "d_co2_cm2_s", "d_h2o_cm2_s"])
    for row in break_sat_times:
        csvwriter.writerow(row)


fig.savefig("test-analytical.png", dpi=144)
# fig.savefig("test1.png", dpi=144)

# # axes.set_title(mof, loc="left", pad=20)
# # axes.set_title("conc vs x @ t=%d" % steps, loc="right")
# axes.plot(x_all, co2_conc, label="co2 x 10", c='orange')
# axes.plot(x_all, n2_conc, label="n2", c='grey')
# axes.plot(x_all, h2o_conc, label="h2o x 10", c='blue')
# axes.set_xlabel("x [cm]")
# axes.set_ylabel("concentration [mol / cm3]")
# axes.set_xlim(0.)
# axes.set_ylim(0.)
# # axes.axvline(x_csdiv, ls="--", color="gray", lw=2)
# # axes.legend()

# fig.savefig("test-analytical.png", dpi=144)
