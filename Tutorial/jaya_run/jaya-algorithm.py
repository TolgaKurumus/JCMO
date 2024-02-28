import os
import random
import copy
import subprocess

def generate_random_variable_values(variable_ranges):
    variable_values = {}
    for var_name, (var_min, var_max) in variable_ranges.items():
        random_value = round(random.uniform(var_min, var_max), 3)
        variable_values[var_name] = random_value
    return variable_values

def create_run_folder(run_num, variable_values, initial_values):
    run_folder = f"run.{run_num}"
    os.makedirs(run_folder, exist_ok=True)
    
    cti_template_path = "templatedir/modified_reactions.cti"
    cti_content = None
    with open(cti_template_path, 'r') as template_file:
        cti_content = template_file.read()
        
    # Check if initial_values is provided and it's the first run
    if initial_values is not None and run_num == 1:
        # Set initial variable values for run.1
        for var_name, var_value in initial_values.items():
            cti_content = cti_content.replace(f"{{{var_name}}}", str(var_value))    
            
    for var_name, var_value in variable_values.items():
        cti_content = cti_content.replace(f"{{{var_name}}}", str(var_value))
    
    new_cti_path = os.path.join(run_folder, "mech_to_optimize.cti")
    with open(new_cti_path, 'w') as new_cti_file:
        new_cti_file.write(cti_content)
    
    idt_script_path = "casebase/Simulations.py"
    new_idt_script_path = os.path.join(run_folder, "Simulations.py")
    os.system(f"cp {idt_script_path} {new_idt_script_path}")
    

'''
def run_command_in_run_folder(run_folder):
    os.chdir(run_folder)
    subprocess.run(["python3", "Simulations.py.py"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    os.chdir("..")

'''
def run_command_in_run_folder(run_folder):
    os.chdir(run_folder)
    os.system("cti2yaml mech_to_optimize.cti")
    os.system("python3 Simulations.py")
    os.chdir("..")


def update_variables_jaya(variables, best_variables, worst_variables, run_num, num_runs, r_values, variable_ranges):
    updated_variables = copy.deepcopy(variables)
    random_values = {}  # Nested dictionary to store the random values
    
    for var_name, var_value in variables.items():
        if var_name != 'Objective':
            # Use the pre-generated r1 and r2 values
            r1 = r_values[var_name]['r1']
            r2 = r_values[var_name]['r2']
            
            # Read var_value from the variablesAndObjective.txt.run.{}
            variable_values_path = f"run.{run_num-num_runs}/variablesAndObjective.txt.run.{run_num-num_runs}"
            with open(variable_values_path, 'r') as variable_values_file:
                for line in variable_values_file:
                    parts = line.split(': ')
                    if len(parts) == 2 and parts[0] == var_name:
                        var_value = float(parts[1])
                        break
            
            equation_part1 = var_value
            equation_part2 = r1 * (best_variables[f'x{var_name[1:]}'] - abs(var_value))
            equation_part3 = r2 * (worst_variables[f'x{var_name[1:]}'] - abs(var_value))
            
            updated_value = equation_part1 + equation_part2 - equation_part3
                
            # Ensure the updated value stays within the specified range
            var_min, var_max = variable_ranges[var_name]
            updated_value = max(var_min, min(updated_value, var_max))
            
            updated_variables[var_name] = updated_value
            '''
            # Check if c{var_name[1:]} exists in variable_ranges
            if f'c{var_name[1:]}' in variable_ranges:
                c_var_name = f'c{var_name[1:]}'
                c_var_range = variable_ranges[c_var_name]
                coeff = 1 - ((updated_value - variable_ranges[f'x{var_name[1:]}'][0]) / (variable_ranges[f'x{var_name[1:]}'][1] - variable_ranges[f'x{var_name[1:]}'][0]))
                print(variable_ranges[f'x{var_name[1:]}'][0])
                c_var_value = c_var_range[1] + (c_var_range[0] - c_var_range[1])*coeff
                updated_variables[c_var_name] = c_var_value
            else:
                print(f'Warning: c{var_name[1:]} does not exist in variable_ranges.')    
            '''
            
    return updated_variables

def update_variables_jaya_next_step(variables, best_variables, worst_variables, folder_names, r_values, variable_ranges):
    updated_variables_by_folder = {}  # Dictionary to store updated variables for each folder
    
    for folder_name in folder_names:
        updated_variables = copy.deepcopy(variables)  # Initialize updated_variables for each folder
        variable_values_path = os.path.join(folder_name, f"variablesAndObjective.txt.{os.path.basename(folder_name)}")
        #print(f"Processing folder: {folder_name}, variable_values_path: {variable_values_path}")
        with open(variable_values_path, 'r') as variable_values_file:
            for line in variable_values_file:
                parts = line.split(': ')
                if len(parts) == 2 and parts[0] in variables:
                    var_name = parts[0]
                    var_value = float(parts[1])
                    
                    if var_name != 'Objective':
                        r1 = r_values[var_name]['r1']
                        r2 = r_values[var_name]['r2']

                        equation_part1 = var_value
                        equation_part2 = r1 * (best_variables[f'x{var_name[1:]}'] - abs(var_value))
                        equation_part3 = r2 * (worst_variables[f'x{var_name[1:]}'] - abs(var_value))

                        updated_value = equation_part1 + equation_part2 - equation_part3

                        # Ensure the updated value stays within the specified range
                        var_min, var_max = variable_ranges[var_name]
                        updated_value = max(var_min, min(updated_value, var_max))
                        updated_variables[var_name] = updated_value
                        '''
                        print(f"{var_name}:")
                        print(f"var_value: {var_value}")
                        print(f"  best_variables[x{var_name[1:]}]: {best_variables[f'x{var_name[1:]}']}")
                        print(f"  worst_variables[x{var_name[1:]}]: {worst_variables[f'x{var_name[1:]}']}")
                        print(f"  r1: {r1}")
                        print(f"  r2: {r2}")
                        print(f"  Equation Part 1: {equation_part1}")
                        print(f"  Equation Part 2: {equation_part2}")
                        print(f"  Equation Part 3: {equation_part3}")
                        print(f"  Updated Value: {updated_value}")
                        '''
        updated_variables_by_folder[folder_name] = updated_variables
    
    return updated_variables_by_folder

def write_variables_and_objective(run_folder, variables, r1, r2, label=None):
    variable_values_path = os.path.join(run_folder, f"variablesAndObjective.txt.{os.path.basename(run_folder)}")
    with open(variable_values_path, 'w') as variable_values_file:
        for var_name, var_value in variables.items():
            variable_values_file.write(f"{var_name}: {var_value}\n")
        if 'Objective' in variables:
            variable_values_file.write(f"Objective: {variables['Objective']}\n")
        variable_values_file.write(f"r1: {r1}\n")
        variable_values_file.write(f"r2: {r2}\n")
        if label is not None:
            variable_values_file.write(f"Label: {label}\n")

def generate_r_values(variable_ranges):
    r_values = {}
    for var_name in variable_ranges:
        r_values[var_name] = {
            'r1': round(random.uniform(0.01, 0.99), 2),
            'r2': round(random.uniform(0.01, 0.99), 2)
        }
    return r_values

def main():
    initial_values = {
        'x1'	:	(1.000000e+14),
        'x2'	:	(2.200000e+08),
        'x3'	:	(2.600000e+11),
        'x4'	:	(1.600000e+14),
        'x5'	:	(1.900000e+27),
        'x6'	:	(6.400000e+05),
        'x7'	:	(1.000000e+13),
        'x8'	:	(2.400000e+13),
        'x9'	:	(1.700000e+08),
        'x10'	:	(3.300000e+08),
        'x11'	:	(1.100000e+14),
        'x12'	:	(2.500000e+14),
        'x13'	:	(5.600000e+00),
        'x14'	:	(2.600000e+11),
        'x15'	:	(4.300000e+14),
        'x16'	:	(4.300000e+10),
        'x17'	:	(2.000000e+06)
    }

    
    variable_ranges = {
        'x1'	:	(74131024130091.8, 134896288259165.0),
        'x2'	:	(145352558.561671, 332983474.655966),
        'x3'	:	(121611136734.672, 555870143270.58),
        'x4'	:	(11327132550146.2, 2260060071396410.0),
        'x5'	:	(9.52255743891818e+24, 3.79099839844087e+29),
        'x6'	:	(3207.59829521454, 127696788.158008),
        'x7'	:	(50118723362.7273, 1995262314968880.0),
        'x8'	:	(14132247728534.1, 40757847659081.9),
        'x9'	:	(852018.297166363, 33919459354.4709),
        'x10'	:	(1653917.87097, 65843656393.973),
        'x11'	:	(551305956990.0, 2.19478854646577e+16),
        'x12'	:	(1252968084068.18, 4.9881557874222e+16),
        'x13'	:	(5.0, 1117.34689638257),
        'x14'	:	(18406590393.9876, 3672597616019.16),
        'x15'	:	(2155105104597.27, 8.57962795436618e+16),
        'x16'	:	(25320277180.2903, 73024477055.855),
        'x17'	:	(240452.886923483, 16635275.4220534)
    }

    
    num_runs = 6 #len(variable_ranges)  # Change this to the desired number of run folders  
    num_of_sets = num_runs * 1000  # Total number of sets to generate
    
    objective_values_by_case = {}  
    # Create a dictionary to store objective values for each group
    objective_values_by_group = {}
    
    # Create a dictionary to store variable values for each run folder
    variable_values_by_run = {}    
    
    # Part 1: Create initial set of folders and calculate objectives
    for run_num in range(1, num_runs + 1):
        variable_values = generate_random_variable_values(variable_ranges)
        create_run_folder(run_num, variable_values, initial_values)      
        run_folder = f"run.{run_num}"
        run_command_in_run_folder(run_folder)      
        # Read the objective value from the objective.txt file
        objective_path = os.path.join(run_folder, "objective.txt")
        with open(objective_path, 'r') as objective_file:
            objective_number = float(objective_file.read())      
        # Store the variable values along with their objective number
        variable_values['Objective'] = objective_number
        objective_values_by_case[run_folder] = variable_values 
        write_variables_and_objective(run_folder, variable_values, 0, 0)  # Call the function here
        # Store variable values in the dictionary
        variable_values_by_run[run_folder] = variable_values

    # Find the num_runs groups with the lowest objectives
    best_group_nums = sorted(
        range(1, num_runs + 1),
        key=lambda group_num: objective_values_by_case[f"run.{group_num}"]["Objective"]
    )[:num_runs]
        
    # Find best and worst variables
    best_case = min(objective_values_by_case, key=lambda k: objective_values_by_case[k]['Objective'])
    worst_case = max(objective_values_by_case, key=lambda k: objective_values_by_case[k]['Objective'])
    best_variables = objective_values_by_case[best_case]
    worst_variables = objective_values_by_case[worst_case]

    # Label the files as best and worst
    for run_folder, variables in objective_values_by_case.items():
        label = None
        if run_folder == best_case:
            label = "Best"
        elif run_folder == worst_case:
            label = "Worst"
        write_variables_and_objective(run_folder, variables, 0, 0, label)  # Call the function here
    
    # Part 2: Create new set of folders using JAYA algorithm
    for run_num in range(num_runs + 1, num_runs * 2 + 1):
        # Check if it's time to regenerate r_values
        if (run_num - 1) % num_runs == 0:
            r_values = generate_r_values(variable_ranges)

        # Update variables using JAYA algorithm
        new_variables = update_variables_jaya(
            best_variables, best_variables, worst_variables, run_num, num_runs, r_values, variable_ranges
        )

        # Create new folder and save new variables
        new_run_folder = f"run.{run_num}"
        create_run_folder(run_num, new_variables, initial_values)
        write_variables_and_objective(new_run_folder, new_variables, 0, 0)  # Call the function here

        # Run calculations in the new folder
        run_command_in_run_folder(new_run_folder)

        # Read the new objective value from the objective.txt file
        new_objective_path = os.path.join(new_run_folder, "objective.txt")
        with open(new_objective_path, 'r') as new_objective_file:
            new_objective_number = float(new_objective_file.read())

        # Store the variable values along with their new objective number
        new_variables['Objective'] = new_objective_number
        variable_values_by_run[new_run_folder] = new_variables

        # Write the updated variable values back to the variablesAndObjective.txt file
        write_variables_and_objective(new_run_folder, new_variables, 0, 0)  # Call the function here

        # Update objectives_part1 here
        objectives_part1 = []
        
        # Initial number of sets generated
    sets_generated = num_runs
        
    # Part 3: Print objectives from last 2 sets of run folders
    objectives_part2 = []  
    objectives_old = []
    combined_objectives = []
    # Iteration loop for generating more sets
    while sets_generated < num_of_sets:
        sets_generated += num_runs  # Increment the count

        objectives_old = combined_objectives[:num_runs]
        
        objectives_part2 = []  
        
        print(f"Objective old: {objectives_old}\n")
        
        for run_num in range(sets_generated - 2 * num_runs + 1, sets_generated + 1):
            if run_num <= 0:
                continue  # Skip negative run numbers
            folder_name = f"run.{run_num}"
            objective_path = os.path.join(folder_name, "objective.txt")
            with open(objective_path, 'r') as objective_file:
                objective_number = float(objective_file.read())
            objectives_part2.append((folder_name, objective_number))
            
        objectives_part2.sort(key=lambda x: x[1])
        
        # Combine objectives_part2 and objectives_old while removing duplicates
        combined_objectives = list(set(objectives_part2 + objectives_old))
        
        # Sort all folders by objective
        combined_objectives.sort(key=lambda x: x[1])
        print(f"Objective combined: {combined_objectives}\n")
        
        for i, (folder_name, objective) in enumerate(combined_objectives, start=1):
            print(f"{i}. {folder_name} -> Objective: {objective:.3f}")

        # Select the top N folders with the smallest objectives
        top_best_folders = combined_objectives[:num_runs]
        
        # Update best and worst objectives based on top best folders
        new_best_objective = min(top_best_folders, key=lambda x: x[1])[1]
        new_worst_objective = max(top_best_folders, key=lambda x: x[1])[1]

        # Update best and worst variables based on top best folders
        new_best_variables = None
        new_worst_variables = None

        

        for i, (folder_name, objective) in enumerate(top_best_folders, start=1):
            variables_path = os.path.join(folder_name, f"variablesAndObjective.txt.{os.path.basename(folder_name)}")
            with open(variables_path, 'r') as variables_file:
                lines = variables_file.readlines()
                if i == 1:
                    new_best_variables = {
                        line.split(': ')[0]: float(line.split(': ')[1])
                        for line in lines if line.startswith('x')
                    }
                new_worst_variables = {
                    line.split(': ')[0]: float(line.split(': ')[1])
                    for line in lines if line.startswith('x')
                }

        #print("\nPart 4: Creating new set of folders using lowest objectives from Part 2")
        
        # List of folder names for which to update variables
        folders_to_update = [folder_name for folder_name, _ in top_best_folders]
        
        # Update best and worst objectives based on top best folders
        new_best_objective = min(top_best_folders, key=lambda x: x[1])[1]
        new_worst_objective = max(top_best_folders, key=lambda x: x[1])[1]
        
        #print(f"New best objective: {new_best_objective}")
        #print(f"New worst objective: {new_worst_objective}")
        #print(f"New best var: {new_best_variables}")
        #print(top_best_folders)
        print(folders_to_update)
        # Part 5: Create new set of folders using JAYA algorithm with updated variables
        r_values = generate_r_values(variable_ranges)
        updated_variables_by_folder = update_variables_jaya_next_step(
            new_best_variables, new_best_variables, new_worst_variables, folders_to_update, r_values, variable_ranges
        )
        
        updated_folders_and_variables = list(updated_variables_by_folder.items())[:num_runs]


        for run_num, (folder_name, new_variables) in enumerate(updated_folders_and_variables, start=sets_generated + 1):
            # Create new folder and save new variables
            new_run_folder = f"run.{run_num}"
            create_run_folder(run_num, new_variables, initial_values)
            write_variables_and_objective(new_run_folder, new_variables, 0, 0)
            
            # Run calculations in the new folder
            run_command_in_run_folder(new_run_folder)

            # Read the new objective value from the objective.txt file
            new_objective_path = os.path.join(new_run_folder, "objective.txt")
            with open(new_objective_path, 'r') as new_objective_file:
                new_objective_number = float(new_objective_file.read())

            # Store the variable values along with their new objective number
            new_variables['Objective'] = new_objective_number
            variable_values_by_run[new_run_folder] = new_variables

            # Write the updated variable values back to the variablesAndObjective.txt file
            write_variables_and_objective(new_run_folder, new_variables, 0, 0)  # Call the function here
        
if __name__ == "__main__":
    main()

