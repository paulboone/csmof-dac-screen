#!/usr/bin/env python3

import argparse
import math
import random
import yaml

import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

def autocorrFFT(x, N):
    N=len(x)
    F = np.fft.fft(x, n=2*N)  #2*N because of zero-padding
    PSD = F * F.conjugate()
    res = np.fft.ifft(PSD)
    res= (res[:N]).real   #now we have the autocorrelation in convention B
    n=N*np.ones(N)-np.arange(0,N) #divide res(m) by (N-m)
    return res/n #this is the autocorrelation in convention A

def msd_fft(r, N):
    N=len(r)
    D=np.square(r).sum(axis=1)
    D=np.append(D,0)
    S2=sum([autocorrFFT(r[:, i], N) for i in range(r.shape[1])])
    Q=2*D.sum()
    S1=np.zeros(N)
    for m in range(N):
        Q=Q-D[m-1]-D[N-m]
        S1[m]=Q/(N-m)
        # if m % 10000 == 0:
        #     print(m)
    return S1-2*S2

def attempt_fits(time, results, reduced_rows):
    """ attempt fits across different ranges

    generally for all fits, first 10% and last 50% are thrown away
    different ranges from 0.1-0.5 are tried, and fit with lowest r2 is selected as the
    "correct" fit and reported as the diffusivity.
    """
    lin_fit_pairs = [(0.0,1.0), (0.10,0.50), (0.10,0.45), (0.10,0.40), (0.10,0.35), (0.30,0.50), (0.25,0.50), (0.20,0.50), (0.15,0.50), (0.20,0.40), (0.15,0.40), (0.20, 0.45)]
    fit_results = []
    for pair in lin_fit_pairs:
        # y = at + b
        p1 = int(pair[0] * (reduced_rows - 1))
        p2 = int(pair[1] * (reduced_rows - 1))
        slope, intercept, r_value, _, _ = stats.linregress(time[p1:p2], results[p1:p2])
        poly = (slope, intercept)
        r2 = r_value ** 2
        fit_results.append([(p1, p2), r2, poly])

    fit_results.sort(key=lambda x: x[1], reverse=True)
    return fit_results

parser = argparse.ArgumentParser("./npytraj_diffusivity.py")
parser.add_argument('filename', help="Path to numpy array: should be a 3d array of row: molecule #: x, y, z")
parser.add_argument("--output-molecule-plots", action='store_true', help="output plot per molecule")
parser.add_argument("--fs-per-row", default=10, type=int, help="femtoseconds per row. Defaults to 10.")
parser.add_argument("--average-rows", default=1,  type=int, help="# of rows to average together to get a dataset of reasonable size (typically about 1000 points for graphing)")
parser.add_argument("--max-molecules", default=0,  type=int, help="maximum number of molecules to process. Useful for debugging")

# args = parser.parse_args(["./edusif/lammpstrj.npy", "--average-rows", "4000", "--output-molecule-plots", "--max-molecules", "1"])
args = parser.parse_args()

### load data and truncate to multiple of args.average_rows
data = np.load(args.filename) # row:molecule:x,y,z
num_rows, num_molecules, num_cols = data.shape
reduced_rows = num_rows // args.average_rows
num_rows = reduced_rows * args.average_rows
data = data[0:num_rows, :, :]
if args.max_molecules > 0:
    data = data[:, 0:args.max_molecules, :]
    num_molecules = args.max_molecules

# take row index for all rows, average args.average_rows number of them together, and convert to ns
simple_t = np.mean(np.arange(0,num_rows).reshape(-1, args.average_rows), axis=1) * args.fs_per_row / 1e6

### per molecule data and plots
simple_results = np.zeros((num_molecules, reduced_rows))
for m in range(num_molecules):
    print("Molecule %d..." % m)
    d0 = data[:,m,:][:num_rows,:] # m for mth molecule
    results = msd_fft(d0, num_rows)
    simple_results[m,:] = np.mean(results.reshape(-1, args.average_rows), axis=1)

# sample with replacement from available trajectories to estimate error
diffs = []
for _ in range(1000):
    all_results = np.zeros(reduced_rows)
    for molecule in random.choices(range(num_molecules), k=num_molecules):
        all_results += simple_results[molecule]
    all_results /= num_molecules

    fit_results = attempt_fits(simple_t, all_results, reduced_rows)
    p, r2, poly = fit_results[0]
    diffs.append(poly[0] / (6 * 1e6))

diffs.sort()
diffs = np.array(diffs)
np.save("sampled_diffs.npy", np.array(diffs))

# calculate confidence interval bounds on the diffusion calculated via fit
alpha = 0.05 # 95% confidence
num_to_remove_from_tail = int(len(diffs)  * alpha / 2)
d_lower_conf_bound = diffs[num_to_remove_from_tail]
d_upper_conf_bound = diffs[-num_to_remove_from_tail]

# calculate normal fit on all data (no sampling)
all_results = np.mean(simple_results, axis=0)
fit_results = attempt_fits(simple_t, all_results, reduced_rows)
total_time = simple_t[-1] * 1e6
msd = all_results[-1]
d_msd = msd / (6 * total_time)
p, r2, poly = fit_results[0]
d_fit = poly[0] / (6 * 1e6)
np.save("aggregated_traj_results.npy", all_results)

# output stats in machine-readable format
with open("diff_stats.yaml", "w") as f:
    yaml.dump(dict(
            total_time=float(total_time),
            best_fit=dict(
                start_time=float(simple_t[p[0]]),
                end_time=float(simple_t[p[1]]),
                r2=float(r2),
                poly=[float(poly[0]), float(poly[1])],
            ),
            msd_ang2=float(msd),
            d_msd_t_ang2_fs=float(d_msd),
            d_fit_ang2_fs=float(d_fit),
            d_fit_lower_interval_ang2_fs=float(d_lower_conf_bound),
            d_fit_upper_interval_ang2_fs=float(d_upper_conf_bound)
        ), f, sort_keys=False)

# output human-readable stats
print("Total Time: %f" % total_time)
print("Best fit: (%.2f - %.2f ns; r^2 = %.3f):" % (simple_t[p[0]], simple_t[p[1]], r2))
print("MSD = %4e angstrom^2" % msd)
print("D (MSD / t) = %4e angstrom^2 / fs" % d_msd)
print("D (fit) = %4e angstrom^2 / fs" % d_fit)
print("D (fit) 95%% bound interval: %4e, %4e" % (d_lower_conf_bound, d_upper_conf_bound))

# output histogram on diffusivities
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(1, 1, 1)
ax.hist(diffs, 41, density=True, facecolor='g')
ax.axvline(d_fit, lw=2, color='black')
ax.axvline(np.mean(diffs), lw=2, color='grey')
ax.axvline(d_lower_conf_bound, lw=2, color='black', ls='--')
ax.axvline(d_upper_conf_bound, lw=2, color='black', ls='--')
fig.savefig("diffusivities_hist.png", dpi=288)

# output log / log plot
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(1, 1, 1)
ax.set_xlabel('tau [ns]')
ax.set_ylabel('MSD [Ang^2]')
ax.grid(linestyle='-', color='0.7', zorder=0)
ax.loglog(simple_t, all_results, zorder=2)
fig.savefig("msd_vs_time_loglog.png", dpi=288)

# output plot of all molecules
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(1, 1, 1)
ax.set_xlabel('tau [ns]')
ax.set_ylabel('MSD [Ang^2]')
ax.grid(linestyle='-', color='0.7', zorder=0)
ax.plot(simple_t, simple_results.transpose(), zorder=2)
fig.savefig("msd_fft_molecule_plots.png", dpi=288)

# plot combined data and fits
fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(1, 1, 1)
ax.set_xlabel('tau [ns]')
ax.set_ylabel('MSD [Ang^2]')
ax.grid(linestyle='-', color='0.7', zorder=0)
ax.plot(simple_t, all_results, zorder=10)
for p, r2, poly in fit_results:
    ax.plot(simple_t[p[0]:p[1]], np.polyval(poly, simple_t[p[0]:p[1]]), zorder=2,
            label="%.1f-%.1fns r2=%0.3f: %2.0ft%+2.0f" % (simple_t[p[0]], simple_t[p[1]], r2, *poly))
ax.legend()
fig.savefig("msd_fft_all_plot.png", dpi=288)





