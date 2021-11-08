from pathlib import Path

import click

from mofun import Atoms, replace_pattern_in_structure
from mofun.rough_uff import assign_pair_coeffs

@click.command()
@click.argument('structure_path',  type=click.Path())
@click.argument('linker_path', type=click.Path())
@click.argument('fnlinkers', nargs=-1, type=click.Path())
@click.option('--replace-fraction', type=float, default=1.0)
@click.option('--expected-num', type=int, default=None)
@click.option('--output-dir', type=click.Path())
def functionalize_structure_with_linkers(structure_path, linker_path, fnlinkers, replace_fraction=1.0,
        expected_num=None,output_dir=Path()):

    linker = Atoms.load(Path(linker_path))
    structure = Atoms.load(structure_path)
    output_dir = Path(output_dir)
    assign_pair_coeffs(structure, assign_atom_type_labels_from_elements=True)

    for fnlinker_path in fnlinkers:
        print("reading %s" %fnlinker_path)
        fnlinker = Atoms.load(fnlinker_path)
        try:
            new_structure, num_matches = replace_pattern_in_structure(structure, linker, fnlinker,
                replace_fraction=replace_fraction, return_num_matches=True)

            if  expected_num is not None and expected_num != num_matches:
                print("ERROR: # of matches %d does NOT match expected number %d" % (num_matches, expected_num))
            else:
                new_structure.save(output_dir / (Path(fnlinker_path).stem + ".lmpdat"))
        except Exception as e:
            print("ERROR! ", e.args)

if __name__ == '__main__':
    functionalize_structure_with_linkers()
