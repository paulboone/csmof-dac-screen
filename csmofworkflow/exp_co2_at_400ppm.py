from pathlib import Path

import click
import pandas as pd

from scipy.interpolate import interp1d

@click.command()
@click.argument('glob')
@click.option('--pressure', '-p', type=float, default=0.0004)
@click.option('--outputpath', '-o', type=click.Path(), default="loadings400ppm.csv")
def exp_co2_at_400ppm(glob, pressure=0.0004, outputpath="loadings400ppm.csv"):
    alldata = []
    for isotherm_path in Path("./").glob(glob):
        mof, gas, sim = isotherm_path.stem.split("_")
        isodf = pd.read_csv(isotherm_path)
        f = interp1d(isodf.pressure_bar, isodf.loading_cc_g, fill_value="extrapolate")

        alldata.append(dict(
            mof=mof,
            gas=gas,
            sim=sim,
            pressure_bar=pressure,
            loading_cc_g=f(pressure)
        ))

    df = pd.DataFrame(alldata)
    df.to_csv(outputpath, index=False)

if __name__ == '__main__':
    exp_co2_at_400ppm()
