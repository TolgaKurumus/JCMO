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
# Define the tempretures for which we will run the simulations
reference_species = "OH"

target_file = '/u/84/kurumua1/unix/InterfaceWork/JAYA-IDT-LBV-interface-tutorialTest/exp-idt-phi1.csv'
# Read the data from the CSV file
data_1_idt = np.genfromtxt(target_file, delimiter=",", skip_header=1)

# Extract the T and experimental_target values
T_1_idt = data_1_idt[:, 0]
experimental_target = data_1_idt[:, 1]

estimated_ignition_delay_times = np.ones_like(T_1_idt, dtype=float)
estimated_ignition_delay_times[:6] = 0.1
estimated_ignition_delay_times[-4:-2] = 10
estimated_ignition_delay_times[-2:] = 100

def ignition_delay_1_idt(args):
    mech, T_1_idt, experimental_target = args
    pres = 1.4
    reactor_pressure = ct.one_atm * pres
    gas = gases[mech]
    gas.TP = T_1_idt, reactor_pressure
    fuel = 'NH3:0.005715'
    oxidizer = 'O2:0.004285, Ar:0.99'
    phi = 1
    gas.set_equivalence_ratio(phi, fuel, oxidizer)
    r = ct.Reactor(contents=gas, name="Batch Reactor")
    reactor_network = ct.ReactorNet([r])
    
    objective_1_idt = []    
    
    reference_species_history = []
    time_history = []
    t = 0
    i = 0
    
    while t < estimated_ignition_delay_times[i]:
      t = reactor_network.step()
      time_history.append(t)
      reference_species_history.append(gas[reference_species].X[0])			
    i_ign = np.array(reference_species_history).argmax()
    tau = time_history[i_ign]*1e6
    objective_1_idt.append((((tau) - experimental_target)/(2*experimental_target))**2)
    fi = open("idt_objective_1_idt.txt", "a")
    fi.write('%s\n' % sum(objective_1_idt))
    fi.close()
    fi2 = open("idt_1_idt.txt", "a")
    fi2.write('%s, %s, %s\n' % ((1000/T_1_idt), experimental_target, tau))
    fi2.close()

def idt_calculate_objective_1_idt():
    objective_1_idt = []
    
    total = 0
    with open('idt_objective_1_idt.txt', 'r') as inp:
    	for line in inp:
           num = float(line)
           objective_1_idt.append(num)
    
    with open('idt_objective_1_idt.txt', 'w') as outp:
    # Write the updated lines to the file
    	outp.write('%s\n' % mean(objective_1_idt)) 
    
def idt_parallel_1_idt(mech, nProcs, T_1_idt, experimental_target):
    with multiprocessing.Pool(processes=nProcs, initializer=init_process, initargs=(mech,)) as pool:
        y = pool.map(ignition_delay_1_idt, zip(itertools.repeat(mech), T_1_idt, experimental_target))
    return y

t1 = time()

idt_parallel_1_idt(mechanism, nProcs, T_1_idt, experimental_target)

idt_calculate_objective_1_idt()

t2 = time()
print('Parallel: {0:.3f} seconds'.format(t2-t1))

# Define the tempretures for which we will run the simulations
reference_species = "OH"

target_file = '/u/84/kurumua1/unix/InterfaceWork/JAYA-IDT-LBV-interface-tutorialTest/exp-idt-phi05.csv'
# Read the data from the CSV file
data_2_idt = np.genfromtxt(target_file, delimiter=",", skip_header=1)

# Extract the T and experimental_target values
T_2_idt = data_2_idt[:, 0]
experimental_target = data_2_idt[:, 1]

estimated_ignition_delay_times = np.ones_like(T_2_idt, dtype=float)
estimated_ignition_delay_times[:6] = 0.1
estimated_ignition_delay_times[-4:-2] = 10
estimated_ignition_delay_times[-2:] = 100

def ignition_delay_2_idt(args):
    mech, T_2_idt, experimental_target = args
    pres = 1.4
    reactor_pressure = ct.one_atm * pres
    gas = gases[mech]
    gas.TP = T_2_idt, reactor_pressure
    fuel = 'NH3:0.004'
    oxidizer = 'O2:0.006, Ar:0.99'
    phi = 0.5
    gas.set_equivalence_ratio(phi, fuel, oxidizer)
    r = ct.Reactor(contents=gas, name="Batch Reactor")
    reactor_network = ct.ReactorNet([r])
    
    objective_2_idt = []    
    
    reference_species_history = []
    time_history = []
    t = 0
    i = 0
    
    while t < estimated_ignition_delay_times[i]:
      t = reactor_network.step()
      time_history.append(t)
      reference_species_history.append(gas[reference_species].X[0])			
    i_ign = np.array(reference_species_history).argmax()
    tau = time_history[i_ign]*1e6
    objective_2_idt.append((((tau) - experimental_target)/(2*experimental_target))**2)
    fi = open("idt_objective_2_idt.txt", "a")
    fi.write('%s\n' % sum(objective_2_idt))
    fi.close()
    fi2 = open("idt_2_idt.txt", "a")
    fi2.write('%s, %s, %s\n' % ((1000/T_2_idt), experimental_target, tau))
    fi2.close()

def idt_calculate_objective_2_idt():
    objective_2_idt = []
    
    total = 0
    with open('idt_objective_2_idt.txt', 'r') as inp:
    	for line in inp:
           num = float(line)
           objective_2_idt.append(num)
    
    with open('idt_objective_2_idt.txt', 'w') as outp:
    # Write the updated lines to the file
    	outp.write('%s\n' % mean(objective_2_idt)) 
    
def idt_parallel_2_idt(mech, nProcs, T_2_idt, experimental_target):
    with multiprocessing.Pool(processes=nProcs, initializer=init_process, initargs=(mech,)) as pool:
        y = pool.map(ignition_delay_2_idt, zip(itertools.repeat(mech), T_2_idt, experimental_target))
    return y

t1 = time()

idt_parallel_2_idt(mechanism, nProcs, T_2_idt, experimental_target)

idt_calculate_objective_2_idt()

t2 = time()
print('Parallel: {0:.3f} seconds'.format(t2-t1))


target_file = '/u/84/kurumua1/unix/InterfaceWork/JAYA-IDT-LBV-interface-tutorialTest/exp-lbv.csv'
# Read the data from the CSV file
data = np.genfromtxt(target_file, delimiter=",", skip_header=1)

# Extract the T and experimental_target values
phi_1_idt = data[:, 0]
experimental_target = data[:, 1]


def burning_velocity_1_idt(args):
    mech, phi_1_idt, experimentValuesLBV = args
    gas = gases[mech]
    initial_grid = np.linspace(0.0, 0.05, 100)
    pres = 1
    P = ct.one_atm * pres
    T = 298
    fuel = 'NH3: 1.0'
    oxidizer = 'O2: 1.0, N2: 3.76'
    vels = []
    objLBV = []
    gas.TP = T, P
    gas.set_equivalence_ratio(phi_1_idt, fuel, oxidizer)
    f = ct.FreeFlame(gas, initial_grid)
    f.transport_model = "mixture-averaged" # Mix-Multi-UnityLewis
    f.set_refine_criteria(ratio=3.0, slope=0.1, curve=0.2)
    f.set_grid_min(1e-10)
    f.solve(loglevel=0, refine_grid=True, auto=True)
    vels = f.velocity[0]*100
    objLBV.append(((((vels) - experimentValuesLBV)/(2*experimentValuesLBV)))**2)
    fi = open("lbv_objective_1_idt.txt", "a")
    fi.write('%s\n' % sum(objLBV))
    fi.close() 
    fi2 = open("lbv_1_idt.txt", "a")
    fi2.write('%s, %s, %s\n' % (phi_1_idt, experimentValuesLBV, vels))
    fi2.close()

def lbv_calculate_objective_1_idt():
    objective_1_idt = []
    
    total = 0
    with open('lbv_objective_1_idt.txt', 'r') as inp:
    	for line in inp:
           num = float(line)
           objective_1_idt.append(num)
    
    with open('lbv_objective_1_idt.txt', 'w') as outp:
    # Write the updated lines to the file
    	outp.write('%s\n' % mean(objective_1_idt)) 
    
def lbv_parallel_1_idt(mech, nProcs, phi_1_idt, experimental_target):
    with multiprocessing.Pool(processes=nProcs, initializer=init_process, initargs=(mech,)) as pool:
        y = pool.map(burning_velocity_1_idt, zip(itertools.repeat(mech), phi_1_idt, experimental_target))
    return y  
    
t1 = time()

lbv_parallel_1_idt(mechanism, nProcs, phi_1_idt, experimental_target)

lbv_calculate_objective_1_idt()

t2 = time()
print('Parallel: {0:.3f} seconds'.format(t2-t1))


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
