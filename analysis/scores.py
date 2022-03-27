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

def conc(t, x, ads, diff, threshold=0.):
    """returns units of adsorption"""
    if t == 0:
        return -threshold
    return ads - threshold + sum([ads * bn * math.sin(lan * x) * math.exp(-lan**2 * diff * t) for bn, lan in zip(allbn, alllan)])

def find_breakthrough_time(conc_args):
    print('conc_args: ', conc_args)
    co2_bt = root_scalar(conc, conc_args, bracket=(0, 1e20))
    return co2_bt.root

def find_total_adsorption(x_all, t, ads, diff):
    h2o_conc = np.array([conc(t, x, ads, diff) for x in x_all])
    return np.trapz(h2o_conc)

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

shell_size = 0.15 # cm

allbn = calculate_bn_constants(100)
alllan = calculate_lan_constants(shell_size*2, 100)

# convert adsorption units to mole / cm3
mol_cm3_per_m_a3 = (1e8)**3 * 6.022e-23
mofs['a_co2_mole_cm3'] = mol_cm3_per_m_a3 * mofs.a_co2_m_a3
mofs['a_n2_mole_cm3'] = mol_cm3_per_m_a3 * mofs.a_n2_m_a3
mofs['a_h2o_mole_cm3'] = mol_cm3_per_m_a3 * mofs.a_h2o_m_a3
mofs.drop(labels=['a_co2_m_a3', 'a_n2_m_a3', 'a_h2o_m_a3'], axis='columns', inplace=True)

# convert diffusion units to cm2 / s
mofs['d_co2_cm2_s'] =  mofs.d_co2_a2_fs / 10
mofs['d_n2_cm2_s'] = mofs.d_n2_a2_fs / 10
mofs['d_h2o_cm2_s'] =  mofs.d_h2o_a2_fs / 10
mofs.drop(labels=['d_co2_a2_fs', 'd_n2_a2_fs', 'd_h2o_a2_fs'], axis='columns', inplace=True)

# calculate breakthrough times
# define the breakthrough limit to be 1% of the equilibrium loading of co2
mofs['co2_breakthrough_limit'] = mofs['a_co2_mole_cm3'] / 100
mofs['shell_size_cm'] = shell_size
mofs['co2_breakthrough_time_s'] = [find_breakthrough_time(conc_args) for conc_args in
    mofs[['shell_size_cm', 'a_co2_mole_cm3', 'd_co2_cm2_s', 'co2_breakthrough_limit']].itertuples(index=False)]
mofs['h2o_breakthrough_time_s'] = [find_breakthrough_time(conc_args) for conc_args in
    mofs[['shell_size_cm', 'a_h2o_mole_cm3', 'd_h2o_cm2_s', 'co2_breakthrough_limit']].itertuples(index=False)]
mofs['delta_t_s'] = mofs['h2o_breakthrough_time_s'] - mofs['co2_breakthrough_time_s']
mofs['co2_flux_mole_cm2s'] = mofs['a_co2_mole_cm3'] * mofs['d_co2_cm2_s'] / mofs['shell_size_cm']

# calculate water adsorption in shell at breakthrough time
x_all = np.linspace(0., shell_size, 200)
mofs['h2o_breakthrough_adsorption_mol_cm2'] = [find_total_adsorption(x_all, *conc_args) for conc_args in
    mofs[['h2o_breakthrough_time_s', 'a_h2o_mole_cm3', 'd_h2o_cm2_s']].itertuples(index=False)]


shells = mofs
cores = mofs[['mof', 'a_co2_mole_cm3', 'a_n2_mole_cm3']]

cs = shells.join(cores, how="cross", lsuffix="_shell", rsuffix="_core")
cs['core_size_cm'] = cs['co2_flux_mole_cm2s'] * cs['delta_t_s'] / cs['a_co2_mole_cm3_core']
cs['cs_co2_mole_cm2'] = cs['a_co2_mole_cm3_shell'] * cs['shell_size_cm'] + cs['a_co2_mole_cm3_core'] * cs['core_size_cm']
cs['cs_h2o_mole_cm2'] = cs['a_n2_mole_cm3_shell'] * cs['shell_size_cm']
cs['cs_n2_mole_cm2'] = cs['a_n2_mole_cm3_shell'] * cs['shell_size_cm'] + cs['a_n2_mole_cm3_core'] * cs['core_size_cm']
cs['cs_co2_fraction'] = cs['cs_co2_mole_cm2'] / (cs['cs_co2_mole_cm2'] + cs['cs_h2o_mole_cm2'] + cs['cs_n2_mole_cm2'])

cs['shell_membrane_co2_h2o_selectivity'] = cs['a_co2_mole_cm3_shell'] * cs['d_co2_cm2_s'] / (cs['a_h2o_mole_cm3'] * cs['d_h2o_cm2_s'])
cs['core_adsorption_co2_n2_selectivity'] = (cs['a_co2_mole_cm3_core'] / 42.18) / (cs['a_n2_mole_cm3_core'] / 79033.50)
cs['cs_score'] = cs['cs_co2_fraction'] / (400/1000000)
cs['cs_score_2'] = cs['cs_score'] * cs['cs_co2_mole_cm2']

cs.to_csv("scores.csv")


print(cs)
# for i, mof in enumerate(mofs.itertuples()):
#     conc_args = (shell_size, ads_co2, diff_co2, -co2threshold)
#     co2_breakthrough = find_breakthrough_time(conc_args)

#     conc_args = (shell_size, ads_h2o, diff_h2o, -co2threshold)
#     h2o_breakthrough = find_breakthrough_time(conc_args)


#     # times = [format_time(co2_breakthrough), format_time(h2o_breakthrough),
#     #     format_sci(ads_co2), format_sci(ads_h2o), format_sci(diff_co2), format_sci(diff_h2o)]
#     # break_sat_times.append([mof.mof, *times])

# with open('breakthrough-times-analytical.csv', 'w') as csvfile:
#     csvwriter = csv.writer(csvfile)
#     csvwriter.writerow(["mof", "co2_breakthrough_s", "h2o_breakthrough_s", "a_co2_mol_cm3", "a_h2o_mol_cm3", "d_co2_cm2_s", "d_h2o_cm2_s"])
#     for row in break_sat_times:
#         csvwriter.writerow(row)



