import os
import csv

def main():
    run_folders = [folder for folder in os.listdir() if folder.startswith("run.")]
    run_folders.sort(key=lambda folder: int(folder.split(".")[-1]))  # Sort folders numerically
    
    # Create CSV file and write header
    with open("objectives.csv", "w", newline="") as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Run", "Objective"])

        # Read objective values from the objective.txt files in run folders
        for run_folder in run_folders:
            objective_path = os.path.join(run_folder, "objective.txt")
            
            with open(objective_path, 'r') as objective_file:
                objective_number = float(objective_file.read())
            
            run_num = int(run_folder.split(".")[-1])
            csv_writer.writerow([run_num, objective_number])

if __name__ == "__main__":
    main()

