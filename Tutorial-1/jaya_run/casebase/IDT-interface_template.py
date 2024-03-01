# Define the tempretures for which we will run the simulations
reference_species = "OH"

target_file = 
# Read the data from the CSV file
data_INDEX = np.genfromtxt(target_file, delimiter=",", skip_header=1)

# Extract the T and experimental_target values
T_INDEX = data_INDEX[:, 0]
experimental_target = data_INDEX[:, 1]

estimated_ignition_delay_times = np.ones_like(T_INDEX, dtype=float)
estimated_ignition_delay_times[:6] = 0.1
estimated_ignition_delay_times[-4:-2] = 10
estimated_ignition_delay_times[-2:] = 100

def ignition_delay_INDEX(args):
    mech, T_INDEX, experimental_target = args
    pres = 
    reactor_pressure = ct.one_atm * pres
    gas = gases[mech]
    gas.TP = T_INDEX, reactor_pressure
    fuel = 
    oxidizer = 
    phi = 
    gas.set_equivalence_ratio(phi, fuel, oxidizer)
    r = ct.Reactor(contents=gas, name="Batch Reactor")
    reactor_network = ct.ReactorNet([r])
    
    objective_INDEX = []    
    
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
    objective_INDEX.append((((tau) - experimental_target)/(2*experimental_target))**2)
    fi = open("idt_objective_INDEX.txt", "a")
    fi.write('%s\n' % sum(objective_INDEX))
    fi.close()
    fi2 = open("idt_INDEX.txt", "a")
    fi2.write('%s, %s, %s\n' % ((1000/T_INDEX), experimental_target, tau))
    fi2.close()

def idt_calculate_objective_INDEX():
    objective_INDEX = []
    
    total = 0
    with open('idt_objective_INDEX.txt', 'r') as inp:
    	for line in inp:
           num = float(line)
           objective_INDEX.append(num)
    
    with open('idt_objective_INDEX.txt', 'w') as outp:
    # Write the updated lines to the file
    	outp.write('%s\n' % mean(objective_INDEX)) 
    
def idt_parallel_INDEX(mech, nProcs, T_INDEX, experimental_target):
    with multiprocessing.Pool(processes=nProcs, initializer=init_process, initargs=(mech,)) as pool:
        y = pool.map(ignition_delay_INDEX, zip(itertools.repeat(mech), T_INDEX, experimental_target))
    return y

t1 = time()

idt_parallel_INDEX(mechanism, nProcs, T_INDEX, experimental_target)

idt_calculate_objective_INDEX()

t2 = time()
print('Parallel: {0:.3f} seconds'.format(t2-t1))
