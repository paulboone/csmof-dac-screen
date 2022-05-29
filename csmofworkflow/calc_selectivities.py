
import csv
from pathlib import Path
import sys

import click

import numpy as np
import pandas as pd


mof_name_mapping = {
    "UIO-66":                 "UIO-66",
    "UIO-66-CF3-2":           'UIO-66 2x CF$_3$',
    "UIO-66-F":               'UIO-66 4x F',
    "UIO-66-HNC3-alkane":     'UIO-66 alkane-HNC$_3$',
    "UIO-66-HNC3-alkane-2":   'UIO-66 2x alkane-HNC$_3$',
    "UIO-66-HNC4-alkane":     'UIO-66 alkane-HNC$_4$',
    "UIO-66-HNC4-alkane-2":   'UIO-66 2x alkane-HNC$_4$',
    "UIO-66-HNC5-alkane":     'UIO-66 alkane-HNC$_5$',
    "UIO-66-HNC5-alkane-2":   'UIO-66 2x alkane-HNC$_5$',
    "UIO-66-HNC5-branched":   'UIO-66 branched-HNC$_5$',
    "UIO-66-HNC5-branched-2": 'UIO-66 2x branched-HNC$_5$',
    "UIO-66-HNC5-ring":       'UIO-66 ring-HNC$_5$',
    "UIO-66-HNC5-ring-2":     'UIO-66 2x ring-HNC$_5$',
    "UIO-66-HNC6-ring":       'UIO-66 ring-HNC$_6$',
    "UIO-66-HNC6-ring-2":     'UIO-66 2x ring-HNC$_6$',
    "UIO-66-N3":              'UIO-66 N$_3$',
    "UIO-66-N3-2":            'UIO-66 2x N$_3$',
    "UIO-66-NC4-2":           'UIO-66 2x NC$_4$',
    "UIO-66-NH2":             'UIO-66 NH$_2$',
    "UIO-66-NH2-2":           'UIO-66 2x NH$_2$',
    "UIO-66-NH2-10x":         'UIO-66 NH$_2$ 10x',
    "UIO-66-NH2-2-10x":       'UIO-66 2x NH$_2$ 10x',
    "UIO-66-OC3-alkane":      'UIO-66 alkane-OC$_3$',
    "UIO-66-OC3-alkane-2":    'UIO-66 2x alkane-OC$_3$',
    "UIO-66-OC4-alkane":      'UIO-66 alkane-OC$_4$',
    "UIO-66-OC4-alkane-2":    'UIO-66 2x alkane-OC$_4$',
    "UIO-66-OC5-alkane":      'UIO-66 alkane-OC$_5$',
    "UIO-66-OC5-alkane-2":    'UIO-66 2x alkane-OC$_5$',
    "UIO-66-OH":              'UIO-66 OH',
    "UIO-66-OH-2":            'UIO-66 2x OH',
    "UIO-67":                 'UIO-67',
    "UIO-67-CF3-2":           'UIO-67 2x CF$_3$',
    "UIO-67-F":               'UIO-67 8x F',
    "UIO-67-HNC3-alkane":     'UIO-67 alkane-HNC$_3$',
    "UIO-67-HNC3-alkane-2":   'UIO-67 2x alkane-HNC$_3$',
    "UIO-67-HNC4-alkane":     'UIO-67 alkane-HNC$_4$',
    "UIO-67-HNC4-alkane-2":   'UIO-67 2x alkane-HNC$_4$',
    "UIO-67-HNC5-alkane":     'UIO-67 alkane-HNC$_5$',
    "UIO-67-HNC5-alkane-2":   'UIO-67 2x alkane-HNC$_5$',
    "UIO-67-HNC5-branched":   'UIO-67 branched-HNC$_5$',
    "UIO-67-HNC5-branched-2": 'UIO-67 2x branched-HNC$_5$',
    "UIO-67-HNC5-ring":       'UIO-67 ring-HNC$_5$',
    "UIO-67-HNC5-ring-2":     'UIO-67 2x ring-HNC$_5$',
    "UIO-67-HNC6-ring":       'UIO-67 ring-HNC$_6$',
    "UIO-67-HNC6-ring-2":     'UIO-67 2x ring-HNC$_6$',
    "UIO-67-N3":              'UIO-67 N$_3$',
    "UIO-67-N3-2":            'UIO-67 2x N$_3$',
    "UIO-67-NC4-2":           'UIO-67 2x NC$_4$',
    "UIO-67-NH2":             'UIO-67 NH$_2$',
    "UIO-67-NH2-2":           'UIO-67 2x NH$_2$',
    "UIO-67-NH2-10x":         'UIO-67 NH$_2$ 10x',
    "UIO-67-NH2-2-10x":       'UIO-67 2x NH$_2$ 10x',
    "UIO-67-CH3":             'UIO-67 CH$_3$',
    "UIO-67-CH3-2":           'UIO-67 2x CH$_3$',
    "UIO-67-OC3-alkane":      'UIO-67 alkane-OC$_3$',
    "UIO-67-OC3-alkane-2":    'UIO-67 2x alkane-OC$_3$',
    "UIO-67-OC4-alkane":      'UIO-67 alkane-OC$_4$',
    "UIO-67-OC4-alkane-2":    'UIO-67 2x alkane-OC$_4$',
    "UIO-67-OC5-alkane":      'UIO-67 alkane-OC$_5$',
    "UIO-67-OC5-alkane-2":    'UIO-67 2x alkane-OC$_5$',
    "UIO-67-OH":              'UIO-67 OH',
    "UIO-67-OH-2":            'UIO-67 2x OH'
}

mof_order = [
    'UIO-66',
    'UIO-66 4x F',
    'UIO-66 2x CF$_3$',
    'UIO-66 2x NC$_4$',
    'UIO-66 OH',
    'UIO-66 2x OH',
    'UIO-66 N$_3$',
    'UIO-66 2x N$_3$',
    'UIO-66 NH$_2$',
    'UIO-66 2x NH$_2$',
    'UIO-66 alkane-HNC$_3$',
    'UIO-66 2x alkane-HNC$_3$',
    'UIO-66 alkane-HNC$_4$',
    'UIO-66 2x alkane-HNC$_4$',
    'UIO-66 alkane-HNC$_5$',
    'UIO-66 2x alkane-HNC$_5$',
    'UIO-66 branched-HNC$_5$',
    'UIO-66 2x branched-HNC$_5$',
    'UIO-66 ring-HNC$_5$',
    'UIO-66 2x ring-HNC$_5$',
    'UIO-66 ring-HNC$_6$',
    'UIO-66 2x ring-HNC$_6$',
    'UIO-66 alkane-OC$_3$',
    'UIO-66 2x alkane-OC$_3$',
    'UIO-66 alkane-OC$_4$',
    'UIO-66 2x alkane-OC$_4$',
    'UIO-66 alkane-OC$_5$',
    'UIO-66 2x alkane-OC$_5$',
    'UIO-67',
    'UIO-67 8x F',
    'UIO-67 2x CF$_3$',
    'UIO-67 2x NC$_4$',
    'UIO-67 OH',
    'UIO-67 2x OH',
    'UIO-67 N$_3$',
    'UIO-67 2x N$_3$',
    'UIO-67 NH$_2$',
    'UIO-67 NH$_2$ 10x',
    'UIO-67 2x NH$_2$',
    'UIO-67 2x NH$_2$ 10x',
    'UIO-67 CH$_3$',
    'UIO-67 2x CH$_3$',
    'UIO-67 alkane-HNC$_3$',
    'UIO-67 2x alkane-HNC$_3$',
    'UIO-67 alkane-HNC$_4$',
    'UIO-67 2x alkane-HNC$_4$',
    'UIO-67 alkane-HNC$_5$',
    'UIO-67 2x alkane-HNC$_5$',
    'UIO-67 branched-HNC$_5$',
    'UIO-67 2x branched-HNC$_5$',
    'UIO-67 ring-HNC$_5$',
    'UIO-67 2x ring-HNC$_5$',
    'UIO-67 ring-HNC$_6$',
    'UIO-67 2x ring-HNC$_6$',
    'UIO-67 alkane-OC$_3$',
    'UIO-67 2x alkane-OC$_3$',
    'UIO-67 alkane-OC$_4$',
    'UIO-67 2x alkane-OC$_4$',
    'UIO-67 alkane-OC$_5$',
    'UIO-67 2x alkane-OC$_5$'
]

@click.command()
@click.argument('loadings_csv', type=click.Path())
@click.argument('henrys_csv', type=click.Path())
@click.argument('diff_csv', type=click.Path())
@click.option('--output-path', type=click.Path(), default="data-all-mofs.csv")
def create_diff_ads_m_a3(loadings_csv, henrys_csv, diff_csv, output_path="data-all-mofs.csv"):
    # ASSUME STP
    n2_pa = 79033.50
    h2o_pa = 2050
    co2_pa = 42.18

    henrys = pd.read_csv(henrys_csv, usecols=['mof', 'henrys_mol_kg_pa.2', 'molkg_per_m_uc', 'uc_volume_a3'])
    henrys.rename(columns={'henrys_mol_kg_pa.2':'h2o_mol_kg_pa'}, inplace=True)
    henrys['a_h2o_m_a3'] = henrys["h2o_mol_kg_pa"] * h2o_pa / (henrys['molkg_per_m_uc'] * henrys['uc_volume_a3'])
    henrys = henrys.filter(['mof', 'a_h2o_m_a3'])

    loadings = pd.read_csv(loadings_csv, usecols=['mof', 'gas', 'loading_m_uc', 'uc_volume_a3'])
    loadings['loading_m_a3'] = loadings['loading_m_uc'] / loadings['uc_volume_a3']
    loadings.drop("loading_m_uc", axis="columns", inplace=True)
    loadings = loadings.pivot(index="mof", columns="gas", values=['loading_m_a3'])
    loadings.columns = ["_".join(a) for a in loadings.columns.to_flat_index()]
    loadings.rename(columns={'mof_':'mof', "loading_m_a3_co2": "a_co2_m_a3", "loading_m_a3_n2": "a_n2_m_a3"}, inplace=True)

    diffs = pd.read_csv(diff_csv, usecols=["mof", "gas", "d_fit_a2_fs", "msd_a2", "d_fit_lower_interval_a2_fs", "d_fit_upper_interval_a2_fs"], skipinitialspace=True)
    diffs.rename(columns={
            'd_fit_a2_fs': 'd_a2_fs',
            'd_fit_lower_interval_a2_fs': 'd_lower_a2_fs',
            'd_fit_upper_interval_a2_fs': 'd_upper_a2_fs',
        }, inplace=True)
    diffs = diffs.pivot(index="mof", columns="gas", values=["msd_a2", "d_a2_fs", "d_lower_a2_fs", "d_upper_a2_fs"])
    diffs.reset_index(level=0, inplace=True) # convert mof to column
    diffs.columns = ["_".join(a) for a in diffs.columns.to_flat_index()]
    diffs.rename(columns={'mof_':'mof',
        "d_a2_fs_co2": "d_co2_a2_fs", "d_a2_fs_n2": "d_n2_a2_fs", "d_a2_fs_tip4p": "d_h2o_a2_fs",
        "d_lower_a2_fs_co2": "d_lower_co2_a2_fs", "d_lower_a2_fs_n2": "d_lower_n2_a2_fs", "d_lower_a2_fs_tip4p": "d_lower_h2o_a2_fs",
        "d_upper_a2_fs_co2": "d_upper_co2_a2_fs", "d_upper_a2_fs_n2": "d_upper_n2_a2_fs", "d_upper_a2_fs_tip4p": "d_upper_h2o_a2_fs"
        },
    inplace=True)
    diffs.replace(np.inf, 1000., inplace=True)
    diffs.replace(np.nan, 0., inplace=True)

    data = pd.merge(henrys, loadings, on="mof")
    data = pd.merge(data, diffs, on="mof")

    data['mof'] = data['mof'].str.replace("uio6", "UIO-6")
    data['mof'] = data['mof'].map(mof_name_mapping)
    data.set_index('mof').reindex(mof_order).to_csv(output_path, float_format='%.2e')

@click.command()
@click.argument('loadings_csv', type=click.Path())
@click.argument('henrys_csv', type=click.Path())
def loadings2selectivities(loadings_csv, henrys_csv):

    n2_pa = 79033.50
    h2o_pa = 2050
    co2_pa = 42.18

    henrys = pd.read_csv(henrys_csv, usecols=['mof', 'henrys_mol_kg_pa.2', 'henrys_err.2', 'mol/kg->V/V'])
    henrys.rename(columns={'henrys_mol_kg_pa.2':'h2o_mol_kg', 'henrys_err.2':'h2o_err_mol_kg'}, inplace=True)
    henrys["loading_h2o_old"] = henrys["h2o_mol_kg"] * h2o_pa
    henrys['loading_h2o'] = henrys["h2o_mol_kg"] * henrys["mol/kg->V/V"] * h2o_pa

    loadings = pd.read_csv(loadings_csv)
    loadings = loadings.pivot(index="mof", columns="gas", values=["loading", "loading err"])
    loadings.columns = ["_".join(a) for a in loadings.columns.to_flat_index()]

    data = pd.merge(henrys, loadings, on="mof")
    data["co2/n2 selectivity"] = (data['loading_co2'] / co2_pa) / (data['loading_n2'] / n2_pa)
    data["co2/h2o selectivity"] = (data['loading_co2'] / co2_pa) / (data['loading_h2o'] / h2o_pa)
    data['mof'] = data['mof'].str.replace("uio6", "UIO-6")
    data['mof'] = data['mof'].map(mof_name_mapping)

    data.set_index('mof').reindex(mof_order).to_csv("loadings_all.csv")

@click.command()
@click.argument('diff_csv', type=click.Path())
def diffusivities2selectivities(diff_csv):
    diffs = pd.read_csv(diff_csv, usecols=["mof", "gas", "D(FIT)", "MSD"], skipinitialspace=True)
    diffs.rename(columns={'D(FIT)':'diff', 'MSD':'msd'}, inplace=True)
    diffs.loc[diffs["msd"] < 200, 'diff'] = 0.
    diffs.drop("msd", axis='columns', inplace=True)

    diffs = diffs.pivot(index="mof", columns="gas", values=["diff"])
    diffs.reset_index(level=0, inplace=True) # convert mof to column
    diffs.columns = ["_".join(a) for a in diffs.columns.to_flat_index()]
    diffs.rename(columns={'mof_':'mof', "diff_co2": "CO2", "diff_n2": "N2", "diff_tip4p": "H2O"}, inplace=True)

    diffs["CO2/N2"] = diffs['CO2'] / diffs['N2']
    diffs["CO2/H2O"] = diffs['CO2'] / diffs['H2O']
    diffs['mof'] = diffs['mof'].str.replace("uio6", "UIO-6")
    diffs['mof'] = diffs['mof'].map(mof_name_mapping)

    diffs.replace(np.inf, 1000., inplace=True)
    diffs.replace(np.nan, 0., inplace=True)

    diffs.set_index('mof').reindex(mof_order).to_csv("diff_summ.csv", float_format='%.2e')
