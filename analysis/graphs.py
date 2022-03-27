import csv
import sys

from fipy import Variable, FaceVariable, CellVariable, Grid1D, ExplicitDiffusionTerm, TransientTerm, DiffusionTerm, Viewer
from fipy.tools import numerix
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def csmof_pde(diff, adsorption, mesh, timestep, steps, x_csdiv, saturation_threshold=0.8, exit_on_core_saturation=False):
    conc = CellVariable(name="conc", mesh=mesh, value=0.)
    conc.constrain(adsorption, mesh.facesLeft)
    conc.faceGrad.constrain([0.], mesh.facesRight)
    eq = TransientTerm() == ExplicitDiffusionTerm(coeff=diff)

    # print("adsorption: ", adsorption)
    # core_length = (mesh.x[-1] - mesh.x[round(x_csdiv) - 1])
    core_length = len(mesh.x) - round(x_csdiv) - 1 # USE THIS UNTIL WE NORMALIZE UNITS
    # print("core_length: ", core_length)
    # core_saturation_adsorption = adsorption * (mesh.x[-1] - mesh.x[round(x_csdiv) - 1])

    cs_ads = []
    c_ads = []
    breakthrough_time = -1
    core_saturation_time = -1
    for step in range(steps):
        eq.solve(var=conc, dt=timestep)

        # cs_ads.append(np.mean(conc))
        # c_ads.append(np.mean(conc[round(x_csdiv):]))

        cs_ads.append(np.trapz(conc))
        c_ads.append(np.trapz(conc[round(x_csdiv):]))

        if breakthrough_time == -1 and conc[round(x_csdiv)] > 1e-5:
            print("breakthrough time: ", step, conc[round(x_csdiv)])
            breakthrough_time = step * timestep
        if step % 1000 == 0:
            print("Step %d: core %5.1f%% saturated" % (step, 100*(c_ads[-1] / core_length) / adsorption))
            if exit_on_core_saturation and core_saturation_time > 0:
                print("step: ", step)
                break
        #     print("--", step)
        #     print("ads core core: ", c_ads[-1])
        #     print("current core ads / l: %f; 50%% adsorption: %f" % (c_ads[-1] / core_length, 0.5*adsorption))
        #     print("ads @ left-boundary: ", conc[0])
        #     print("ads @ CS-boundary: ", conc[round(x_csdiv)])
        #     print("ads @ right-boundary: ", conc[-1])
        #     print(round(x_csdiv))
        #     print(conc[round(x_csdiv):])
        #     print(np.trapz(conc[round(x_csdiv):]))
        #     print("%5.2f%%" % ((c_ads[-1] / core_length) / adsorption))

        if core_saturation_time == -1 and c_ads[-1] / core_length > saturation_threshold * adsorption:
            print("core saturation time: ", step*timestep)
            core_saturation_time = step * timestep

    return (conc, np.array(cs_ads), np.array(c_ads)), breakthrough_time, core_saturation_time, step + 1

def add_plots_for_mof(axes, mof, mesh, steps, timestep, co2_conc, co2, co2_core, n2_conc, n2, n2_core, h2o_conc, h2o, h2o_core, x_csdiv):

    time_ns = np.array(range(steps)) * timestep / 1e6 #ns

    i = 0
    axes[i].set_title(mof, loc="left", pad=20)
    axes[i].set_title("conc vs x @ t=%d" % steps, loc="right")
    axes[i].plot(list(mesh.vertexCoords[0,1:]), list(co2_conc * 10 ), label="co2 x 10", c='orange')
    axes[i].plot(list(mesh.vertexCoords[0,1:]), list(n2_conc),  label="n2", c='grey')
    axes[i].plot(list(mesh.vertexCoords[0,1:]), list(h2o_conc * 10), label="h2o x 10", c='blue')
    axes[i].set_xlabel("x [Angstroms]")
    axes[i].set_ylabel("concentration")
    axes[i].set_xlim(0.)
    axes[i].axvline(x_csdiv, ls="--", color="gray", lw=2)
    axes[i].legend()

    i += 1
    axes[i].set_title("total adsorbed in CORE-SHELL vs time")
    axes[i].plot(time_ns, co2 * 100, label="co2 x 100", c='orange')
    axes[i].plot(time_ns, n2, label="n2", c='grey')
    axes[i].plot(time_ns, h2o * 100, label="h2o x 100", c='blue')
    axes[i].set_xlabel("t [ns]")
    axes[i].set_ylabel("total adsorbed in C-S")
    axes[i].set_xlim(0.)
    axes[i].legend()

    i += 1
    axes[i].set_title("fraction co2 in CORE-SHELL vs time")
    axes[i].plot(time_ns, 100 * co2 / (co2 + n2 + h2o), label="fraction co2 x 100")
    axes[i].set_xlabel("t [ns]")
    axes[i].set_ylabel("fraction")
    axes[i].set_ylim(0., 1.02)
    axes[i].set_xlim(0.)
    axes[i].axhline(400*100/1000000, c="black", ls="--", lw=2, label="400 ppm CO2")
    axes[i].legend()

    i += 1
    axes[i].set_title("fraction co2 / (co2 + h2o) in CORE-SHELL")
    axes[i].plot(time_ns, co2 / (co2 + h2o), label="fraction co2 / (co2 + h2o) in CORE-SHELL")
    axes[i].set_xlabel("t [ns]")
    axes[i].set_ylabel("fraction")
    axes[i].set_ylim(0., 1.02)
    axes[i].set_xlim(0.)
    axes[i].legend()

    i += 1
    axes[i].set_title("total adsorbed in CORE vs time")
    axes[i].plot(time_ns, co2_core * 100, label="co2 x 100", c='orange')
    axes[i].plot(time_ns, n2_core, label="n2", c='grey')
    axes[i].plot(time_ns, h2o_core * 100, label="h2o x 100", c='blue')
    axes[i].set_xlabel("t [ns]")
    axes[i].set_ylabel("total adsorbed in core")
    axes[i].set_xlim(0.)
    axes[i].legend()

    i += 1
    axes[i].set_title("fraction co2 in CORE vs time")
    axes[i].plot(time_ns, 100 * co2_core / (co2_core + n2_core + h2o_core), label="fraction co2 in core x 100")
    axes[i].set_xlabel("t [ns]")
    axes[i].set_ylabel("fraction")
    axes[i].set_ylim(0., 1.02)
    axes[i].set_xlim(0.)
    axes[i].axhline(400*100/1000000, c="black", ls="--", lw=2, label="400 ppm CO2")
    axes[i].legend()

    i += 1
    axes[i].set_title("fraction co2 / (co2 + h2o) in CORE")
    axes[i].plot(time_ns, co2_core / (co2_core + h2o_core), label="fraction co2 / (co2 + h2o) in CORE")
    axes[i].set_xlabel("t [ns]")
    axes[i].set_ylabel("fraction")
    axes[i].set_ylim(0., 1.02)
    axes[i].set_xlim(0.)
    axes[i].legend()


def format_time(f):
    if f == -1:
        return "-1"
    else:
        return "%.0f" % (f/1000)

# nx = 50
# dx = 1. # Angstroms
# steps = 50
# max_diff = 4
# timestep = 0.9 * dx**2 / (2 * max_diff)
# timestep = 0.9 * dx**2 / (2 * max_diff)
# print("timestep = %f" % timestep)
# print("timestep / max_diff= %f" % (timestep / max_diff))


csmof_size = 500
nx = 50
dx = csmof_size / nx
max_diff = 1.2e-3 # Angstroms^2 / fs from uio67-OH
timestep = 0.9 * dx**2 / (5 * max_diff)
# timestep = 1000
max_steps = 100000
# steps = 25000
print("timestep = %f" % timestep)
print("timestep / max_diff= %f" % (timestep / max_diff))

mofs = pd.read_csv("diff-ads-noD0.csv")

num_graphs = 7
num_mofs = len(mofs)
# num_mofs = 5
fig = plt.figure(figsize=(num_graphs*4 + 1, num_mofs*4), constrained_layout=True)
axes = fig.subplots(num_mofs, num_graphs, squeeze=False)

saturation_threshold = 0.8

break_sat_times = []
for i, mof in enumerate(mofs.itertuples()):
    if i >= num_mofs:
        break
    print(mof.mof)
    # if str(mof.mof) != "uio67-OH-2":
    #     print("continue")
    #     continue
    print(mof.d_co2, mof.d_n2, mof.d_h2o)
    if mof.d_co2 == 0.0 or mof.d_n2 == 0.0 or mof.d_h2o == 0.0:
        print("Diffusion is 0.0 for one of the gasses... skipping MOF")
        next
    mesh = Grid1D(nx=nx, dx=dx)
    print("CO2")
    co2tup, co2_breakthrough, co2_saturation, steps = csmof_pde(mof.d_co2, mof.a_co2, mesh, timestep, max_steps,
        x_csdiv=nx/2, saturation_threshold=saturation_threshold, exit_on_core_saturation=True)
    # steps = int(round(co2_saturation / timestep, -3)) + 1
    print("steps from co2: ", co2_saturation, timestep, steps)
    print("N2")
    n2tup, n2_breakthrough, n2_saturation, _ = csmof_pde(mof.d_n2, mof.a_n2, mesh, timestep, steps, x_csdiv=nx/2,
        saturation_threshold=saturation_threshold)
    print("H2O")
    h2otup, h2o_breakthrough, h2o_saturation, _ = csmof_pde(mof.d_h2o, mof.a_h2o, mesh, timestep, steps, x_csdiv=nx/2,
        saturation_threshold=saturation_threshold)
    add_plots_for_mof(axes[i], mof.mof, mesh, steps, timestep, *co2tup, *n2tup, *h2otup, x_csdiv=nx*dx/2)

    times = [co2_breakthrough, co2_saturation, n2_breakthrough, n2_saturation, h2o_breakthrough, h2o_saturation]
    times = [format_time(t) for t in times]
    break_sat_times.append([mof.mof, *times])


with open('breakthrough-saturation-times.csv', 'w') as csvfile:
    csvwriter = csv.writer(csvfile)
    csvwriter.writerow(["MOF", "CO2_breakthrough", "CO2_saturation", "N2_breakthrough", "N2_saturation", "H2O_breakthrough", "H2O_saturation"])
    for row in break_sat_times:
        csvwriter.writerow(row)

fig.savefig("test1.png", dpi=144)

# ax2.set_title("total adsorbed vs time")
# ax2.plot(range(0,50), co2_core)
# ax2.set_xlabel("t")
# ax2.set_ylabel("total adsorbed")
