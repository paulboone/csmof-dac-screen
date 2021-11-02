"""
USES pyGAP, which does not support python 3.9 (rather, its dependency didn't) so this may require running in a different
virtual env!
"""

from pathlib import Path

import click
import pandas as pd
import pygaps as pg


@click.command()
@click.argument('glob')
@click.option('--outputpath', '-o', type=click.Path(), default="bet_surface_areas.csv")
def iso2sa(glob, outputpath="bet_surface_areas.csv"):
    kwargs = dict(
        pressure_key='pressure_bar',
        loading_key='loading_cc_g',
        pressure_unit='bar',
        pressure_mode='absolute',
        loading_unit='cm3(STP)',
        material_unit='g',
        material_basis='mass'
    )

    alldata = []
    for isotherm_path in Path("./").glob(glob):

        mof, gas, sim = isotherm_path.stem.split("_")
        # NOTE: SHOULD ONLY RUN THIS FOR N2@77K
        temp = 77
        gas = "N2"

        isodf = pd.read_csv(isotherm_path)
        isotherm = pg.PointIsotherm(isotherm_data=isodf, material=mof, adsorbate=gas, temperature=temp, **kwargs)

        data = pg.area_BET(isotherm, verbose=False)
        data['mof'] = mof
        data['gas'] = gas
        data['temp'] = temp
        data['sim'] = sim
        alldata.append(data)

    df = pd.DataFrame(alldata)
    df.to_csv(outputpath, index=False)

if __name__ == '__main__':
    iso2sa()
