#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cluster=smp
#SBATCH --time=1-0
#SBATCH --qos=short
#SBATCH --job-name=lammps.lammps
#SBATCH --output=lammps-stdout.log

# Load Modules
module load intel/2017.1.132 intel-mpi/2017.1.132
module load gcc/9.2.0

# Copy everything to scratch
mkdir -p $SLURM_SUBMIT_DIR/output
shopt -s nullglob # Sets nullglob
inputs=$(ls *.{lammps,restart,lmpdat})
shopt -u nullglob # unsets nullglob
for i in ${inputs[@]}; do
    sbcast $SLURM_SUBMIT_DIR/$i $SLURM_SCRATCH/$i
done

# The ulimit
ulimit -s unlimited

cd $SLURM_SCRATCH

run_on_exit(){
    cp -pR $SLURM_SCRATCH/* $SLURM_SUBMIT_DIR/output
}
trap run_on_exit EXIT

srun --mpi=pmi2 ~/workspace/lammps_stable/src/lmp_mpi -in *.lammps -var mofpath uio*.lmpdat -l lammps.log
