#!/bin/bash
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cluster=smp
#SBATCH --time=3-0
#SBATCH --qos=normal
#SBATCH --job-name=raspa
#SBATCH --output=raspajob.log

echo JOB_ID: $SLURM_JOBID JOB_NAME: $SLURM_JOBNAME HOSTNAME: $SLURM_O_HOST
echo start_time: `date`

# dependencies
module purge


# Copy everything to scratch
cp -R $SLURM_SUBMIT_DIR/* $SLURM_SCRATCH/
mkdir -p $SLURM_SUBMIT_DIR/results
#shopt -s nullglob # Sets nullglob
#inputs=$(ls *.{input,cif,def})
#shopt -u nullglob # unsets nullglob
#for i in ${inputs[@]}; do
#    sbcast $SLURM_SUBMIT_DIR/$i $SLURM_SCRATCH/$i
#done

# The ulimit
ulimit -s unlimited

cd $SLURM_SCRATCH

run_on_exit(){
    cp -pR $SLURM_SCRATCH/* $SLURM_SUBMIT_DIR/results
}
trap run_on_exit EXIT

simulate -i *.input
