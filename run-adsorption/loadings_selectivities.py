
import csv
from pathlib import Path
import sys

import click

import pandas as pd

@click.command()
@click.argument('loadings_csv', type=click.Path())
@click.argument('henrys_csv', type=click.Path())
def loadings_selectivities(loadings_csv, henrys_csv):


    n2_pa=79033.50
    h2o_pa=2050
    co2_pa= 42.18


    henrys = pd.read_csv(henrys_csv, usecols=['mof', 'henrys.2', 'henrys_err.2', 'mol/kg->V/V'])
    henrys.rename(columns={'henrys.2':'h2o_mol_kg', 'henrys_err.2':'h2o_err_mol_kg'}, inplace=True)
    henrys["loading_h2o_old"] = henrys["h2o_mol_kg"]*water_pa
    henrys['loading_h2o'] = henrys["h2o_mol_kg"] * henrys["mol/kg->V/V"] * water_pa

    loadings = pd.read_csv(loadings_csv)
    loadings = loadings.pivot(index="mof", columns="gas", values=["loading", "loading err"])
    loadings.columns = ["_".join(a) for a in loadings.columns.to_flat_index()]

    data = pd.merge(henrys, loadings, on="mof")
    data["co2/n2 selectivity"] = (data['loading_co2'] / co2_pa) / (data['loading_n2'] / n2_pa)
    data["co2/h2o selectivity"] = (data['loading_co2'] / co2_pa) / (data['loading_h2o'] / h2o_pa)
    data.sort_values('mof', inplace=True)
    data.set_index('mof', inplace=True)
    data.to_csv("loadings_all.csv")

    data = data[['mof', '   ']]
    data.to_csv("loadings_all.csv")


if __name__ == '__main__':
    loadings_selectivities()
