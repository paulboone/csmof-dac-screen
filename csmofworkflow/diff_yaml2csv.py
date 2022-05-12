import csv
import glob
from pathlib import Path

import click
import yaml

@click.command()
@click.argument('yamlglob')
@click.option('--output-path', type=click.Path(), default="diffusivities.csv")
def diff_yaml2csv(yamlglob, output_path="diffusivities.csv"):
    with open(output_path, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(["mof", "gas", "msd_a2", "d_msd_a2_fs", "d_fit_a2_fs", "d_fit_lower_interval_a2_fs", "d_fit_upper_interval_a2_fs"])

        for yaml_path in Path("./").glob(yamlglob):
            with open(yaml_path, "r") as f:
                d = yaml.safe_load(f)

                csvwriter.writerow([
                    d['mof'],
                    d['gas'],
                    d['msd_a2'],
                    d['d_msd_a2_fs'],
                    d['d_fit_a2_fs'],
                    d['d_fit_lower_interval_a2_fs'],
                    d['d_fit_upper_interval_a2_fs'],
                ])

if __name__ == '__main__':
    diff_yaml2csv()

