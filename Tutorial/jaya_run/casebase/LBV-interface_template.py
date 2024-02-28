
target_file = 
# Read the data from the CSV file
data = np.genfromtxt(target_file, delimiter=",", skip_header=1)

# Extract the T and experimental_target values
phi_INDEX = data[:, 0]
experimental_target = data[:, 1]


def burning_velocity_INDEX(args):
    mech, phi_INDEX, experimentValuesLBV = args
    gas = gases[mech]
    initial_grid = np.linspace(0.0, 0.05, 100)
    pres = 
    P = ct.one_atm * pres
    T = 
    fuel = 
    oxidizer = 
    vels = []
    objLBV = []
    gas.TP = T, P
    gas.set_equivalence_ratio(phi_INDEX, fuel, oxidizer)
    f = ct.FreeFlame(gas, initial_grid)
    f.transport_model = "mixture-averaged" # Mix-Multi-UnityLewis
    f.set_refine_criteria(ratio=3.0, slope=0.1, curve=0.2)
    f.set_grid_min(1e-10)
    f.solve(loglevel=0, refine_grid=True, auto=True)
    vels = f.velocity[0]*100
    objLBV.append(((((vels) - experimentValuesLBV)/(2*experimentValuesLBV)))**2)
    fi = open("lbv_objective_INDEX.txt", "a")
    fi.write('%s\n' % sum(objLBV))
    fi.close() 
    fi2 = open("lbv_INDEX.txt", "a")
    fi2.write('%s, %s, %s\n' % (phi_INDEX, experimentValuesLBV, vels))
    fi2.close()

def lbv_calculate_objective_INDEX():
    objective_INDEX = []
    
    total = 0
    with open('lbv_objective_INDEX.txt', 'r') as inp:
    	for line in inp:
           num = float(line)
           objective_INDEX.append(num)
    
    with open('lbv_objective_INDEX.txt', 'w') as outp:
    # Write the updated lines to the file
    	outp.write('%s\n' % mean(objective_INDEX)) 
    
def lbv_parallel_INDEX(mech, nProcs, phi_INDEX, experimental_target):
    with multiprocessing.Pool(processes=nProcs, initializer=init_process, initargs=(mech,)) as pool:
        y = pool.map(burning_velocity_INDEX, zip(itertools.repeat(mech), phi_INDEX, experimental_target))
    return y  
    
t1 = time()

lbv_parallel_INDEX(mechanism, nProcs, phi_INDEX, experimental_target)

lbv_calculate_objective_INDEX()

t2 = time()
print('Parallel: {0:.3f} seconds'.format(t2-t1))
