#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='CSMOF-DAC-WORKFLOW',
    version='0.1.0',
    description='Workflow for running core-shell MOF simulations',
    author='Paul Boone',
    author_email='paulboone@pitt.edu',
    url='https://github.com/paulboone/csmof-dac-screening.git',
    install_requires=[
          'ase',
          'numpy',
          'scipy',
          'networkx',
          'click',
    ],
    entry_points={
        'console_scripts': [
            'uff-parameterize-linker = csmofworkflow.uff_parameterize_linker:uff_parameterize_linker',
            'functionalize-structure = csmofworkflow.functionalize_structure:functionalize_structure_with_linkers',
            'lmpdatdump2cif = csmofworkflow.lmpdatdump2cif:lmpdatdump2cif',
            'checkNVTdumpfile = csmofworkflow.checkdumpfile:checkdumpfile',
            'mofun_converter = csmofworkflow.mofun_converter:mofun_converter',
            'packmol_gaslmpdat = csmofworkflow.packmol_gaslmpdat:packmol_gaslmpdat',
            'check-config = csmofworkflow.check_config:check_config',
            'extract-loadings = csmofworkflow.extract_loadings:extract_loadings',
            'extract-henrys = csmofworkflow.extract_henrys:extract_henrys',
            'loadings2selectivities = csmofworkflow.calc_selectivities:loadings2selectivities',
            'diffusivities2selectivities = csmofworkflow.calc_selectivities:diffusivities2selectivities',
            'diffads-csv = csmofworkflow.calc_selectivities:create_diff_ads_m_a3',
            'average-temps = csmofworkflow.average_temps:average_temps'
        ]
    }
)
