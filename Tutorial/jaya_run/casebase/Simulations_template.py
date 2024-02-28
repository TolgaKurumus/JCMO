import multiprocessing
import numpy as np
import cantera as ct
from time import time
import itertools
from statistics import mean
import glob


gases = {}

def init_process(mech):
    """
    This function is called once for each process in the Pool. We use it to
    initialize any Cantera objects we need to use.
    """
    gases[mech] = ct.Solution(mech)

nProcs = 4
mechanism = 'mech_to_optimize.yaml'

# APPEND HERE

def calculate_mean_objective():
    objective_files = glob.glob('idt_objective_*.txt') + glob.glob('lbv_objective_*.txt')
    objective_values = []

    for file in objective_files:
        with open(file, 'r') as f:
            lines = f.readlines()
            if lines:
                # Get the last line (mean value)
                last_line = lines[-1]
                try:
                    value = float(last_line.strip())
                    objective_values.append(value)
                except ValueError:
                    print(f"Could not convert {last_line} to float in file {file}")

    if objective_values:
        overall_mean = mean(objective_values)
        with open('objective.txt', 'w') as f:
            f.write(f'{overall_mean}')
    else:
        print("No objective values found.")

# Call the function
calculate_mean_objective()
