#!/bin/bash
#SBATCH --time=00:10:00
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=8
#SBATCH --cpus-per-task 1
#SBATCH --output=../output/C-%x.%j.out
#SBATCH --error=../output/C-%x.%j.err
module spider
module load Python/3.5.2-goolf-2015a
time mpirun python ../main.py