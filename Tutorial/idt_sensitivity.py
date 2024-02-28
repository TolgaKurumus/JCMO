#import sys
import numpy as np
import pandas as pd
import cantera as ct
import matplotlib.pyplot as plt
import timeit

def ign_uq(g, factor, temp, pres, fuel, phi, T_equi, simtype='UV', bootplot=False):
	gas.set_multiplier(1.0) # reset all multipliers
	for i in range(gas.n_reactions):
		gas.set_multiplier(factor[i],i)
		# print(gas.reaction_equation(i)+' index_reaction:',i,'multi_factor:',factor[i])
	
	gas.set_equivalence_ratio( phi, fuel, oxidizer)
	gas.TP = temp, pres*ct.one_atm

	# here it is constant volume with IdealGasReactor
	if simtype == 'UV':
		r = ct.IdealGasReactor(gas)
	else:
		r = ct.IdealGasConstPressureReactor(gas)

	sim = ct.ReactorNet([r])
	
	# set the tolerances for the solution and for the sensitivity coefficients
	sim.rtol = 1.0e-6
	sim.atol = 1.0e-15

	t_end = 10;
	time = []
	temperature = []
	states = ct.SolutionArray(gas, extra=['t'])

	# stateArray = []
	while sim.time < t_end and r.T < T_equi - 0.1:
		sim.step()
		time.append(sim.time)
		temperature.append(r.T)
		states.append(r.thermo.state, t=sim.time)
		# stateArray.append(r.thermo.X)

	time = np.array(time)
	temperature = np.array(temperature)
	diff_temperature = np.diff(temperature)/np.diff(time)

	if 0:
		# print(r.T, T_equi)
		plt.figure()
		plt.plot(states.t, states.T, '-ok')

		# plt.plot( 1.0, states.T[ign_pos], 'rs',markersize=6  )
		plt.xlabel('Time [ms]')
		plt.ylabel('T [K]')
		# plt.xlim( 0.99, 1.01 )
		#plt.ylim( -0.001,0.001 )
		plt.tight_layout()
		plt.show()

	ign_pos = np.argmax( diff_temperature )

	ign = time[ign_pos]
	
	gas.set_multiplier(1.0) # reset all multipliers

	return ign
    
###########################################################################################
pres = 
temp = 
phi = 
simtype = 'UV'

fuel = 
oxidizer = 
#fuel = 'IC8H18:1'
mech = 
dk = 1

# mech = 'h2_li_19.xml'
# fuel = 'nc7h16'
# mech = 'nc7sk88.cti'
# gas = ct.Solution('mech/dme_sk39.cti')
# gas = ct.Solution('mech/ic8sk143.cti')
# mech = "c4_49.xml"

string_list = [fuel, mech, str(phi), str(pres), str(temp), str(dk), simtype]
string_list = '_'.join(string_list)
print(string_list)

#ct.add_directory('/u/41/bhattaa7/unix/Desktop/sensi/')
mechfile = mech
gas = ct.Solution(mechfile)
print('number of species: {:.3e} and number of reactions {:.3e}'.format(gas.n_total_species,gas.n_reactions))
gas.set_equivalence_ratio( phi, fuel, oxidizer)
#gas.set_equivalence_ratio(phi,'IC8H18:0.164298161, NC7H16:0.086028143,	C7H8:0.249673696, DMF25:0.375, CH3OCH3:0.125', 'O2:1.0, N2:3.76')
gas.TP = temp, pres*ct.one_atm

# print('species_names:')
# print(gas.species_names)
# print(gas.species_index('OH'))

# Get equilibrium temperature for ignition break
gas.equilibrate(simtype)
T_equi = gas.T

m = gas.n_reactions

# Create a dataframe to store sensitivity-analysis data
ds = pd.DataFrame(data=[], index=gas.reaction_equations(range(m)))
pd.options.display.float_format = '{:,.2e}'.format

# Create an empty column to store the sensitivities data. 
# baseCase for brute force method
ds["index"] = ""
ds["bruteforce"] = ""
#ds["adjoint"] = ""
#ds["ratio"] = ""

factor = np.ones( gas.n_reactions )
ign0 = ign_uq(gas, factor, temp, pres, fuel, phi, T_equi, simtype, False)
print("Ignition Delay is: {:.4f} ms".format(ign0*1000))

print('Start Brute Force')

for i in range(m):
    factor[i] = 1+dk
    ign = ign_uq(gas, factor, temp, pres, fuel, phi, T_equi, simtype, False)
    factor[i] = 1.0
#    ds["bruteforce"][i] = (ign-ign0)/(ign0*dk)
    ds["bruteforce"][i] = (ign-ign0)/(ign0)

#elapsed = timeit.default_timer() - start_time
print('Finish Brute Force')

for i in range(m):
    ds['index'][i] = i
    
pd.DataFrame(ds).to_csv("brute_force.csv")
