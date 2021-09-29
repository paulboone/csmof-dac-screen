
import csv
from pathlib import Path
import sys

import click

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
    "UIO-67-BPDC":            'UIO-67 BPDC$_2$',
    "UIO-67-BPDC-2":          'UIO-67 2x BPDC$_2$',
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
    'UIO-67 2x NH$_2$',
    'UIO-67 BPDC$_2$',
    'UIO-67 2x BPDC$_2$',
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
def loadings_selectivities(loadings_csv, henrys_csv):

    n2_pa=79033.50
    h2o_pa=2050
    co2_pa= 42.18

    henrys = pd.read_csv(henrys_csv, usecols=['mof', 'henrys_mol_kg_pa.2', 'henrys_err.2', 'mol/kg->V/V'])
    henrys.rename(columns={'henrys_mol_kg_pa.2':'h2o_mol_kg', 'henrys_err.2':'h2o_err_mol_kg'}, inplace=True)
    henrys["loading_h2o_old"] = henrys["h2o_mol_kg"]*h2o_pa
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


if __name__ == '__main__':
    loadings_selectivities()
