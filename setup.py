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
          'networkx'
    ],
    entry_points={
        'console_scripts': [
            'uff-parameterize-linker = csmofworkflow.uff_parameterize_linker:uff_parameterize_linker',
            'functionalize-structure = csmofworkflow.functionalize_structure:functionalize_structure_with_linkers',
            'lmpdatdump2cif = csmofworkflow.lmpdatdump2cif:lmpdatdump2cif'
            'checkNVTdumpfile = csmofworkflow.checkdumpfile:checkdumpfile'
        ]
    }
)
