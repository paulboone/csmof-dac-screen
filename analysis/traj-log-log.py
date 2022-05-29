
import matplotlib.pyplot as plt
import numpy as np


data = np.load('aggregated_traj_results.npy')
time = range(0.5,10.5 + 0.5, 1000)

fig = plt.figure(figsize=(7,7))
ax = fig.add_subplot(1, 1, 1)
ax.set_xlabel('tau [ns]')
ax.set_ylabel('MSD [Ang^2]')
ax.grid(linestyle='-', color='0.7', zorder=0)
ax.loglog(time, data, zorder=2)
fig.savefig("loglog.png", dpi=288)

