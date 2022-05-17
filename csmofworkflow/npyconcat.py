
import click
import numpy as np

@click.command()
@click.argument('input-filenames', type=click.Path(), nargs=-1)
@click.option('--output-path', type=click.Path())
def npyconcat(input_filenames, output_path="gastrj.npy"):
    all_arrays = [np.load(path) for path in input_filenames]
    final_array = np.concatenate(all_arrays, axis=1)
    np.save(output_path, final_array)

if __name__ == '__main__':
    npyconcat()


