#!/usr/bin/env python3
import csv
import sys

import click
import numpy as np

@click.command()
@click.option("--rowheader", "-r", type=str)
def average_temps(rowheader=""):
    tsv = csv.writer(sys.stdout)
    temps = [rowheader]

    ## NVE sizes
    # a = np.loadtxt("nvt-eq.tsv", skiprows=1)
    # temps += list(a[0:2000,1].reshape(400,5).mean(axis=0))
    #
    # a = np.loadtxt("nve-eq.tsv", skiprows=1)
    # temps += list(a[0:500,1].reshape(100,5).mean(axis=0))
    #
    # a = np.loadtxt("nve.tsv", skiprows=1)
    # temps += list(a[0:10000,1].reshape(5,2000).mean(axis=1))

    a = np.loadtxt("nvt-eq.tsv", skiprows=1)
    temps += list(a[0:2000,1].reshape(400,5).mean(axis=0))

    a = np.loadtxt("nvt.tsv", skiprows=1)
    temps += list(a[0:10000,1].reshape(5,2000).mean(axis=1))

    tsv.writerow(temps)


if __name__ == '__main__':
    average_temps()
