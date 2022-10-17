import argparse
import gzip

import click
import numpy as np

@click.command()
@click.argument('input-filenames', type=click.Path())
@click.option('--output-path', type=click.Path())
@click.option("--atoms-per-molecule", default=3, type=int, help="Number of atoms per molecule.")
@click.option("--start-molecule-index", default=1, type=int, help="index of first molecule to track.")
def lammpstrj2npy(input_filenames, output_path="gastrj.npy", atoms_per_molecule=3, start_molecule_index=1):
    num_cols = 3 # x, y, z (for COM)
    data = []
    row_num = 0

    if args.input_filename.endswith(".gz"):
        f = gzip.open(args.input_filename, 'r')
    else:
        f = open(args.input_filename, 'r')

    while True:
        try:
            _ = next(f) # timestep label
        except StopIteration:
            finished = True
            break
        except EOFError:
            print("Surprise end of file! Possibly this gzip was saved without being closed properly")
            break

        timestep = int(next(f))
        if row_num % 1000 == 0:
            print("row %d: timestep %d" % (row_num, timestep))

        _ = next(f) # number of atoms
        num_atoms = int(next(f))
        num_molecules = num_atoms // args.atoms_per_molecule

        _ = next(f) # box bounds
        _ = next(f) # box bounds x
        _ = next(f) # box bounds y
        _ = next(f) # box bounds z

        _ = next(f) # atoms


        masses = np.zeros(num_molecules)
        timestep_data = np.zeros((num_molecules,3))
        for a in range(num_atoms):
            cols = next(f).strip().split()
            mol_index = int(cols[2]) - args.start_molecule_index

            mass = float(cols[3])
            x = float(cols[4])
            y = float(cols[5])
            z = float(cols[6])

            # mass is added here so COM is calculated when divided by total mass
            masses[mol_index] += mass
            timestep_data[mol_index, 0] += x * mass
            timestep_data[mol_index, 1] += y * mass
            timestep_data[mol_index, 2] += z * mass

        # divide x,y,z by total mass, giving COM
        timestep_data /= np.repeat(masses, 3).reshape(timestep_data.shape)
        data.append(timestep_data)
        row_num += 1

    f.close()

    print("finished at row # %d" % row_num)

    np_data = np.array(data)
    np.save(args.output_filename, np_data)


if __name__ == '__main__':
    lammpstrj2npy()

