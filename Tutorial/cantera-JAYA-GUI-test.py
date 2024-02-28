import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, filedialog
import subprocess
import os
import re
import pandas as pd
from tkinter import IntVar, Radiobutton
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from PIL import Image, ImageTk
import numpy as np
import shutil
import glob

output_file = 'jaya_run/templatedir/modified_reactions.cti'
brute_force_file = 'brute_force.csv'

# Global arrays for x_values and descriptors
descriptors = []
initial_values = []

# Delete the output file if it already exists
if os.path.isfile(output_file):
    os.remove(output_file)

# Create the main window

window = tk.Tk()

# Set the window title
window.title("Chemical Kinetic Mechanism Optimizer")

# Create a label for the input file
label_input_file = tk.Label(window, text="Select the mechanism:", bg="lightblue")
label_input_file.grid(row=1, column=0, padx=10, pady=10)

# Create an entry widget to display the selected input file
entry_input_file = tk.Entry(window, width=40)
entry_input_file.grid(row=1, column=1, padx=10, pady=10)

# Create a browse button to select the input file
def browse_input_file():
    global input_file  # Access the global variable
    file_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select the mechanism:", filetypes=(("CTI files", "*.cti"),))
    if file_path:
        input_file = file_path  # Update the global variable
        entry_input_file.delete(0, tk.END)  # Clear the current entry
        entry_input_file.insert(0, input_file)  # Set the selected file path
    target_folder = os.path.join("jaya_run", "casebase")
    new_file_name = "mech_to_optimize.cti"
    new_file_path = os.path.join(target_folder, new_file_name)
    shutil.copy(input_file, new_file_path)
    idt_list_button.config(state="normal")
    button_prompt_csv.config(state="normal")
    button_analysis.config(state="normal")
    
browse_button = tk.Button(window, text="Browse", command=browse_input_file)
browse_button.grid(row=1, column=2, padx=10, pady=10)

def detect_reaction_type(input_file, target_reaction_number):
    # Read the content of the CTI file
    with open(input_file, 'r') as file:
        content = file.read()

    # Define the pattern to match the target reaction
    pattern = rf"(?im)^# Reaction {target_reaction_number}\b.*?\n([a-zA-Z_]+_reaction)\("

    # Find the matching reaction type
    match = re.search(pattern, content)
    if match:
        reaction_type = match.group(1)
    else:
        # Check for additional reaction types
        if re.search(rf"(?im)^# Reaction {target_reaction_number}\b.*?\n(reaction)\(", content):
            reaction_type = 'regular'
        elif re.search(rf"(?im)^# Reaction {target_reaction_number}\b.*?\n(pdep_arrhenius)\(", content):
            reaction_type = 'pdep_arrhenius'
        else:
            reaction_type = 'unknown'
            print("Reaction type is unknown, please check the syntax.")
    return reaction_type

# Global counter variable
x_counter = 0

def get_x_counter():
    """Increment the global counter variable and return its value."""
    global x_counter
    x_counter += 1
    return x_counter

def regular_reaction(input_file, output_file, target_reaction_number_regular):
    global x_counter, descriptors, initial_values
    
    # Read the input .cti file
    if os.path.isfile(output_file):
        with open(output_file, 'r+') as file:
            content = file.read()
    else:
        with open(input_file, 'r') as file:
            content = file.read()

    # Define the pattern to match the target reaction
    pattern = rf"(?im)^# Reaction {target_reaction_number_regular}\s*\n\s*reaction\s*\('.*'\s*,\s*\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"

    detectReaction = rf"(?im)^# Reaction {target_reaction_number_regular}\s*\n\s*reaction\s*\('([^']+)'\s*,\s*\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"
    match = re.search(detectReaction, content)
    reaction = match.group(1)

    #initial_values.append(match.group(2))
    #initial_values.append(match.group(3))
    #initial_values.append(match.group(4))
    
    x1 = f"{{x{get_x_counter()}}}"
    descriptors.append(x1.strip("{}"))
    #x2 = f"{{x{get_x_counter()}}}"
    #descriptors.append(x2.strip("{}"))
    #x3 = f"{{x{get_x_counter()}}}"
    #descriptors.append(x3.strip("{}"))

    # Find the target reaction and replace the rate coefficients with placeholders
    modified_content = re.sub(pattern,
                              rf"# Reaction {target_reaction_number_regular}\n"
                              rf"reaction('{reaction}', [{x1}, \2, \3]",
                              content)
         
    if modified_content == content:
        print(f"Warning: Target reaction pattern not found for reaction {target_reaction_number}.")       
    else:
        with open(output_file, "w") as file:
            file.write(modified_content)
        print("Modified reactions saved to", output_file)
        idt_num_configs["state"] = "normal"
        lbv_num_configs["state"] = "normal"
        button_set_configs["state"] = "normal"
        
def three_body_reaction(input_file, output_file, target_reaction_number, var_values_for_selected_reaction, three_body_initial_values_storage):

    global x_counter, descriptors, initial_values
    
    # Read the input .cti file
    if os.path.isfile(output_file):
       with open(output_file, 'r+') as file:
        content = file.read()
    else:
       with open(input_file, 'r') as file:
        content = file.read()
    # Define the pattern to match the target reaction
    pattern = rf"(?im)^# Reaction {target_reaction_number}\s*\n\s*three_body_reaction\s*\('.*'\s*,\s*\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"

    detectReaction = rf"(?im)^# Reaction {target_reaction_number}\s*\n\s*three_body_reaction\s*\('([^']+)'\s*,\s*\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"
    match = re.search(detectReaction, content)
    reaction = match.group(1)

    #initial_values.append(match.group(2))
    #initial_values.append(match.group(3))
    #initial_values.append(match.group(4))
    
    # Define the placeholder values
    x1 = f"{{x{get_x_counter()}}}"
    descriptors.append(x1.strip("{}"))
    #x2 = f"{{x{get_x_counter()}}}"
    #descriptors.append(x2.strip("{}"))
    #x3 = f"{{x{get_x_counter()}}}"
    #descriptors.append(x3.strip("{}"))
    # Find the target reaction and replace the three-body rate with placeholders
    modified_content = re.sub(pattern,
                              rf"# Reaction {target_reaction_number}\n"
                              rf"three_body_reaction('{reaction}', [{x1}, \2, \3]",
                              content)
          
    if modified_content == content:
        print(f"Warning: Target reaction pattern not found for reaction {target_reaction_number}.")
    else:
        with open(output_file, 'w') as file:
            file.write(modified_content)
        print("Modified reactions saved to", output_file)
        idt_num_configs["state"] = "normal"
        lbv_num_configs["state"] = "normal"
        button_set_configs["state"] = "normal"
        
def falloff_reaction(input_file, output_file, target_reaction_number_falloff, var_values_for_selected_reaction):

    global x_counter, descriptors, initial_values
    
    # Read the input .cti file
    if os.path.isfile(output_file):
       with open(output_file, 'r+') as file:
        content = file.read()
    else:
       with open(input_file, 'r') as file:
        content = file.read()

    # Define the pattern to match the target reaction
    pattern = rf"(?im)^# Reaction {target_reaction_number_falloff}\s*\n\s*falloff_reaction\s*\('.*'\s*,\s*kf=\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]\s*,\s*kf0=\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]\s*"

    detectReaction = rf"(?im)^# Reaction {target_reaction_number_falloff}\s*\n\s*falloff_reaction\s*\('([^']+)'\s*,\s*kf=\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]\s*,\s*kf0=\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"

    match = re.search(detectReaction, content)
    reaction = match.group(1)

    #initial_values.append(match.group(2))
    #initial_values.append(match.group(3))
    #initial_values.append(match.group(4))
    #initial_values.append(match.group(5))
    #initial_values.append(match.group(6))
    #initial_values.append(match.group(7))

    x1 = f"{{x{get_x_counter()}}}"
    descriptors.append(x1.strip("{}"))
    #x2 = f"{{x{get_x_counter()}}}"
    #descriptors.append(x2.strip("{}"))
    #x3 = f"{{x{get_x_counter()}}}"
    #descriptors.append(x3.strip("{}"))
    #x4 = f'{{x{get_x_counter()}}}'
    #descriptors.append(x4.strip("{}"))
    #x5 = f'{{x{get_x_counter()}}}'
    #descriptors.append(x5.strip("{}"))
    #x6 = f'{{x{get_x_counter()}}}'
    #descriptors.append(x6.strip("{}"))
    # Find the target reaction and replace kf and kf0 values with placeholders
    modified_content = re.sub(pattern,
                              rf"# Reaction {target_reaction_number_falloff}\n"
                              rf"falloff_reaction('{reaction}',\n"
                              rf"                 kf=[{x1}, \2, \3],\n"
                              rf"                 kf0=[\4, \5, \6]",
                              content)
           
    if modified_content == content:
        print(f"Warning: Target reaction pattern not found for reaction {target_reaction_number_falloff}.")
    else:
        with open(output_file, 'w') as file:
            file.write(modified_content)
        print("Modified reactions saved to", output_file)
        idt_num_configs["state"] = "normal"
        lbv_num_configs["state"] = "normal"
        button_set_configs["state"] = "normal"

def pdep_arrhenius(input_file, output_file, target_reaction_number_pdep, var_values_for_selected_reaction, pdep_initial_values_storage):
    global x_counter, descriptors, initial_values

    # Read the content of the CTI file
    with open(output_file if os.path.isfile(output_file) else input_file, 'r') as file:
        content = file.read()

    # Define the pattern to match the reactions range
    pattern = rf"(?im)^# Reaction {target_reaction_number_pdep}\b.*?^# Reaction {target_reaction_number_pdep + 1}\b"
    match = re.search(pattern, content, flags=re.DOTALL)
    num_occurrences = len(re.findall(r"\[\(", match.group(0))) if match else content[content.find(f"# Reaction {target_reaction_number_pdep}"):].count("[(")

    # Detect the reaction
    detectReaction = rf"(?im)^# Reaction {target_reaction_number_pdep}\s*\n\s*pdep_arrhenius\s*\('([^']+)'\s*,(\n.*){{{num_occurrences}}}"
    match = re.search(detectReaction, content, flags=re.IGNORECASE)
    reaction = match.group(0)

    # Extract the pressure values
    pressureValues = [float(value) for value in re.findall(r"\(\s*([\d.e+-]+),\s*'atm'\)", reaction)]
    
    # Prepare replacements and a temporary list for selected values
    replacements = []
    selected_values = []

    for counter, value in enumerate(pressureValues):
        if var_values_for_selected_reaction[counter]:
            replacements.append(
                (
                    rf"\(\s*({value}),\s*'atm'\),\s*([\d.e+-]+),\s*([\d.e+-]+),\s*([\d.e+-]+)",
                    lambda m, pv_value=value, xc1=get_x_counter(): (
                        selected_values.append(float(m.group(2))),
                        f"({pv_value}, 'atm'), {{x{xc1}}}, {m.group(3)}, {m.group(4)}",
                        descriptors.append(f"x{xc1}")
                    )[1]
                )
            )

    # Apply replacements
    for old, new_func in replacements:
        reaction = re.sub(old, lambda m, f=new_func: f(m), reaction, flags=re.IGNORECASE)

    # Create a dictionary to store selected values for each reaction number
    selected_values_storage = {}
    if target_reaction_number_pdep in pdep_initial_values_storage:
        selected_values_storage[target_reaction_number_pdep] = selected_values

    # Update initial_values based on selected_values_storage
    for reaction_number, selected_values in selected_values_storage.items():
        if reaction_number in pdep_initial_values_storage:
            pdep_values = pdep_initial_values_storage[reaction_number]
            start_index = next((i for i, v in enumerate(initial_values) if v in pdep_values), None)

            if start_index is not None:
                for i, selected_value in enumerate(selected_values):
                    initial_values[start_index + i] = selected_value

                # Remove any remaining pdep values that were not replaced
                end_index = start_index + len(pdep_values)
                initial_values = initial_values[:start_index + len(selected_values)] + initial_values[end_index:]

    # Update the content with the modified reaction
    modified_content = re.sub(detectReaction, reaction, content)

    # Write back the modified content
    with open(output_file, 'w') as file:
        file.write(modified_content)

    # Extract the reaction name
    detectReactionName = rf"(?im)^# Reaction {target_reaction_number_pdep}\s*\n\s*pdep_arrhenius\s*\('([^']+)'\s*,"
    reaction_name = re.search(detectReactionName, content, flags=re.IGNORECASE).group(1) if re.search(detectReactionName, content, flags=re.IGNORECASE) else None

    idt_num_configs["state"] = "normal"
    lbv_num_configs["state"] = "normal"
    button_set_configs["state"] = "normal"
    
    return reaction_name, num_occurrences, pressureValues, selected_values_storage

  
def initial_values_regular_reaction(input_file, output_file, target_reaction_number_regular, regular_initial_values_storage):
    global x_counter, descriptors, initial_values, regular_initial_values
    regular_initial_values = {}
    
    # Read the input .cti file
    if os.path.isfile(output_file):
        with open(output_file, 'r+') as file:
            content = file.read()
    else:
        with open(input_file, 'r') as file:
            content = file.read()

    # Define the pattern to match the target reaction
    pattern = rf"(?im)^# Reaction {target_reaction_number_regular}\s*\n\s*reaction\s*\('.*'\s*,\s*\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"

    detectReaction = rf"(?im)^# Reaction {target_reaction_number_regular}\s*\n\s*reaction\s*\('([^']+)'\s*,\s*\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"
    match = re.search(detectReaction, content)
    reaction = match.group(1)

    initial_values.append(match.group(2))
    
    # Extract the reaction name
    detectReactionName = rf"(?im)^# Reaction {target_reaction_number_regular}\s*\n\s*reaction\s*\('([^']+)'\s*,\s*\[([\d.e+-]+)\s*"
    match = re.search(detectReactionName, content, flags=re.IGNORECASE)
    if match:
        reaction_name = match.group(1)
    else:
        reaction_name = None
        
    temp_initial_values = []
    # Store the initial values in the storage dictionary
    regular_initial_values_storage[target_reaction_number_regular] = temp_initial_values 
    regular_initial_values = regular_initial_values_storage
    
    return reaction_name     
      
def initial_values_three_body_reaction(input_file, output_file, target_reaction_number_three_body, three_body_initial_values_storage):

    global x_counter, descriptors, initial_values, three_body_initial_values
    three_body_initial_values = {}
    
    # Read the input .cti file
    if os.path.isfile(output_file):
       with open(output_file, 'r+') as file:
        content = file.read()
    else:
       with open(input_file, 'r') as file:
        content = file.read()
    # Define the pattern to match the target reaction
    pattern = rf"(?im)^# Reaction {target_reaction_number_three_body}\s*\n\s*three_body_reaction\s*\('.*'\s*,\s*\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"

    detectReaction = rf"(?im)^# Reaction {target_reaction_number_three_body}\s*\n\s*three_body_reaction\s*\('([^']+)'\s*,\s*\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"
    match = re.search(detectReaction, content)
    reaction = match.group(1)

    initial_values.append(match.group(2))
    
    # Extract the reaction name
    detectReactionName = rf"(?im)^# Reaction {target_reaction_number_three_body}\s*\n\s*three_body_reaction\s*\('([^']+)'\s*"
    match = re.search(detectReactionName, content, flags=re.IGNORECASE)
    if match:
        reaction_name = match.group(1)
    else:
        reaction_name = None
        
    temp_initial_values = []
    # Store the initial values in the storage dictionary
    three_body_initial_values_storage[target_reaction_number_three_body] = temp_initial_values 
    three_body_initial_values = three_body_initial_values_storage
    
    return reaction_name    
    
def initial_values_falloff_reaction(input_file, output_file, target_reaction_number_falloff, falloff_initial_values_storage):
    global x_counter, descriptors, initial_values, falloff_initial_values
    falloff_initial_values = {}
    if os.path.isfile(output_file):
        with open(output_file, 'r+') as file:
         content = file.read()
    else:
        with open(input_file, 'r') as file:
         content = file.read()
    # Define the pattern to match the target reaction
    pattern = rf"(?im)^# Reaction {target_reaction_number_falloff}\s*\n\s*falloff_reaction\s*\('.*'\s*,\s*kf=\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]\s*,\s*kf0=\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]\s*"
    detectReaction = rf"(?im)^# Reaction {target_reaction_number_falloff}\s*\n\s*falloff_reaction\s*\('([^']+)'\s*,\s*kf=\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]\s*,\s*kf0=\[([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*,\s*([\d.e+-]+)\s*\]"
    match = re.search(detectReaction, content)
    reaction = match.group(1)
    initial_values.append(match.group(2))
    temp_initial_values = []
    # Store the initial values in the storage dictionary
    falloff_initial_values_storage[target_reaction_number_falloff] = temp_initial_values 
    falloff_initial_values = falloff_initial_values_storage
    
      
def initial_values_pdep_arrhenius(input_file, output_file, target_reaction_number_pdep, pdep_initial_values_storage):
    global x_counter, descriptors, initial_values, pdep_initial_values
    pdep_initial_values = {}
    # Read the content of the CTI file
    if os.path.isfile(output_file):
        with open(output_file, 'r+') as file:
            content = file.read()
    else:
        with open(input_file, 'r') as file:
            content = file.read()

    # Define the pattern to match the reactions range
    pattern = rf"(?im)^# Reaction {target_reaction_number_pdep}\b.*?^# Reaction {target_reaction_number_pdep + 1}\b"
    
    # Find the matching range of reactions
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        reactions_range = match.group(0)
        num_occurrences = len(re.findall(r"\[\(", reactions_range))
    else:
        start_index = content.find(f"# Reaction {target_reaction_number_pdep}")
        remaining_content = content[start_index:]
        num_occurrences = remaining_content.count("[(")
    
    detectReaction = rf"(?im)^# Reaction {target_reaction_number_pdep}\s*\n\s*pdep_arrhenius\s*\('([^']+)'\s*,(\n.*){{{num_occurrences}}}"

    match = re.search(detectReaction, content, flags=re.IGNORECASE)
    reaction = match.group(0)
    # Extract the values using regular expressions
    pressureValues = re.findall(r"\(\s*([\d.e+-]+),\s*'atm'\)", reaction)

    pv = []

    # Print the extracted values
    for value in pressureValues:
        pv.append(float(value))

    replacements = []
    temp_initial_values = []
    current_x_counter = x_counter
    for counter, value in enumerate(pressureValues):
        replacements.append(
            (
                rf"\(\s*({value}),\s*'atm'\),\s*([\d.e+-]+),\s*([\d.e+-]+),\s*([\d.e+-]+)",
                lambda m, pv_value=value, xc1=get_x_counter(): (
                    initial_values.append(float(m.group(2))),
                    temp_initial_values.append(float(m.group(2))),
                    f"({pv_value}, 'atm'), {{x{xc1}}}, {m.group(3)}, {m.group(4)}"
                )[1]
            )
        )  

    for old, new_func in replacements:
        reaction = re.sub(old, lambda m, f=new_func: f(m), reaction, flags=re.IGNORECASE)
    x_counter = (current_x_counter + x_counter) - x_counter
    # Extract the reaction name
    detectReactionName = rf"(?im)^# Reaction {target_reaction_number_pdep}\s*\n\s*pdep_arrhenius\s*\('([^']+)'\s*,"
    match = re.search(detectReactionName, content, flags=re.IGNORECASE)
    if match:
        reaction_name = match.group(1)
    else:
        reaction_name = None
        
    # Store the initial values in the storage dictionary
    pdep_initial_values_storage[target_reaction_number_pdep] = temp_initial_values 
    pdep_initial_values = pdep_initial_values_storage
    
    # Return both the reaction name and the number of occurrences
    return reaction_name, num_occurrences, pressureValues
    
# Define a global variable to store the threshold value
global_threshold = 0.1  # Initialize with a default value
   
def show_sorted_reactions(reactions):
    global global_threshold, filtered_data, initial_values, brute_force_file, lower_bounds_entries, upper_bounds_entries, lower_bounds_entries_list, upper_bounds_entries_list, target_reaction_numbers_list, store_var_values
    
    selected_reactions = []  # Initialize as an empty list
    # Create a new Tkinter window
    reactions_window = tk.Toplevel(window)
    reactions_window.title("Sensitive Reactions")
    reactions_window.geometry("800x600")
    # Create a Label for the threshold value
    threshold_label = tk.Label(reactions_window, text="Threshold Value:")
    threshold_label.pack()

    # Create an Entry widget for the threshold value
    threshold_entry = tk.Entry(reactions_window)
    threshold_entry.insert(0, str(global_threshold))  # Display the current global threshold
    threshold_entry.pack()
    # Create an "Apply" button to apply the new threshold
    apply_button = tk.Button(reactions_window, text="Apply", command=lambda: apply_threshold(threshold_entry))
    apply_button.pack()
   
    # Function to apply the threshold and update the reactions 
    def apply_threshold(entry_widget):
        global global_threshold
        global brute_force_file
        # Get the threshold value from the Entry widget
        entered_threshold = float(entry_widget.get())
        global_threshold = entered_threshold  # Update global_threshold directly   
        reactions_window.destroy()  # Close the reactions window    
        # Call the filter_reactions function with the new threshold
        filter_reactions(brute_force_file, global_threshold)
        window.was_cancelled = False
        reactions_window.destroy()

    def proceed():
        global selected_reactions, lower_bounds_entries_list, upper_bounds_entries_list, lower_bounds_values, upper_bounds_values, filtered_data, pressureValues, initial_values, target_reaction_numbers_list, pressureValues_storage, store_var_values, initial_reaction_types
        initial_filtered_reactions = [reaction for reaction, var in reaction_checkboxes.items()]

        reaction_numbers = filtered_data.index
        store_var_values = [var.get() for reaction, var in reaction_checkboxes.items()]
        selected_reactions = [reaction for reaction, var in reaction_checkboxes.items() if var.get() == 1]
        unselected_reactions = [reaction for reaction, var in reaction_checkboxes.items() if var.get() == 0]
        
        # Filter out reactions that are in the original 'reactions' list
        # selected_reactions = ['H + O2 (+M) <=> HO2 (+M)_0']
        stripped_selected_reactions = ['_'.join(reaction.split('_')[:-1]) for reaction in selected_reactions]

        initial_reaction_types = reaction_types
        pressure_lengths = [len(inner_list) for inner_list in pressureValues_storage]

        updated_initial_values = []
        pdep_arrhenius_count = 0
        current_initial_value_index = 0

        for reaction_type in reaction_types:
            if reaction_type == 'pdep_arrhenius':
                # Append the skipped values for this 'pdep_arrhenius'
                skip_count = pressure_lengths[pdep_arrhenius_count]
                updated_initial_values.extend(initial_values[current_initial_value_index:current_initial_value_index + skip_count])
                current_initial_value_index += skip_count
                pdep_arrhenius_count += 1
            else:
                # Process the current value if the store_var_value is not 0
                if current_initial_value_index < len(store_var_values) and store_var_values[current_initial_value_index] != 0:
                    updated_initial_values.append(initial_values[current_initial_value_index])
                current_initial_value_index += 1

        # Now, updated_initial_values contains the processed values, skipping appropriately for 'pdep_arrhenius'
        
        initial_values = updated_initial_values
        
        # Initialize lists for lower and upper bounds values
        lower_bounds_values = []
        upper_bounds_values = []
        
        # Retrieve values from lower and upper bound entries
        for index, reaction in enumerate(initial_filtered_reactions):
            var = store_var_values[index]
            # Check if the corresponding var.get() is 1
            if var == 1:
                lower_bound_entry = lower_bounds_entries_list[index]
                upper_bound_entry = upper_bounds_entries_list[index]

                lower_bound = lower_bound_entry.get() if lower_bound_entry else 'Empty'
                upper_bound = upper_bound_entry.get() if upper_bound_entry else 'Empty'

                # Process and store the bounds values
                try:
                    lower_bound_float = float(lower_bound)
                    lower_bounds_values.append(lower_bound_float)
                except ValueError:
                    lower_bounds_values.append('Empty')

                try:
                    upper_bound_float = float(upper_bound)
                    upper_bounds_values.append(upper_bound_float)
                except ValueError:
                    upper_bounds_values.append('Empty')
                    
        # Close the reactions window and unblock the process
        window.was_cancelled = False
        reactions_window.destroy()
        window.grab_set()
        window.focus_set()

    # Define the "Cancel" button command
    def cancel():
        # Close the reactions window, show a message box, and set 'was_cancelled' to True
        reactions_window.destroy()
        messagebox.showinfo("Cancelled", "Sorting reactions cancelled!")
        window.was_cancelled = True
        window.grab_set()
        window.focus_set()
    # Create a frame for the checkboxes
    checkbox_frame = ttk.Frame(reactions_window)
    checkbox_frame.pack(fill='both', expand=True)

    # Create a canvas and a scrollbar
    canvas = tk.Canvas(checkbox_frame)
    scrollbar = ttk.Scrollbar(checkbox_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)

    # Configure the canvas
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)

    # Pack the canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Add a label for "Reactions"
    header_frame = ttk.Frame(scrollable_frame)
    header_frame.pack(fill='x', expand=True)
    reactions_label = tk.Label(header_frame, text="Reactions", font=("Arial", 12))
    reactions_label.pack(side='left', padx=(80,0))
    initial_value_label = tk.Label(header_frame, text="Initial Values", font=("Arial", 12))
    initial_value_label.pack(side='left', padx=(110, 5))
    lower_bound_label = tk.Label(header_frame, text="Lower Bound", font=("Arial", 12))
    lower_bound_label.pack(side='left', padx=(47, 55))
    upper_bound_label = tk.Label(header_frame, text="Upper Bound", font=("Arial", 12))
    upper_bound_label.pack(side='left', padx=(30, 5))
    
    # Dictionary to store the IntVar for each reaction
    reaction_checkboxes = {}
    # Ensure reactions is a list of reaction strings
    reactions = reactions.split('\n')  # Adjust this line based on how reactions are formatted

    def extract_initial_values(brute_force_file, threshold):
        global filtered_data, pressureValues, target_reaction_numbers_list, pressureValues_storage
        # Read the CSV file into a pandas DataFrame
        data = pd.read_csv(brute_force_file)
        
        # Sort the DataFrame by sensitivity rate in descending order
        sorted_data = data.sort_values('bruteforce', ascending=False)

        # Calculate the mean of the sensitivity rate (highest value)
        mean_rate = sorted_data['bruteforce'].max()
    
        # Divide the sensitivity rate by the mean
        sorted_data['bruteforce'] = sorted_data['bruteforce'] / mean_rate
        # Filter the DataFrame for reactions with a sensitivity rate higher than 0.1
        filtered_data = sorted_data[sorted_data['bruteforce'] > threshold]
        
        # Get the sorted reactions as a string
        sorted_reactions = '\n'.join(filtered_data.iloc[:, 0])
    
        filtered_data = sorted_data[sorted_data['bruteforce'] > global_threshold]
        
        selected_reactions = [reaction for reaction, var in reaction_checkboxes.items() if var.get() == 1]
        
        # Extract the index numbers from each string in selected_reactions
        extracted_reactions = ['_'.join(reaction.split('_')[:-1]) for reaction in selected_reactions]
        # Filter the DataFrame using the extracted reaction strings
        filtered_data = filtered_data[filtered_data['Unnamed: 0'].isin(extracted_reactions)]
        
        # Extract the target numbers from the reactions column
        target_reaction_numbers = filtered_data.index + 1
        # Convert the target reaction numbers to a list
    
        target_reaction_numbers_list = target_reaction_numbers.tolist()
        # Create the reaction data dictionary
        reaction_data = {
            'reaction_number': target_reaction_numbers_list,
            'reactions': filtered_data.iloc[:, 0],
            'bruteforce': filtered_data['bruteforce']
        }
        # Create a DataFrame from the reaction data
        reaction_df = pd.DataFrame(reaction_data)
        # Detect the reaction type for each target reaction number
        reaction_types = []
        
        for target_reaction_number in target_reaction_numbers:
            reaction_type = detect_reaction_type(input_file, target_reaction_number)
            reaction_types.append(reaction_type)

        # Loop through the filtered reactions and reaction types
        if os.path.isfile(output_file):
            os.remove(output_file)
        
        regular_initial_values_storage = {}
        three_body_initial_values_storage = {}
        falloff_initial_values_storage = {}
        pdep_initial_values_storage = {}
        pressureValues_storage = []
        for i in range(len(target_reaction_numbers_list)):
            reaction_number = target_reaction_numbers_list[i]
            reaction_type = reaction_types[i]
            # Determine the corresponding function based on the reaction type
            if reaction_type == 'regular':
                initial_values_regular_reaction(input_file, output_file, reaction_number, regular_initial_values_storage)
            elif reaction_type == 'three_body_reaction':
                initial_values_three_body_reaction(input_file, output_file, reaction_number, three_body_initial_values_storage)
            elif reaction_type == 'falloff_reaction':
                initial_values_falloff_reaction(input_file, output_file, reaction_number, falloff_initial_values_storage)
            elif reaction_type == 'pdep_arrhenius':
                reaction_name, num_occurrences, pressureValues = initial_values_pdep_arrhenius(input_file, output_file, reaction_number, pdep_initial_values_storage)
                pressureValues_storage.append(pressureValues)
            else:
                print(f"Unknown reaction type for reaction {reaction_number}")
        return reaction_types
    
    for index, initial_reaction in enumerate(reactions):
        if not initial_reaction.strip():
            continue
        unique_id_init = f"{initial_reaction}_{index}"  # Unique identifier for each reaction
        var_init = tk.IntVar(value=1)  # Default value is checked (1)
        reaction_checkboxes[unique_id_init] = var_init
        initial_values = []        
        reaction_types = extract_initial_values(brute_force_file, global_threshold)

    # New list to store the updated reactions
    updated_reactions = []
    pressure_lengths = [len(inner_list) for inner_list in pressureValues_storage]
    
    pdep_arrhenius_count = 0  # To track the number of 'pdep_arrhenius' encountered so far

    updated_reactions = []

    for reaction, reaction_type in zip(reactions, reaction_types):
        if reaction_type == 'pdep_arrhenius':
            # Use the count to get the correct length from pressureValues_storage
            length_to_extend = pressure_lengths[pdep_arrhenius_count]
            updated_reactions.extend([reaction] * length_to_extend)
            pdep_arrhenius_count += 1  # Increment the count for next 'pdep_arrhenius' encounter
        else:
            updated_reactions.append(reaction)

    reactions = updated_reactions
           
    # Dictionaries to store the Entry widgets for lower and upper bounds
    lower_bounds_entries = {}
    upper_bounds_entries = {}
    
    lower_bounds_entries_list = []
    upper_bounds_entries_list = []  
    
    # Clear existing checkboxes before populating new ones
    reaction_checkboxes.clear() 
    
    # Create a checkbox for each reaction
    for index, reaction in enumerate(reactions):
        # Skip empty lines
        if not reaction.strip():
            continue
        # Create a frame for each reaction
        reaction_frame = ttk.Frame(scrollable_frame)
        reaction_frame.pack(fill='x', expand=True, pady=2)
        # Create separate frames for checkbox, reaction label, and initial value
        checkbox_frame = ttk.Frame(reaction_frame)
        reaction_label_frame = ttk.Frame(reaction_frame)
        initial_value_frame = ttk.Frame(reaction_frame) 
        lower_bound_frame = ttk.Frame(reaction_frame)
        upper_bound_frame = ttk.Frame(reaction_frame)
        
        # Pack the frames side by side
        checkbox_frame.pack(side='left', fill='y')
        reaction_label_frame.pack(side='left', fill='both', expand=True, padx=5)
        initial_value_frame.pack(side='left', fill='y', padx=5)          
        lower_bound_frame.pack(side='left', fill='y', padx=5)
        upper_bound_frame.pack(side='left', fill='y', padx=5) 
             
        unique_id = f"{reaction}_{index}"  # Unique identifier for each reaction
        var = tk.IntVar(value=1)  # Default value is checked (1)
        cb = tk.Checkbutton(checkbox_frame, variable=var)
        cb.pack(side='left', padx=5)
        reaction_checkboxes[unique_id] = var
        
        # Label for the reaction
        reaction_label = tk.Label(reaction_label_frame, text=reaction, anchor='w')
        reaction_label.pack(fill='x', expand=True, side='left', padx=5)
        
        initial_values=[]
        reaction_types = extract_initial_values(brute_force_file, global_threshold)
    
        initial_value = initial_values[index] if index < len(initial_values) else "N/A"
        initial_value_label = tk.Label(initial_value_frame, text=str(initial_value))
        initial_value_label.pack(side='left', padx=(10, 0))
        
        reaction_key = reaction.split('_')[0]
   
        # Lower bound entry
        lower_bound_entry = tk.Entry(lower_bound_frame)
        lower_bound_entry.pack(side='left', padx=5)
        lower_bounds_entries[reaction_key] = lower_bound_entry
        # ... create lower_bound_entry and upper_bound_entry
        lower_bounds_entries_list.append(lower_bound_entry)
           
        # Upper bound entry
        upper_bound_entry = tk.Entry(upper_bound_frame)
        upper_bound_entry.pack(side='left', padx=5)
        upper_bounds_entries[reaction_key] = upper_bound_entry
        upper_bounds_entries_list.append(upper_bound_entry) 
        
    # Create the "Proceed" and "Cancel" buttons
    warning_label = tk.Label(reactions_window, text="Warning! For any unattended or non-numerical bound entries, an uncertainty factor of 0.2 will be applied.")
    warning_label.pack(side='top', padx=10, pady=5 )
    proceed_button = tk.Button(reactions_window, text="Proceed", command=proceed)
    proceed_button.pack(side=tk.LEFT, padx=10, pady=10)
    cancel_button = tk.Button(reactions_window, text="Cancel", command=cancel)
    cancel_button.pack(side=tk.LEFT, padx=10, pady=10)
    
    # Block the process until the window is closed
    reactions_window.transient(window)
    reactions_window.grab_set()
    reactions_window.wait_window()
    # Return the states of the checkboxes
    return {reaction: var.get() for reaction, var in reaction_checkboxes.items()}, target_reaction_numbers_list, pressure_lengths, store_var_values, initial_reaction_types
     
# Update the filter_reactions function
def filter_reactions(brute_force_file, threshold): 
    global initial_values   
    # Read the CSV file into a pandas DataFrame
    data = pd.read_csv(brute_force_file)

    # Sort the DataFrame by sensitivity rate in descending order
    sorted_data = data.sort_values('bruteforce', ascending=False)

    # Calculate the mean of the sensitivity rate (highest value)
    mean_rate = sorted_data['bruteforce'].max()

    # Divide the sensitivity rate by the mean
    sorted_data['bruteforce'] = sorted_data['bruteforce'] / mean_rate
    # Filter the DataFrame for reactions with a sensitivity rate higher than 0.1
    filtered_data = sorted_data[sorted_data['bruteforce'] > threshold]

    # Get the sorted reactions as a string
    sorted_reactions = '\n'.join(filtered_data.iloc[:, 0])
    
    # Show the sorted reactions in a new window
    var_dict, target_reaction_numbers_list, pressure_lengths, store_var_values, initial_reaction_types = show_sorted_reactions(sorted_reactions)
  
    filtered_data = sorted_data[sorted_data['bruteforce'] > global_threshold]
    
    # Extract the index numbers from each string in selected_reactions
    extracted_reactions = ['_'.join(reaction.split('_')[:-1]) for reaction in selected_reactions]
  
    police_var = []
    pressure_index = 0  # Separate index for pressure_lengths
    for rtype in initial_reaction_types:
        if rtype == 'pdep_arrhenius':
            police_var.append(pressure_lengths[pressure_index])
            pressure_index += 1
        else:
            police_var.append(1)

    # Function to check if all values in a range are zero
    def all_zeros_in_range(start, length, values):
        return all(value == 0 for value in values[start:start+length])
    
    smooth_var = []
    start = 0
    for length in police_var:
        if length == 1:
            smooth_var.append(store_var_values[start])
        else:
            smooth_var.append(0 if all_zeros_in_range(start, length, store_var_values) else 1)
        start += length
        
    # Filter the DataFrame using the extracted reaction strings
    filtered_data = filtered_data[filtered_data['Unnamed: 0'].isin(extracted_reactions)]
    
    duplicated_reactions = filtered_data['Unnamed: 0'].duplicated(keep=False)

    if duplicated_reactions.any():
        # Iterate over duplicated reactions
        for index, is_duplicated in duplicated_reactions.items():
            if is_duplicated:
                reaction_number = filtered_data.at[index, 'index'] + 1
                # Find the position of reaction_number in target_reaction_numbers_list
                if reaction_number in target_reaction_numbers_list:
                    pos = target_reaction_numbers_list.index(reaction_number)
                    if smooth_var[pos] == 0:
                        # Remove this row from reaction_data
                        filtered_data = filtered_data.drop(index)

    # Reset the index if needed
    filtered_data.set_index('index', inplace=True)
 
    # Create a new DataFrame for filtered results
    filtered_results = pd.DataFrame()

    adjusted_target_list = [x - 1 for x in target_reaction_numbers_list]

    # Filter out the rows where the index matches any number in target_reaction_numbers_list
    new_filtered_data = filtered_data[filtered_data.index.isin(adjusted_target_list)]

    filtered_data = new_filtered_data
    
    # Check if filtered_data is empty
    if filtered_data.empty:
        print("No reactions left after filtering. Exiting function.")
        return pd.DataFrame(), [], [], {}
             
    target_reaction_numbers_list = filtered_data.index.tolist()
    adjusted_target_list_2 = [x + 1 for x in target_reaction_numbers_list]
    target_reaction_numbers_list = adjusted_target_list_2
    
    # Check if the process was cancelled
    if window.winfo_exists() and not window.was_cancelled:
        # Extract the target numbers from the reactions column
        #target_reaction_numbers = filtered_data.index + 1
        #target_reaction_numbers = target_reaction_numbers_list
        # Convert the target reaction numbers to a list
        #target_reaction_numbers_list = target_reaction_numbers.tolist()

        # Create the reaction data dictionary
        reaction_data = {
            'reaction_number': target_reaction_numbers_list,
            'reactions': filtered_data.iloc[:, 0],
            'bruteforce': filtered_data['bruteforce']
        }
        
        # Create a DataFrame from the reaction data
        reaction_df = pd.DataFrame(reaction_data)

        # Detect the reaction type for each target reaction number
        reaction_types = []
        pdep_reaction_numbers = []
        for target_reaction_number in target_reaction_numbers_list:
            reaction_type = detect_reaction_type(input_file, target_reaction_number)
            reaction_types.append(reaction_type)
               
        pdep_reaction_numbers = [number for number, type_ in zip(target_reaction_numbers_list, reaction_types) if type_ == 'pdep_arrhenius']
                   
        var_values_dict = {}
        var_values_index = 0  # Index to track current position in var_values
        pdep_arrhenius_count = 0  # To track 'pdep_arrhenius' occurrences
        var_values = store_var_values 
        
        ################################################################################################
        non_string_indices = [i for i, value in enumerate(initial_values) if not isinstance(value, str)]

        split_var_values = []
        start = 0
        for length in pressure_lengths:
            indices = non_string_indices[start:start+length]
            split_var_values.append([var_values[i] for i in indices])
            start += length
        no_zeros_split_var_values = [sublist for sublist in split_var_values if not all(value == 0 for value in sublist)]
        # Collect all indices to delete first, then delete them in reverse order to avoid index errors
        indices_to_delete = []
        for i, reaction_var_values in enumerate(split_var_values):
            if all(val == 0 for val in reaction_var_values):
                reaction_indices = non_string_indices[sum(pressure_lengths[:i]):sum(pressure_lengths[:i + 1])]
                indices_to_delete.extend(reaction_indices)

        # Sort indices in reverse order and delete them
        for index in sorted(indices_to_delete, reverse=True):
            del initial_values[index]
        ################################################################################################
              
        for reaction_type in reaction_types:
            if reaction_type == 'pdep_arrhenius':
                # Determine the range of var_values to use
                length_to_use = pressure_lengths[pdep_arrhenius_count]

                pdep_var_values = no_zeros_split_var_values[pdep_arrhenius_count]
                # Use the reaction number as the key
                unique_key = pdep_reaction_numbers[pdep_arrhenius_count]
                var_values_dict[unique_key] = pdep_var_values

                # Update the indices
                var_values_index += length_to_use
                pdep_arrhenius_count += 1
            else:
                # Skip non-'pdep_arrhenius' reaction types
                continue

        # Return the filtered DataFrame and other relevant data
        return reaction_df[['reaction_number', 'reactions', 'bruteforce']], reaction_types, target_reaction_numbers_list, var_values_dict, initial_reaction_types, pressure_lengths
            
def proceed_with_csv(csv_path):
    global brute_force_file, lower_bounds_values, upper_bounds_values
    brute_force_file = csv_path
    # Call the filter_reactions function
    filtered_reactions, reaction_types, target_reaction_numbers_list, var_values_dict, initial_reaction_types, pressure_lengths = filter_reactions(brute_force_file, global_threshold)
    # Delete the output file if it already exists
    if os.path.isfile(output_file):
        os.remove(output_file)
      
    # Loop through the filtered reactions and reaction types
    for i in range(len(target_reaction_numbers_list)):
        reaction_number = target_reaction_numbers_list[i]
        reaction_type = reaction_types[i]
        
        # Determine the corresponding function based on the reaction type
        if reaction_type == 'regular':
            #var_values_regular = var_values_dict.get(reaction_number, [])
            regular_reaction(input_file, output_file, reaction_number)
        elif reaction_type == 'three_body_reaction':
            var_values_three_body = var_values_dict.get(reaction_number, [])
            three_body_reaction(input_file, output_file, reaction_number, var_values_three_body, three_body_initial_values)
        elif reaction_type == 'falloff_reaction':
            var_values_falloff = var_values_dict.get(reaction_number, [])
            falloff_reaction(input_file, output_file, reaction_number, var_values_falloff)
        elif reaction_type == 'pdep_arrhenius':
            var_values_pdep = var_values_dict.get(reaction_number, [])
            pressureValues = pdep_arrhenius(input_file, output_file, reaction_number, var_values_pdep, pdep_initial_values)
        else:
            print(f"Unknown reaction type for reaction {reaction_number}")

    in_path = 'jaya_run/jaya.in'
    org_in_path = 'jaya_run/jaya.in.org'
    if os.path.exists(in_path):
        os.remove(in_path)
    # Copy jaya-algorithm.org.py to jaya-algorithm.py
    shutil.copy(org_in_path, in_path)
    update_jaya_input_file(in_path, descriptors, initial_values, lower_bounds_values, upper_bounds_values) 

def prompt_csv_exists(button):

    # Create a window to prompt the user
    window = tk.Toplevel()
    window.title("CSV File")

    # Create a variable to store the user's choice
    csv_choice = IntVar()

    # Create the question text
    question_label = tk.Label(window, text="Load the *.csv file as shown in the example!")
    question_label.pack()

    def browse_csv():
        csv_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select sensitivity.csv file", filetypes=(("CSV files", "*.csv"),))
        if csv_path:
            window.destroy()  # Close the prompt window
            proceed_with_csv(csv_path)
            button.config(state="disabled")  # Change the state of the button to "disabled"
            idt_list_button.config(state="disabled")  # Change the state of the checkbutton to "normal"
            button_analysis.config(state="disabled")  # Change the state of the button to "disabled"
            
    # Create a button for browsing the CSV file
    browse_button = tk.Button(window, text="Browse", command=browse_csv)
    browse_button.pack()

    # Start the main event loop for the window
    window.mainloop()

# Function to modify and run the idt_sensitivity.py script
def run_sensitivity_analysis(csv_path=None):
    # Get the values from the input fields
    pres = float(entry_sensitivity_pres.get())
    temp = float(entry_sensitivity_temp.get())
    phi = float(entry_sensitivity_phi.get())
    fuel = entry_sensitivity_fuel.get()
    oxidizer = entry_sensitivity_oxidizer.get()
    #mech = entry_sensitivity_mech.get()
    mech = input_file

    # Construct the command
    command = f"cti2yaml {mech}"

    # Construct the output YAML file name
    mech_yaml = mech.replace('.cti', '.yaml')
    
    # Run the command
    try:
        subprocess.run(command, check=True, shell=True)
    except subprocess.CalledProcessError as e:
        print(f"An error occurred while converting CTI to YAML: {e}")
        return
    except FileNotFoundError:
        print("cti2yaml command not found. Make sure it is installed and in your PATH.")
        return
        
    new_filename = "user_defined_idt_sensitivity.py"  # Specify the user-defined filename here

    # Read the original idt_sensitivity.py script
    with open("idt_sensitivity.py", "r") as file:
        script_content = file.read()

    # Update the variables in the script content
    updated_script = script_content.replace("pres = ", f"pres = {pres}")
    updated_script = updated_script.replace("temp = ", f"temp = {temp}")
    updated_script = updated_script.replace("phi = ", f"phi = {phi}")
    updated_script = updated_script.replace("fuel = ", f"fuel = '{fuel}'")
    updated_script = updated_script.replace("oxidizer = ", f"oxidizer = '{oxidizer}'")
    updated_script = updated_script.replace("mech = ", f"mech = '{mech_yaml}'")

    # Specify the absolute file path for the temporary script
    temp_script_path = os.path.join(os.getcwd(), new_filename)

    # Write the updated script to the temporary file
    with open(temp_script_path, "w") as file:
        file.write(updated_script)

    # Run the updated script using the subprocess module
    try:
        if csv_path:
            subprocess.run(["python3", temp_script_path, csv_path], check=True)
        else:
            subprocess.run(["python3", temp_script_path], check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to run the sensitivity analysis script.")
    
    # Delete the temporary script file
    os.remove(temp_script_path)
    global brute_force_file
    proceed_with_csv(brute_force_file)

    button_prompt_csv.config(state="disabled")
    idt_list_button.config(state="disabled")
    button_analysis.config(state="disabled")
    
def update_jaya_input_file(file_path, descriptors, initial_values, lower_bounds_values, upper_bounds_values):
    
    with open(file_path, 'r') as file:
        lines = file.readlines()

    updated_line = 'cdv_initial_point\t'
    for descriptor, value in zip(descriptors, initial_values):
        updated_line += f'{value}\t'

    updated_lower_bounds_line = 'cdv_lower_bounds\t'
    updated_upper_bounds_line = 'cdv_upper_bounds\t'

    
    for index, (value_initial, value_lower, value_upper) in enumerate(zip(initial_values, lower_bounds_values, upper_bounds_values)):
    
        try:
            initial_float = float(value_initial)
        except ValueError:
            initial_float = None  # or some default value if value_initial is not a float

        try:
            # Try converting value_lower to float
            lower_bound_float = float(value_lower)
            lower_bounds_values[index] = lower_bound_float
        except ValueError:
            if initial_float is not None:
                if initial_float < 0:
                    lower_bounds_values[index] = initial_float * 10**0.2   
                else:
                    lower_bounds_values[index] = initial_float / 10**0.2   
        updated_lower_bounds_line += f'{lower_bounds_values[index]}\t'
        try:
            # Try converting value_upper to float
            upper_bound_float = float(value_upper)
            upper_bounds_values[index] = upper_bound_float
        except ValueError:
            if initial_float is not None:
                if initial_float < 0:
                    upper_bounds_values[index] = initial_float / 10**0.2  
                else:
                    upper_bounds_values[index] = initial_float * 10**0.2  
                    
        updated_upper_bounds_line += f'{upper_bounds_values[index]}\t'
        if initial_float < lower_bounds_values[index]:
            print("ERROR! Lower bound is higher than the initial value!")
            return
        if initial_float > upper_bounds_values[index]:
            print("ERROR! Upper bound is lower than the initial value!")
            return

    num_descriptors = len(descriptors)
    
    for i, line in enumerate(lines):
        if 'cdv_initial_point' in line:
            lines[i] = updated_line.rstrip() + '\n'
        elif 'cdv_lower_bounds' in line:
            lines[i] = updated_lower_bounds_line.rstrip() + '\n'
        elif 'cdv_upper_bounds' in line:
            lines[i] = updated_upper_bounds_line.rstrip() + '\n'
        elif 'cdv_descriptor' in line:
            updated_descriptor_line = "cdv_descriptor\t"
            for descriptor in descriptors:
                updated_descriptor_line += f"'{descriptor}'\t"
            lines[i] = updated_descriptor_line.rstrip() + '\n'
        elif 'continuous_design' in line:
            lines[i] = f'continuous_design = {num_descriptors}\n'
            
    with open(file_path, 'w') as file:
        file.writelines(lines)
    
    jaya_algorithm_path = 'jaya_run/jaya-algorithm.py'
    jaya_algorithm_org_path = 'jaya_run/jaya-algorithm.org.py'
    # Check if jaya-algorithm.py exists and delete it
    if os.path.exists(jaya_algorithm_path):
        os.remove(jaya_algorithm_path)
    # Copy jaya-algorithm.org.py to jaya-algorithm.py
    shutil.copy(jaya_algorithm_org_path, jaya_algorithm_path)

    with open(jaya_algorithm_path, 'r') as file:
        lines = file.readlines()
        
    updated_lower_bounds = updated_lower_bounds_line.split('\t')[1:-1]  # Skip the label and the last empty element
    updated_upper_bounds = updated_upper_bounds_line.split('\t')[1:-1]  # Skip the label and the last empty element

    # Update the initial_values and variable_ranges
    for i, line in enumerate(lines):
        if 'initial_values =' in line:
            lines[i] = "    initial_values = {\n"
            for idx, (desc, val) in enumerate(zip(descriptors, initial_values)):
                if idx == len(descriptors) - 1:  # Check if it's the last item
                    lines[i] += f"        '{desc}'\t:\t({val})\n"
                else:
                    lines[i] += f"        '{desc}'\t:\t({val}),\n"
            lines[i] += "    }\n\n"
        elif 'variable_ranges =' in line:
            lines[i] = "    variable_ranges = {\n"
            for idx, (desc, lb, ub) in enumerate(zip(descriptors, updated_lower_bounds_line.rstrip().split('\t')[1:], updated_upper_bounds_line.rstrip().split('\t')[1:])):
                if idx == len(descriptors) - 1:  # Check if it's the last item
                    lines[i] += f"        '{desc}'\t:\t({lb}, {ub})\n"
                else:
                    lines[i] += f"        '{desc}'\t:\t({lb}, {ub}),\n"
            lines[i] += "    }\n\n"

    # Write the updated lines back to the file
    with open(jaya_algorithm_path, 'w') as file:
        file.writelines(lines)
        
def generate_plot():
    # Read data from nd-vasu.txt file
    data = np.loadtxt('jaya_run/workdir.228/nd-idt.txt', delimiter=',')
    x = data[:, 0]
    y1 = data[:, 1]
    y2 = data[:, 2]

    # Create a Figure object and a single subplot
    fig, ax = plt.subplots(figsize=(6, 4))

    # Clear the previous plot and update with new data using symbols and a line plot
    ax.clear()
    ax.plot(x, y1, marker='o', linestyle='', label='Experiment')
    ax.plot(x, y2, label='Latest Best Result')
    ax.set_title('Lowest Error')
    ax.set_xlabel('1000/T')
    ax.set_ylabel('Ignition Delay Time (ms)')
    ax.set_yscale('log')
    ax.legend()
    # Apply tight layout
    plt.tight_layout()
    # Display the plot
    plt.show()

# Add a Refresh button to the top right corner
#refresh_button = tk.Button(window, text="Refresh", command=restart_window)
#refresh_button.grid(row=0, column=1, sticky="NE", padx=10, pady=10)

# Create a button to prompt if a sensitivity.csv file exists
button_prompt_csv = tk.Button(window, text="Do you have a 'sensitivity.csv' file?", command=lambda: prompt_csv_exists(button_prompt_csv), name="prompt_csv_button", state="normal") #disabled
button_prompt_csv.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

def toggle_input_lines():
    if show_input.get():
        # Show the input lines
        label_sensitivity_pres.grid(row=4, column=0, padx=10, pady=10)
        entry_sensitivity_pres.grid(row=4, column=1, padx=10, pady=10)
        label_sensitivity_temp.grid(row=5, column=0, padx=10, pady=10)
        entry_sensitivity_temp.grid(row=5, column=1, padx=10, pady=10)
        label_sensitivity_phi.grid(row=6, column=0, padx=10, pady=10)
        entry_sensitivity_phi.grid(row=6, column=1, padx=10, pady=10)
        label_sensitivity_fuel.grid(row=7, column=0, padx=10, pady=10)
        entry_sensitivity_fuel.grid(row=7, column=1, padx=10, pady=10)
        label_sensitivity_oxidizer.grid(row=8, column=0, padx=10, pady=10)
        entry_sensitivity_oxidizer.grid(row=8, column=1, padx=10, pady=10)
        #label_sensitivity_mech.grid(row=7, column=0, padx=10, pady=10)
        #entry_sensitivity_mech.grid(row=7, column=1, padx=10, pady=10)
    else:
        # Hide the input lines
        label_sensitivity_pres.grid_forget()
        entry_sensitivity_pres.grid_forget()
        label_sensitivity_temp.grid_forget()
        entry_sensitivity_temp.grid_forget()
        label_sensitivity_phi.grid_forget()
        entry_sensitivity_phi.grid_forget()
        label_sensitivity_fuel.grid_forget()
        entry_sensitivity_fuel.grid_forget()
        label_sensitivity_oxidizer.grid_forget()
        entry_sensitivity_oxidizer.grid_forget()
        #label_sensitivity_mech.grid_forget()
        #entry_sensitivity_mech.grid_forget()

browse_target_button = None  # Declare browse_target_button as a global variable

def toggle_input_lines_optimization_configurations():
    global browse_target_button  # Use the global browse_target_button variable

    if show_input_2.get():
        # Show the input lines
        label_optimization_pres.grid(row=13, column=0, padx=10, pady=10)
        entry_optimization_pres.grid(row=13, column=1, padx=10, pady=10)
        label_optimization_phi.grid(row=14, column=0, padx=10, pady=10)
        entry_optimization_phi.grid(row=14, column=1, padx=10, pady=10)
        label_optimization_fuel.grid(row=15, column=0, padx=10, pady=10)
        entry_optimization_fuel.grid(row=15, column=1, padx=10, pady=10)
        label_optimization_oxidizer.grid(row=16, column=0, padx=10, pady=10)
        entry_optimization_oxidizer.grid(row=16, column=1, padx=10, pady=10)
        label_optimization_target.grid(row=17, column=0, padx=10, pady=10)
        entry_optimization_target.grid(row=17, column=1, padx=10, pady=10)
        # Create a button for browsing the target .csv file
        browse_target_button = tk.Button(window, text="Browse", command=browse_target_csv)
        browse_target_button.grid(row=17, column=2, padx=10, pady=10)
        #label_optimization_mech.grid(row=18, column=0, padx=10, pady=10)
        #entry_optimization_mech.grid(row=18, column=1, padx=10, pady=10)
        #button_opt_conditions.grid(row=19, column=0, columnspan=2, padx=10, pady=10)
    else:
        # Hide the input lines and the "Browse" button
        label_optimization_pres.grid_forget()
        entry_optimization_pres.grid_forget()
        label_optimization_phi.grid_forget()
        entry_optimization_phi.grid_forget()
        label_optimization_fuel.grid_forget()
        entry_optimization_fuel.grid_forget()
        label_optimization_oxidizer.grid_forget()
        entry_optimization_oxidizer.grid_forget()
        label_optimization_target.grid_forget()
        entry_optimization_target.grid_forget()
        if browse_target_button is not None:
            browse_target_button.grid_forget()  # Hide the "Browse" button if it exists
            browse_target_button = None  # Reset browse_target_button to None
        #label_optimization_mech.grid_forget()
        #entry_optimization_mech.grid_forget()
        #button_opt_conditions.grid_forget() 
        
# Function to modify IDT-interface file
def optimization_configurations():
    # Get the values from the input fields
    pres = float(entry_optimization_pres.get())
    phi = float(entry_optimization_phi.get())
    fuel = entry_optimization_fuel.get()
    oxidizer = entry_optimization_oxidizer.get()
    #mech = input_file
    target = entry_optimization_target.get()

    # Path to the original IDT-interface_template.py script
    original_file_path = "jaya_run/casebase/IDT-interface_template.py"

    # Path to the original simulator_script
    #original_simulator_script = "jaya_run/simulator_script_template"
    
    # Read the content of the original file
    with open(original_file_path, "r") as file:
        script_content = file.read()

    # Read the content of the original file
    #with open(original_simulator_script, "r") as file:
    #    script_simulator = file.read()
        
    # Update the variables in the script content
    updated_script = script_content.replace("pres = ", f"pres = {pres}")
    updated_script = updated_script.replace("phi = ", f"phi = {phi}")
    updated_script = updated_script.replace("fuel = ", f"fuel = '{fuel}'")
    updated_script = updated_script.replace("oxidizer = ", f"oxidizer = '{oxidizer}'")
    #updated_script = updated_script.replace("mechanism = ", f"mechanism = '{mech}'")
    #update_simulator = script_simulator.replace('mechanism=', f'mechanism="{mech}"')
    updated_script = updated_script.replace('target_file = ', f'target_file = "{target}"')

    # Path to the new IDT-interface.py script
    new_file_path = "jaya_run/casebase/IDT-interface.py"
    #new_simulator_script = "jaya_run/simulator_script"
    
    # Delete the existing IDT-interface.py file if it exists
    if os.path.exists(new_file_path):
        os.remove(new_file_path)

    #if os.path.exists(new_simulator_script):
    #    os.remove(new_simulator_script)
                
    # Write the updated script to the new file
    with open(new_file_path, "w") as file:
        file.write(updated_script)
    # Write the updated script to the new file
    #with open(new_simulator_script, "w") as file:
    #    file.write(update_simulator)
    
    #button_opt_conditions.config(state="disabled")
    button_run_jaya.config(state="normal")
    
  
# Create the widgets - sensitivity
label_sensitivity_pres = tk.Label(window, text="Pressure (atm):", bg="lightblue")
entry_sensitivity_pres = tk.Entry(window)

label_sensitivity_temp = tk.Label(window, text="Temperature (K):", bg="lightblue")
entry_sensitivity_temp = tk.Entry(window)

label_sensitivity_phi = tk.Label(window, text="Equivalence Ratio (Φ):", bg="lightblue")
entry_sensitivity_phi = tk.Entry(window)

label_sensitivity_fuel = tk.Label(window, text="Fuel:", bg="lightblue")
entry_sensitivity_fuel = tk.Entry(window)

label_sensitivity_oxidizer = tk.Label(window, text="Oxidizer:", bg="lightblue")
entry_sensitivity_oxidizer = tk.Entry(window)

#label_sensitivity_mech = tk.Label(window, text="Mechanism File:", bg="lightblue")
#entry_sensitivity_mech = tk.Entry(window)

# Create the widgets - optimization parameters
label_optimization_pres = tk.Label(window, text="Pressure (atm):", bg="lightblue")
entry_optimization_pres = tk.Entry(window)

label_optimization_phi = tk.Label(window, text="Equivalence Ratio (Φ):", bg="lightblue")
entry_optimization_phi = tk.Entry(window)

label_optimization_fuel = tk.Label(window, text="Fuel:", bg="lightblue")
entry_optimization_fuel = tk.Entry(window)

label_optimization_oxidizer = tk.Label(window, text="Oxidizer:", bg="lightblue")
entry_optimization_oxidizer = tk.Entry(window)



def browse_target_csv():
    target_csv_path = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select experimental target .csv file", filetypes=(("CSV files", "*.csv"),))
    if target_csv_path:
        entry_optimization_target.delete(0, tk.END)  # Clear the current entry value
        entry_optimization_target.insert(0, target_csv_path)  # Insert the selected file path into the entry field

# Create the widgets
label_optimization_target = tk.Label(window, text="Experimental Target:", bg="lightblue")
entry_optimization_target = tk.Entry(window)

# Place the widgets on the grid
label_optimization_target.grid(row=13, column=0, padx=10, pady=10)
entry_optimization_target.grid(row=13, column=1, padx=10, pady=10)

#label_optimization_mech = tk.Label(window, text="Mechanism file:", bg="lightblue")
#entry_optimization_mech = tk.Entry(window)

# Create a variable to track the state of the button
show_input = tk.BooleanVar()

# Initially hide the input lines
toggle_input_lines()

show_input_2 = tk.BooleanVar()

toggle_input_lines_optimization_configurations()

# Create the "Open the list" button as a Checkbutton (toggle switch)
idt_list_button = tk.Checkbutton(window, text="Sensitivity Configurations", variable=show_input, command=toggle_input_lines , bg="lightblue", state="normal") #disabled
idt_list_button.grid(row=3, column=0, columnspan=2, padx=10, pady=10)

# Create a button to run the sensitivity analysis
button_analysis = tk.Button(window, text="Run Sensitivity Analysis", command=run_sensitivity_analysis, state="normal") #disabled
button_analysis.grid(row=11, column=0, columnspan=2, padx=10, pady=10)

# Create the "Open the list" button as a Checkbutton (toggle switch)
#idt_list_button_opt = tk.Checkbutton(window, text="Ignition Delay Time - Optimization Configurations", variable=show_input_2, command=toggle_input_lines_optimization_configurations , bg="lightblue", state="disabled")
#idt_list_button_opt.grid(row=12, column=0, columnspan=2, padx=10, pady=10)

# Create a button to run the sensitivity analysis
#button_analysis_plot = tk.Button(window, text="Generate Plot Test", command=generate_plot, state="disabled")
#button_analysis_plot.grid(row=25, column=0, columnspan=2, padx=10, pady=10)
	
#######################################################################################################################################################
# Function to delete existing files matching the pattern
def delete_existing_simulation_files():
    file_pattern_idt = "jaya_run/casebase/IDT-simulation-*"
    for filepath in glob.glob(file_pattern_idt):
        try:
            os.remove(filepath)
            print(f"Deleted file: {filepath}")
        except OSError as e:
            print(f"Error deleting file {filepath}: {e}")

    file_pattern_lbv = "jaya_run/casebase/LBV-simulation-*"
    for filepath in glob.glob(file_pattern_lbv):
        try:
            os.remove(filepath)
            print(f"Deleted file: {filepath}")
        except OSError as e:
            print(f"Error deleting file {filepath}: {e}")
            
# Call this function before initiating new tasks
delete_existing_simulation_files()

def refresh_configurations(idt_num_configs, lbv_num_configs):
    # Clear existing widgets from the scrollable frame
    for widget in scrollable_frame.scrollable_frame.winfo_children():
        widget.destroy()

    # Clear the entry widgets list
    entry_widgets.clear()
    entry_widgets.update({"pres": [], "phi": [], "fuel": [], "oxidizer": [], "target": []})
    entry_widgets_2.clear()
    entry_widgets_2.update({"pres": [], "T": [], "fuel": [], "oxidizer": [], "target": []})
    # Recreate the widgets for both IDT and LBV
    for i in range(idt_num_configs):
        idt_create_optimization_config_input(i)

    for i in range(lbv_num_configs):
        lbv_create_optimization_config_input(i)

    # Update 'Apply Conditions' button position
    total_configs = idt_num_configs + lbv_num_configs + 1
    apply_opt_conditions.grid(row=30 + total_configs * 5, column=0, columnspan=3, padx=10, pady=10)


def delete_excess_idt_simulation_files(num_configs):
    file_pattern = "jaya_run/casebase/IDT-simulation-*.py"
    for filepath in glob.glob(file_pattern):
        # Extract the index from the file name
        index = int(re.search(r'IDT-simulation-(\d+)\.py', filepath).group(1))
        
        # Delete files with index higher than num_configs
        if index > num_configs:
            try:
                os.remove(filepath)
                print(f"Deleted excess file: {filepath}")
            except OSError as e:
                print(f"Error deleting file {filepath}: {e}")

def delete_excess_lbv_simulation_files(num_configs):
    file_pattern = "jaya_run/casebase/LBV-simulation-*.py"
    for filepath in glob.glob(file_pattern):
        # Extract the index from the file name
        index = int(re.search(r'LBV-simulation-(\d+)\.py', filepath).group(1))
        
        # Delete files with index higher than num_configs
        if index > num_configs:
            try:
                os.remove(filepath)
                print(f"Deleted excess file: {filepath}")
            except OSError as e:
                print(f"Error deleting file {filepath}: {e}")
                

class ScrollableFrame(tk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.config(bg="lightblue")
        canvas = tk.Canvas(self, bg="lightblue", width=1000)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="lightblue")

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

scrollable_frame = ScrollableFrame(window)
scrollable_frame.grid(row=32, column=0, columnspan=3, sticky='nsew')

# Assuming you have a dictionary to store your entry widgets
entry_widgets = {
    "pres": [],
    "phi": [],
    "fuel": [],
    "oxidizer": [],
    "target": []
}

entry_widgets_2 = {
    "pres": [],
    "T": [],
    "fuel": [],
    "oxidizer": [],
    "target": []
}

global idt_num_configs
global lbv_num_configs

def experimental_browse_file_idt(index):

    # Open a file dialog and get the selected file path
    filepath = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")], # Show only .csv files
        title="Select a CSV file"
    )

    # If a file was selected, update the corresponding entry field
    if filepath:
        entry_widgets["target"][index].delete(0, tk.END)
        entry_widgets["target"][index].insert(0, filepath)

def experimental_browse_file_lbv(index):

    # Open a file dialog and get the selected file path
    filepath = filedialog.askopenfilename(
        filetypes=[("CSV Files", "*.csv")], # Show only .csv files
        title="Select a CSV file"
    )

    # If a file was selected, update the corresponding entry field
    if filepath:
        entry_widgets_2["target"][index].delete(0, tk.END)
        entry_widgets_2["target"][index].insert(0, filepath)

def append_to_simulations(template_path, output_path):
    # Read the content of Simulations_template.py
    with open(template_path, "r") as file:
        template_content = file.read()

    # Placeholder to append content
    append_placeholder = "# APPEND HERE"

    # Find the position of the placeholder
    append_position = template_content.find(append_placeholder)
    if append_position == -1:
        print("Append placeholder not found in the template.")
        return

    # Initialize the new content with the original content up to the placeholder
    new_content = template_content[:append_position + len(append_placeholder)]

    # Get all IDT and LBV simulation file paths and sort them
    idt_files = sorted(glob.glob("jaya_run/casebase/IDT-simulation-*.py"))
    lbv_files = sorted(glob.glob("jaya_run/casebase/LBV-simulation-*.py"))

    # Append contents of sorted IDT and LBV simulation files
    for filepath in idt_files + lbv_files:
        with open(filepath, "r") as file:
            new_content += "\n" + file.read()

    # Append the remaining part of the template
    new_content += template_content[append_position + len(append_placeholder):]

    # Write the updated content to Simulations.py
    with open(output_path, "w") as file:
        file.write(new_content)

              
def apply_all_conditions():
    print("idt_num_configs", idt_num_configs)
    for i in range(idt_num_configs):
        print(f"Processing IDT configuration {i}")
        idt_optimization_configurations(i)
    print("lbv_num_configs", lbv_num_configs)
    print("Applying LBV conditions...")
    for i in range(lbv_num_configs):
        print(f"Processing LBV configuration {i}")
        lbv_optimization_configurations(i)

    print("Finished applying conditions.")
    apply_opt_conditions.grid(row=40, column=0, columnspan=3, padx=10, pady=10)
    button_run_jaya.config(state="normal")
    
    # Path to the template file
    template_file_path = 'jaya_run/casebase/Simulations_template.py'  # Adjust the path as needed
    output_file_path = 'jaya_run/casebase/Simulations.py'  # Adjust the path as needed
    append_to_simulations(template_file_path, output_file_path)
    
apply_opt_conditions = tk.Button(window, text="Apply Conditions", command=apply_all_conditions, state="normal") #disabled
apply_opt_conditions.grid(row=40, column=0, columnspan=2, padx=10, pady=10)

def set_configurations():

    global idt_num_configs
    global lbv_num_configs
    try:
        idt_num_configs = int(idt_entry_num_configs.get())
        lbv_num_configs = int(lbv_entry_num_configs.get())
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid number")
        return

    refresh_configurations(idt_num_configs, lbv_num_configs)
   
    delete_excess_idt_simulation_files(idt_num_configs)
    delete_excess_lbv_simulation_files(lbv_num_configs)
        
def idt_create_optimization_config_input(index):
    # Set uniform padding for the rows
    for i in range(30 + index * 5, 35 + index * 5):
        scrollable_frame.scrollable_frame.rowconfigure(i, pad=10)
    # Create pressure entry widget
    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.IDT - Pressure (atm):", bg="lightblue").grid(row=30+index*5, column=0)
    pres_entry = tk.Entry(scrollable_frame.scrollable_frame)
    pres_entry.grid(row=30 + index * 5, column=1)
    entry_widgets["pres"].append(pres_entry)

    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.IDT - Equivalence Ratio (Φ):", bg="lightblue").grid(row=31+index*5, column=0)
    phi_entry = tk.Entry(scrollable_frame.scrollable_frame)
    phi_entry.grid(row=31 + index * 5, column=1)
    entry_widgets["phi"].append(phi_entry)

    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.IDT - Fuel :", bg="lightblue").grid(row=32+index*5, column=0)
    fuel_entry = tk.Entry(scrollable_frame.scrollable_frame)
    fuel_entry.grid(row=32 + index * 5, column=1)
    entry_widgets["fuel"].append(fuel_entry)

    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.IDT - Oxidizer :", bg="lightblue").grid(row=33+index*5, column=0)
    oxidizer_entry = tk.Entry(scrollable_frame.scrollable_frame)
    oxidizer_entry.grid(row=33 + index * 5, column=1)
    entry_widgets["oxidizer"].append(oxidizer_entry)

    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.IDT - Experimental Target :", bg="lightblue").grid(row=34+index*5, column=0, pady=(0, 10))
    target_entry = tk.Entry(scrollable_frame.scrollable_frame)
    target_entry.grid(row=34 + index * 5, column=1, pady=(0, 10))
    entry_widgets["target"].append(target_entry)

    # Create Browse button for the target entry
    browse_button = tk.Button(scrollable_frame.scrollable_frame, text="Browse", command=lambda: experimental_browse_file_idt(index))
    browse_button.grid(row=34 + index * 5, column=2, pady=(0, 10))
                
    if index == 0:
        apply_opt_conditions.config(state="normal") 
                 
def idt_optimization_configurations(index):
    # Ensure the index is valid
    if index >= len(entry_widgets["pres"]):
        # Handle invalid index, perhaps show an error message
        return

    # Retrieve values from the entry widgets
    pres = entry_widgets["pres"][index].get()

    phi = entry_widgets["phi"][index].get()
    
    fuel = entry_widgets["fuel"][index].get()
    
    oxidizer = entry_widgets["oxidizer"][index].get()
    
    target = entry_widgets["target"][index].get()
    
    # Path to the original script
    original_file_path = "jaya_run/casebase/IDT-interface_template.py"

    # Read the content of the original file
    with open(original_file_path, "r") as file:
        script_content = file.read()

    # Replace placeholders in the script content
    updated_script = script_content.replace("pres = ", f"pres = {pres}")
    updated_script = updated_script.replace("phi = ", f"phi = {phi}")
    updated_script = updated_script.replace("fuel = ", f"fuel = '{fuel}'")
    updated_script = updated_script.replace("oxidizer = ", f"oxidizer = '{oxidizer}'")
    updated_script = updated_script.replace("target_file = ", f"target_file = '{target}'")
    # Replace the INDEX placeholder with the actual index value
    updated_script = updated_script.replace("INDEX", f"{index + 1}_idt")

    # Path to the new IDT-interface.py script
    new_file_path = f"jaya_run/casebase/IDT-simulation-{index + 1}.py"
    #new_simulator_script = "jaya_run/simulator_script"
    
    # Delete the existing IDT-interface.py file if it exists
    if os.path.exists(new_file_path):
        os.remove(new_file_path)
                
    # Write the updated script to the new file
    with open(new_file_path, "w") as file:
        file.write(updated_script)

    #apply_opt_conditions.config(state="disabled")
    button_run_jaya.config(state="normal")

def lbv_create_optimization_config_input(index):
    # Set uniform padding for the rows
    for i in range(30 + index * 5, 35 + index * 5):
        scrollable_frame.scrollable_frame.rowconfigure(i, pad=10)
    # Create pressure entry widget
    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.LBV - Pressure (atm):", bg="lightblue").grid(row=30+index*5, column=3, padx=(100, 0))
    pres_entry = tk.Entry(scrollable_frame.scrollable_frame)
    pres_entry.grid(row=30 + index * 5, column=4)
    entry_widgets_2["pres"].append(pres_entry)

    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.LBV - Temperature (K):", bg="lightblue").grid(row=31+index*5, column=3, padx=(100, 0))
    T_entry = tk.Entry(scrollable_frame.scrollable_frame)
    T_entry.grid(row=31 + index * 5, column=4)
    entry_widgets_2["T"].append(T_entry)

    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.LBV - Fuel :", bg="lightblue").grid(row=32+index*5, column=3, padx=(100, 0))
    fuel_entry = tk.Entry(scrollable_frame.scrollable_frame)
    fuel_entry.grid(row=32 + index * 5, column=4)
    entry_widgets_2["fuel"].append(fuel_entry)

    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.LBV - Oxidizer :", bg="lightblue").grid(row=33+index*5, column=3, padx=(100, 0))
    oxidizer_entry = tk.Entry(scrollable_frame.scrollable_frame)
    oxidizer_entry.grid(row=33 + index * 5, column=4)
    entry_widgets_2["oxidizer"].append(oxidizer_entry)

    tk.Label(scrollable_frame.scrollable_frame, text=f"{index+1}.LBV - Experimental Target :", bg="lightblue").grid(row=34+index*5, column=3, padx=(100, 0), pady=(0, 10))
    target_entry = tk.Entry(scrollable_frame.scrollable_frame)
    target_entry.grid(row=34 + index * 5, column=4, pady=(0, 10))
    entry_widgets_2["target"].append(target_entry)

    # Create Browse button for the target entry
    browse_button = tk.Button(scrollable_frame.scrollable_frame, text="Browse", command=lambda: experimental_browse_file_lbv(index))
    browse_button.grid(row=34 + index * 5, column=5, pady=(0, 10))
                
    if index == 0:
        apply_opt_conditions.config(state="normal")           

def lbv_optimization_configurations(index):
    # Ensure the index is valid
    if index >= len(entry_widgets_2["pres"]):
        # Handle invalid index, perhaps show an error message
        return

    # Retrieve values from the entry widgets
    pres = entry_widgets_2["pres"][index].get()

    T = entry_widgets_2["T"][index].get()
    
    fuel = entry_widgets_2["fuel"][index].get()
    
    oxidizer = entry_widgets_2["oxidizer"][index].get()
    
    target = entry_widgets_2["target"][index].get()
    
    # Path to the original script
    original_file_path = "jaya_run/casebase/LBV-interface_template.py"

    # Read the content of the original file
    with open(original_file_path, "r") as file:
        script_content = file.read()

    # Replace placeholders in the script content
    updated_script = script_content.replace("pres = ", f"pres = {pres}")
    updated_script = updated_script.replace("T = ", f"T = {T}")
    updated_script = updated_script.replace("fuel = ", f"fuel = '{fuel}'")
    updated_script = updated_script.replace("oxidizer = ", f"oxidizer = '{oxidizer}'")
    updated_script = updated_script.replace("target_file = ", f"target_file = '{target}'")
    # Replace the INDEX placeholder with the actual index value
    updated_script = updated_script.replace("INDEX", f"{index + 1}_idt")

    # Path to the new LBV-interface.py script
    new_file_path = f"jaya_run/casebase/LBV-simulation-{index + 1}.py"
    #new_simulator_script = "jaya_run/simulator_script"
    
    # Delete the existing LBV-interface.py file if it exists
    if os.path.exists(new_file_path):
        os.remove(new_file_path)

    #if os.path.exists(new_simulator_script):
    #    os.remove(new_simulator_script)
                
    # Write the updated script to the new file
    with open(new_file_path, "w") as file:
        file.write(updated_script)

    #apply_opt_conditions.config(state="disabled")
    button_run_jaya.config(state="normal")
               
idt_num_configs = tk.Label(window, text="Number of IDT Configurations:", bg="lightblue", state="normal") #disabled
idt_num_configs.grid(row=29, column=0, padx=10, pady=10)

idt_entry_num_configs = tk.Entry(window)
idt_entry_num_configs.grid(row=29, column=1, padx=10, pady=10)

lbv_num_configs = tk.Label(window, text="Number of LBV Configurations:", bg="lightblue", state="normal") #disabled
lbv_num_configs.grid(row=30, column=0, padx=10, pady=10)

lbv_entry_num_configs = tk.Entry(window)
lbv_entry_num_configs.grid(row=30, column=1, padx=10, pady=10)

button_set_configs = tk.Button(window, text="Set Configurations", command=set_configurations, state="normal") #disabled
button_set_configs.grid(row=29, column=2, padx=10, pady=10)
#######################################################################################################################################################

# Create a frame for the logo
logo_frame = tk.Frame(window)
logo_frame.grid(row=0, column=0, padx=0, pady=10)

# Create a subframe for centering
center_frame = tk.Frame(logo_frame)
center_frame.pack(expand=True)

# Load the logo image
original_image = Image.open("logo2.png")

# Resize the image (example: resize to 100x100 pixels)
resized_image = original_image.resize((90, 100))

# Convert the resized image to a PhotoImage object
logo_image = ImageTk.PhotoImage(resized_image)

# Display the logo image
logo_label = tk.Label(center_frame, image=logo_image, bg="lightblue")
logo_label.pack()

window.configure(bg="lightblue")

def run_jaya_command():
    # Save the current working directory
    original_directory = os.getcwd()
        
    # Change the current working directory to the jaya_run folder
    jaya_run_folder = "jaya_run"
    os.chdir(jaya_run_folder)

    # Set execute permissions for the simulator script
    simulator_script = "simulator_script"  # Replace with the actual filename
        
    # The jaya command to be executed
    command = "python3 jaya-algorithm.py"

    try:
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError:
        messagebox.showerror("Error", "Failed to run the jaya command.")
    finally:
        # Change the current working directory back to the original directory
        os.chdir(original_directory)

               
# Create a button to run the jaya command
button_run_jaya = tk.Button(window, text="Run jaya", command=run_jaya_command, state="normal") #disabled
button_run_jaya.grid(row=100, column=0, columnspan=2, padx=10, pady=10)

#window.minsize(width=800, height=600) 

# Start the main event loop
window.mainloop()

