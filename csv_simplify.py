# Import the modules needed for the program
import pandas as pd
import re
import os
import pickle
import math
import time

# Define the global variables for the regex patterns and the replacement strings
alphanum8_pattern = r'"[a-zA-Z0-9_-]{8}"'
path_pattern = r'(?:(?:[\'"])(/[^\'"]+)(?:[\'"]))|(?:(?<=\s)(/[^\'"\s]+)(?=\s))'
numeric_pattern = r'(?<=echo )\d{5,12}'
hostname_pattern = r"(?P<environment>[p|t|q])(?P<location>[2|3])(?P<segment>[e|a])(?P<tier>[a|d|g|i|m|w])(?P<virtualization>[v|p])(?P<operating_system>[w|x|r|s|k])(?P<application>[a-z0-9]{3,4})(?P<server>[0-9]{2})(?:\.(?P<intra_inter>(intra|inter))(?P<suffix_env>(prd|qat))\.[a-zA-Z0-9]+\.[a-zA-Z0-9]+\.[a-zA-Z0-9]+)?\b"
alphanum8_string = "ALPHANUM8"
path_string = "PATH"
numeric_string = "NUMERIC"
hostname_string = "HOSTNAME"

# Define the global variables for the sensitive values
XXX = "abc"
TLD = "com"
YY = "sg"

# Define the global variables for the environment, segment, intra_inter, and suffix_env
environment = "p"
segment = "e"
intra_inter = "intra"
suffix_env = "prd"

# Define the function for simplifying and replacing the command strings
def simplify_and_replace(command):
    # Initialize the simplified string and the lists of original and replacement strings
    simplified = command
    original = []
    replacement = []
    # Define the arrays of regex strings for the match patterns and replacement strings
    patterns = [alphanum8_pattern, path_pattern, numeric_pattern, hostname_pattern]
    strings = [alphanum8_string, path_string, numeric_string, hostname_string]
    # For each pattern, do the following:
    for i in range(len(patterns)):
        # Find the part of the command string that matches the pattern using re.match and group(0)
        match = re.match(patterns[i], simplified)
        # If the part is a path and it is at the start of the command string, do not replace or reference it
        if match and strings[i] == path_string and match.start() == 0:
            continue
        # Otherwise, replace the part with the corresponding replacement string and add it to the lists of original and replacement strings
        else:
            while match:
                # Replace the match with the replacement string
                simplified = simplified.replace(match.group(0), strings[i])
                # Append the match to the list of original strings
                original.append(match.group(0))
                # Append the replacement string to the list of replacement strings
                replacement.append(strings[i])
                # Find the next match in the simplified string
                match = re.match(patterns[i], simplified)
    # Return the simplified string, the list of original strings, and the list of replacement strings
    return simplified, original, replacement

# Define the function for generating the references
def generate_references(original, originals):
    # Initialize the reference value as an empty list
    reference = []
    # For each original string, do the following:
    for o in original:
        # Check if the original string is already in the original mapping dataframe
        if o in originals["Value"].values:
            # Get the index of the original string in the original mapping dataframe
            index = originals[originals["Value"] == o].index[0]
            # Increment the count of the original string in the original mapping dataframe by one
            originals.loc[index, "Count"] += 1
        # If the original string is not in the original mapping dataframe, do the following:
        else:
            # Get the index of the original string as the length of the original mapping dataframe
            index = len(originals)
            # Append the original string and its count to the original mapping dataframe
            originals = originals.append({"Value": o, "Count": 1}, ignore_index=True)
        # Generate the reference value by appending the index number to the list
        reference.append(index)
    # Return the reference value and the updated original mapping dataframe
    return reference, originals

# Define the function for saving the program state
def save_state(file_name, input_df, originals, counter):
    # Open the state file in write mode using the pickle module
    with open("program_state.pkl", "wb") as state_file:
        # Create a dictionary named "state" with the file name, the input dataframe, the original mapping dataframe, and the counter as the keys and values
        state = {"file_name": file_name, "input_df": input_df, "originals": originals, "counter": counter}
        # Dump the state dictionary to the state file using the pickle module
        pickle.dump(state, state_file)

# Define the function for loading the program state
def load_state(file_name):
    # Check if the state file exists using the os module
    if os.path.exists("program_state.pkl"):
        # Open the state file in read mode using the pickle module
        with open("program_state.pkl", "rb") as state_file:
            # Load the state dictionary from the state file using the pickle module
            state = pickle.load(state_file)
            # Check if the file name matches the current file
            if state["file_name"] == file_name:
                # Get the input dataframe, the original mapping dataframe, and the counter from the state dictionary
                input_df = state["input_df"]
                originals = state["originals"]
                counter = state["counter"]
                # Return the input dataframe, the original mapping dataframe, and the counter
                return input_df, originals, counter
            # If the file name does not match, do the following:
            else:
                # Return None, None, and 0
                return None, None, 0
    # If the state file does not exist, do the following:
    else:
        # Return None, None, and 0
        return None, None, 0

# Define the function for deleting the state file
def delete_state():
    # Check if the state file exists using the os module
    if os.path.exists("program_state.pkl"):
        # Delete the state file using the os module
        os.remove("program_state.pkl")

# Define the function for writing the output file
def write_output(file_name, input_df, originals, pivot):
    # Create a writer object using the ExcelWriter function of pandas with the output file name as the argument
    output_file_name = file_name.replace(".csv", "_simplified.xlsx")
    writer = pd.ExcelWriter(output_file_name)
    # Check the number of rows in the input dataframe and assign it to a variable named rows
    rows = len(input_df)
    # If rows is less than or equal to 1048576, do the following:
    if rows <= 1048576:
        # Write the input dataframe to the writer object with the sheet name "Simplified" and the index argument set to True using the to_excel method of pandas
        input_df.to_excel(writer, sheet_name="Simplified", index=True)
    # If rows is greater than 1048576, do the following:
    else:
        # Calculate the number of chunks needed to split the input dataframe using the formula ceil(rows / 1048576)
        chunks = math.ceil(rows / 1048576)
        # Loop through the number of chunks and do the following:
        for i in range(1, chunks + 1):
            # Get the start and end row numbers for the current chunk using the formula start = (i - 1) * 1048576 and end = i * 1048576 - 1
            start = (i - 1) * 1048576
            end = i * 1048576 - 1
            # Get the subset of the input dataframe for the current chunk using the iloc method of pandas with the start and end row numbers as the arguments
            input_df_chunk = input_df.iloc[start:end]
            # Generate the sheet name for the current chunk using the formula "Simplified_" + str(end + 2)
            sheet_name = "Simplified_" + str(end + 2)
            # Write the subset of the input dataframe to the writer object with the sheet name and the index argument set to True using the to_excel method of pandas
            input_df_chunk.to_excel(writer, sheet_name=sheet_name, index=True)
    # Write the original mapping dataframe to the writer object with the sheet name "Originals" and the index argument set to True using the to_excel method of pandas
    originals.to_excel(writer, sheet_name="Originals", index=True)

    # Write the pattern counts to the writer object with the sheet name "Pattern Counts" and the index argument set to False using the to_excel method of pandas
    pattern_counts = originals["Value"].str.split(" ", expand=True).stack().value_counts().reset_index()
    pattern_counts.columns = ["Pattern", "Count"]
    pattern_counts.to_excel(writer, sheet_name="Pattern Counts", index=False)
    
    # Write the pivot table to the writer object with the sheet name "Command Patterns" and the index argument set to False using the to_excel method of pandas
    pivot.to_excel(writer, sheet_name="Command Patterns", index=False)
    # Save the writer object using the save method of pandas
    writer.save()

# Define the function for processing the input file
def process_file(file_name):
    # Load the program state from the state file using the load_state function and assign the returned values to input_df, original, and counter
    input_df, original, counter = load_state(file_name)
    # If input_df and original are None, create an empty dataframe named original with two columns: "Value" and "Count", then read in the CSV file and store it in a pandas dataframe named input_df
    if input_df is None and original is None:
        original = pd.DataFrame(columns=["Value", "Count"])
        input_df = pd.read_csv(file_name)
    # Get the total number of rows in the input_df dataframe and assign it to a variable named total
    total = len(input_df)
    # Assign the current time to a variable named start_time
    start_time = time.time()
    # Loop through the rows of the input_df dataframe starting from the counter value and get the command string from the "Command/Events" column
    for i in range(counter, total):
        command = input_df.loc[i, "Command/Events"]
        # Simplify and replace the command string with the simplified string and the list of original strings using the simplify_and_replace function
        simplified, original_list, replacement_list = simplify_and_replace(command)
        # Generate the reference value and the updated original mapping dataframe using the generate_references function with the list of original strings and the original mapping dataframe as arguments
        reference, original = generate_references(original_list, original)
        # Update the input_df dataframe with the simplified string and the reference value in a new column named "Reference"
        input_df.loc[i, "Command/Events"] = simplified
        input_df.loc[i, "Reference"] = reference
        # Increment the counter by one
        counter += 1
        # Every time the counter is a multiple of 0.5% of the total number of lines, do the following:
        if counter % math.ceil(total * 0.005) == 0:
            # Call the save_state function with the file name, the input dataframe, the original mapping dataframe, and the counter as arguments
            save_state(file_name, input_df, original, counter)
            # Print a message to the standard output that shows how many lines have been processed and what percentage of the total that is
            print(f"Processed {counter} lines out of {total}, which is {round(counter / total * 100, 2)}% of the total.")
            # Calculate the average time per line and the remaining time based on the current time and the start time
            current_time = time.time()
            avg_time = (current_time - start_time) / counter
            remaining_time = avg_time * (total - counter)
            # Print a message to the standard output that shows the estimated time to finish the program
            print(f"Estimated time to finish: {round(remaining_time, 2)} seconds.")
    # After the loop is finished, create a pivot table of the simplified commands and their counts using the pivot_table function of pandas
    pivot = input_df.pivot_table(index="Command/Events", values="Reference", aggfunc="count").reset_index()
    pivot.columns = ["Command/Events", "Count"]
    # Write the input_df, the original dataframe and the pivot table to the output Excel file using the write_output function
    write_output(file_name, input_df, original, pivot)
    # Delete the state file using the delete_state function
    delete_state()

# Loop through the CSV files in the current directory and do the following:
for file in os.listdir():
    # Get the file name of the current CSV file
    if file.endswith(".csv"):
        # Call the process file function with the file name as the argument
        process_file(file)
