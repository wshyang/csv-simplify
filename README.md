# csv-simplify

## 1. Introduction
This document describes the functional specifications of a program that simplifies and analyzes the command strings in a CSV file. The program replaces the command strings with simplified strings and references, and stores the original values and their counts in a separate dataframe. It also generates a pivot table of the simplified commands and their counts. It writes the output to an Excel file with four tabs: Simplified, Original, Pattern Counts, and Command Patterns.

### 1.1 Overview
The program is designed to simplify and analyze the command strings in a CSV file. The command strings are complex and contain various components, such as paths, numbers, hostnames, etc. The program simplifies the command strings by replacing these components with simplified strings, such as PATH, NUMERIC, HOSTNAME, etc. The program also generates references for the original values that were replaced, using the index number of the original value in the references dataframe. The program stores the original values and their counts in a separate dataframe, and creates a pivot table of the simplified commands and their counts. The program writes the output to an Excel file with four tabs: Simplified, Original, Pattern Counts, and Command Patterns.

### 1.2 Input and Output
The input is a CSV file that contains the command strings in a column named "Command/Events". The output is an Excel file that contains the input dataframe with the simplified values and the references, the references dataframe with the original values and their counts, and the pivot table of the simplified commands and their counts in separate tabs. The output file name is derived from the source file name by appending a suffix of "_simplified". For example, if the input file name is "commands.csv", the output file name will be "commands_simplified.xlsx".

### 1.3 Program State
The program saves and loads the program state to and from a state file named "program_state.pkl". The program state is a dictionary that contains the following keys and values:

- "file_name": the name of the input CSV file
- "input_df": the input dataframe
- "original": the references dataframe
- "counter": the counter variable that tracks the progress of the program

The program saves the program state to the state file every time it reaches a threshold of 0.5% of the total lines to be processed. The program loads the program state from the state file if it exists and the file name matches the current file. The program resumes from the previous state at the line indicated by the counter value. The program deletes the state file after the output file is written and saved.

## 2. Simplification and Replacement Rules
The program simplifies and replaces the command strings with simplified strings and references using the following rules:

- The reference values are generated by using the index number of the original value in the references dataframe. The index number is the same as the index of the original value in the references dataframe. For example, if the original value is `"aBcD_1-2"` and its index in the references dataframe is 2, the reference value will be `ALPHANUM8_2`. The reference values are stored as a comma separated list in the new Reference column of the input dataframe. The references dataframe has an Index column that corresponds to the reference suffixes. For example, if the reference value is `PATH_1`, the Index column will have the value 1. This way, the references can be easily correlated with the original values and their counts.
- Replace a double quote enclosed block of 8 characters consisting of both upper and lowercase alphanumeric characters, underscore and dash, with the string "ALPHANUM8". For example, `"aBcD_1-2"` is replaced with `ALPHANUM8`.
- Replace strings that resemble UNIX paths under the default directories, either not enclosed in quotes, or enclosed in matching single or double quotes, with the string "PATH". For example, `'/usr/bin/python'` and `"/home/user/file.txt"` are replaced with `PATH` and `PATH`, respectively. However, if a PATH is at the start of the command string, it should not be replaced or referenced. For example, `/usr/bin/python /home/user/file.txt` is not replaced or referenced, but `/usr/bin/python /home/user/file.txt` is replaced with `/usr/bin/python PATH` and referenced as `PATH_5`.
- Replace numbers between 5 and 12 digits long that follow the word "echo" with the string "NUMERIC". For example, `echo 123456789` is replaced with `NUMERIC_0`.
- Replace valid hostnames with the string "HOSTNAME". A valid hostname follows the regex pattern defined in the global variable `hostname_pattern`. For example, `p2eavwaabc01.intraPRD.abc.com.sg` is replaced with `HOSTNAME_5`.
- The program does not replace or reference any other components of the command strings that do not match the rules. For example, `echo hello` is not replaced or referenced.

### 2.1 How the References are Generated
The references are generated by using the index number of the original value in the references dataframe. For example, if the simplified value is PATH, the reference value will be PATH_1, PATH_2, etc. depending on how many times the path value has been encountered and replaced in the input dataframe. The reference values are stored as a comma separated list in the new Reference column of the input dataframe. The references dataframe has an Index column that corresponds to the reference suffixes. For example, if the reference value is PATH_1, the Index column will have the value 1. This way, the references can be easily correlated with the original values and their counts.

### 2.2 Example Scenarios for PATH

The following are some examples of test cases and scenarios that demonstrate how the program should simplify and replace the command strings in the input CSV file.

#### Test case 1

The input CSV file contains a command string that starts with a path and has another path in the middle. The program should not replace or reference the first path, but should replace and reference the second path. For example, the input dataframe before processing:

| Command/Events | Reference |
| -------------- | --------- |
| /usr/bin/python /home/user/file.txt |  |

The input dataframe after processing:

| Command/Events | Reference |
| -------------- | --------- |
| /usr/bin/python PATH | [1] |

The references dataframe should contain:

| Index | Value | Count |
| ----- | ----- | ----- |
| 1 | /home/user/file.txt | 1 |

The pivot table should contain:

| Command/Events | Reference |
| -------------- | --------- |
| /usr/bin/python PATH | 1 |

## 3. Functions
The program defines the following functions to perform the simplification and replacement of the command strings, the generation of the references, the saving and loading of the program state, the writing of the output file, and the processing of the input file.

### 3.1 Simplify and Replace Function
The program defines a function `simplify_and_replace` that takes a command string as an argument and returns a simplified string, a list of original strings, and a list of replacement strings that were replaced using the simplification and replacement rules. 

- The simplified string is the command string with the original strings replaced by the replacement strings according to the rules.
- The original list is the list of original strings that were replaced by the replacement strings in the same order as they appear in the command string.
- The replacement list is the list of replacement strings that replaced the original strings in the same order as they appear in the command string.

The function uses the following logic and algorithm to perform the simplification and replacement:

- Define the arrays of regex strings for the match patterns and replacement strings
- For each command string, do the following:
  - Initialize the simplified string and the lists of original and replacement strings
  - For each pattern, do the following:
    - Find the part of the command string that matches the pattern using `re.match` and `group(0)`
    - If the part is a path and it is at the start of the command string, do not replace or reference it
    - Otherwise, replace the part with the corresponding replacement string and add it to the lists of original and replacement strings
- Replace the match with the replacement string
- Append the match to the list of original strings
- Append the replacement string to the list of replacement strings
- Return the simplified string, the list of original strings, and the list of replacement strings

### 3.2 Generate References Function
The program defines a function `generate_references` that takes a list of original strings and the original dataframe as arguments and returns a reference value using the reference generation rules.

- The reference value is a list of integers of the reference values that correspond to the index of the original strings in the references dataframe in the same order as they appear in the command string.
- The function modifies the original dataframe in place according to the reference generation rules. The original dataframe contains the original values and their counts in two columns: "Value" and "Count".

The function uses the following logic and algorithm to perform the reference generation:

- Initialize the reference value as an empty list
- For each original string, do the following:
  - Check if the original string is already in the original dataframe
  - If yes, get the index of the original string in the original dataframe
  - Increment the count of the original string in the original dataframe by one
  - If no, get the index of the original string as the length of the original dataframe
  - Append the original string and its count to the original dataframe
  - Generate the reference value by appending the index number to the list
- Return the reference value

### 3.3 Save State Function
The program defines a function `save_state` that takes the file name, the input dataframe, the original dataframe, and the counter as arguments and saves them to the state file using the pickle module.

- The state file is named "program_state.pkl" and contains the program state as a dictionary with the following keys and values:
  - "file_name": the name of the input CSV file
  - "input_df": the input dataframe
  - "original": the references dataframe
  - "counter": the counter variable that tracks the progress of the program
- The function saves the program state to the state file every time it reaches a threshold of 0.5% of the total lines to be processed.

The function uses the following logic and algorithm to perform the state saving:

- Open the state file in write mode using the pickle module
- Create a dictionary named "state" with the file name, the input dataframe, the original dataframe, and the counter as the keys and values
- Dump the state dictionary to the state file using the pickle module
- Close the state file

### 3.4 Load State Function
The program defines a function `load_state` that takes the file name as an argument and loads the program state from the state file if it exists and the file name matches the current file. It returns the input dataframe, the original dataframe, and the counter.

- The state file is named "program_state.pkl" and contains the program state as a dictionary with the following keys and values:
  - "file_name": the name of the input CSV file
  - "input_df": the input dataframe
  - "original": the references dataframe
  - "counter": the counter variable that tracks the progress of the program
- The function loads the program state from the state file and resumes from the previous state at the line indicated by the counter value.

The function uses the following logic and algorithm to perform the state loading:

- Check if the state file exists using the os module
- If the state file exists, do the following:
  - Open the state file in read mode using the pickle module
  - Load the state dictionary from the state file using the pickle module
  - Close the state file
  - Check if the file name matches the current file
  - If the file name matches, do the following:
    - Get the input dataframe, the original dataframe, and the counter from the state dictionary
    - Return the input dataframe, the original dataframe, and the counter
  - If the file name does not match, do the following:
    - Return None, None, and 0
- If the state file does not exist, do the following:
  - Return None, None, and 0

### 3.5 Delete State Function
The program defines a function `delete_state` that deletes the state file if it exists.

- The state file is named "program_state.pkl" and contains the program state as a dictionary with the following keys and values:
  - "file_name": the name of the input CSV file
  - "input_df": the input dataframe
  - "original": the references dataframe
  - "counter": the counter variable that tracks the progress of the program
- The function deletes the state file after the output file is written and saved.

The function uses the following logic and algorithm to perform the state deletion:

- Check if the state file exists using the os module
- If the state file exists, do the following:
  - Delete the state file using the os module

### 3.6 Write Output Function
The program defines a function `write_output` that takes the file name, the input dataframe, the original dataframe, and the pivot table as arguments and writes them to the output Excel file in separate tabs using the `to_excel` method of pandas with the `index=True` argument to preserve the index of the dataframes.

- The output Excel file is named by appending a suffix of "_simplified" to the source file name. For example, if the input file name is "commands.csv", the output file name will be "commands_simplified.xlsx".
- The output Excel file has four tabs: "Simplified", "Original", "Pattern Counts", and "Command Patterns".
  - The "Simplified" tab contains the input dataframe with the simplified values and the references.
  - The "Original" tab contains the original values and their counts.
  - The "Pattern Counts" tab contains the pattern counts of the simplified values.
  - The "Command Patterns" tab contains the pivot table of the simplified values and their counts.
- The program also checks if the input dataframe exceeds the maximum number of rows per sheet allowed by Excel, which is 1048576. If the input dataframe is too large, the program splits it into smaller chunks and writes them to different sheets in the output Excel file. The sheet names are based on the original sheet name, with a suffix consisting of an underscore, and then the record number of the next record. For example, if the input dataframe has 2000000 rows, the program will write the first 1048575 rows to a sheet named “Simplified”, and the remaining 951425 rows to a sheet named “Simplified_1048576”. This needs to take into account the row taken up by the header row at the top of each sheet.

The function uses the following logic and algorithm to perform the output writing:

- Create a writer object using the `ExcelWriter` function of pandas with the output file name as the argument
- Check the number of rows in the input dataframe and assign it to a variable named `rows`
- If `rows` is less than or equal to 1048576, do the following:
  - Write the input dataframe to the writer object with the sheet name "Simplified" and the index argument set to True using the `to_excel` method of pandas
- If `rows` is greater than 1048576, do the following:
  - Calculate the number of chunks needed to split the input dataframe using the formula `ceil(rows / 1048576)`
  - Loop through the number of chunks and do the following:
    - Get the start and end row numbers for the current chunk using the formula `start = (i - 1) * 1048576` and `end = i * 1048576 - 1`, where `i` is the current chunk number
    - Get the subset of the input dataframe for the current chunk using the `iloc` method of pandas with the start and end row numbers as the arguments
    - Generate the sheet name for the current chunk using the formula `"Simplified_" + str(end + 2)`
    - Write the subset of the input dataframe to the writer object with the sheet name and the index argument set to True using the `to_excel` method of pandas
- Write the original dataframe to the writer object with the sheet name "Original" and the index argument set to True using the `to_excel` method of pandas
- Write the pattern counts to the writer object with the sheet name "Pattern Counts" and the index argument set to True using the `to_excel` method of pandas
- Write the pivot table to the writer object with the sheet name "Command Patterns" and the index argument set to True using the `to_excel` method of pandas
- Save the writer object using the `save` method of pandas

### 3.7 Process File Function
The program defines a function `process_file` that takes the file name as an argument and performs the following steps:

- Load the program state from the state file using the `load_state` function and assign the returned values to `input_df`, `original`, and `counter`.
- If `input_df` and `original` are None, create an empty dataframe named `original` with two columns: "Value" and "Count", then read in the CSV file and store it in a pandas dataframe named `input_df`.
- Get the total number of rows in the `input_df` dataframe and assign it to a variable named `total`.
- Assign the current time to a variable named `start_time`.
- Loop through the rows of the `input_df` dataframe starting from the `counter` value and get the command string from the "Command/Events" column.
- Simplify and replace the command string with the simplified string and the list of original strings using the `simplify_and_replace` function.
- Generate the reference value and the updated original dataframe using the `generate_references` function with the list of original strings and the original dataframe as arguments.
  - Update the `input_df` dataframe with the simplified string and the reference value in a new column named "Reference".
  - Increment the `counter` by one.
- Every time the counter is a multiple of 0.5% of the total number of lines, do the following:
  - Call the save_state function with the file name, the input dataframe, the original dataframe, and the counter as arguments. This will save the current progress of the program to a state file.
  - Print a message to the standard output that shows how many lines have been processed and what percentage of the total that is.
  - Calculate the average time per line and the remaining time based on the current time and the start time. Print a message to the standard output that shows the estimated time to finish the program.
- After the loop is finished, create a pivot table of the simplified commands and their counts using the `pivot_table` function of pandas. The pivot table has the simplified command strings as the index and the counts as the values.
- Write the `input_df`, the `original` dataframe and the pivot table to the output Excel file using the `write_output` function.
- Delete the state file using the `delete_state` function.

## 4. Logic and Algorithm
The program uses the following logic and algorithm to perform the simplification and analysis of the command strings in the input CSV file:

- Import the modules needed for the program, such as pandas, re, os, pickle, math, and time
- Define the global variables for the regex patterns and the replacement strings, such as `alphanum8_pattern`, `path_pattern`, `numeric_pattern`, `hostname_pattern`, `alphanum8_string`, `path_string`, `numeric_string`, and `hostname_string`
- Define the global variables for the sensitive values, such as XXX, TLD, and YY
- Define the global variables for the environment, segment, intra_inter, and suffix_env
- Define the functions for the simplification and replacement, the reference generation, the state saving and loading, the output writing, and the file processing, as described in the previous section
- Loop through the CSV files in the current directory and do the following:
  - Get the file name of the current CSV file
  - Call the process file function with the file name as the argument

## 5. Details of the Regexs and the Hostname Specifications
The program uses the following regexs and hostname specifications to match and replace the command strings according to the rules:

### 5.1 Regex for Matching Paths
The program uses the following regex for matching paths:

`path_pattern = r'(?:(?:[\'"])(/[^\'"]+)(?:[\'"]))|(?:(?<=\s)(/[^\'"\s]+)(?=\s))'`

This regex matches the following cases:

- A path that is enclosed in single or double quotes, such as `'/usr/bin/python'` or `"/home/user/file.txt"`
- A path that is not enclosed in quotes, but is preceded and followed by a whitespace, such as `/usr/bin/python /home/user/file.txt`

The regex captures the path in a group, excluding the quotes if present.

### 5.2 Regex for Matching Numbers
The program uses the following regex for matching numbers:

`numeric_pattern = r'(?<=echo )\d{5,12}'`

This regex matches the following cases:

- A number that is between 5 and 12 digits long and follows the word "echo", such as `echo 123456789`

The regex does not capture the word "echo" in the group, only the number.

### 5.3 Regex for Matching Hostnames
The program uses the following regex for matching hostnames:

```python
r"(?P<environment>[p|t|q])(?P<location>[2|3])(?P<segment>[e|a])(?P<tier>[a|d|g|i|m|w])(?P<virtualization>[v|p])(?P<operating_system>[w|x|r|s|k])(?P<application>[a-z0-9]{3,4})(?P<server>[0-9]{2})(?:\.(?P<intra_inter>(intra|inter))(?P<suffix_env>(PRD|QAT))\.[a-zA-Z0-9]+\.[a-zA-Z0-9]+\.[a-zA-Z0-9]+)?\b"
```

This regex matches any string that follows the hostname format of:

[environment][location][segment][tier][virtualization][operating_system][application][server].suffix

### 5.4 Hostname Format and Specifications
Hostnames follow the below format and specifications:

[environment][location][segment][tier][virtualization][operating_system][application][server].suffix

Each component has a specific meaning and a set of valid characters, as described below:

  - Environment: This component indicates the environment type of the server. It can be one of the following values:
      - Production (p): This indicates that the server is used for production purposes, such as hosting live applications or services.
      - Training (t): This indicates that the server is used for training purposes, such as providing a sandbox environment for learning or testing.
      - Quality (q): This indicates that the server is used for quality assurance purposes, such as performing verification or validation tests on applications or services.
  - Location: This component indicates the location code of the server. It can be either 2 or 3, depending on the region where the server is located. For example, 2 for Singapore, 3 for Tokyo, etc.
  - Segment: This component indicates the business segment of the server. It can be one of the following values:
      - Internet (e): This indicates that the server is used for internet-facing applications or services, such as web portals or APIs.
      - Intranet (a): This indicates that the server is used for internal applications or services, such as intranet sites or databases.
  - Tier: This component indicates the server tier of the server. It can be one of the following values:
      - App server (a): This indicates that the server is used for application logic or processing, such as running scripts or programs.
      - Database server (d): This indicates that the server is used for data storage or retrieval, such as hosting databases or files.
      - Gateway server (g): This indicates that the server is used for network communication or routing, such as providing access to other servers or networks.
      - Integration server (i): This indicates that the server is used for data integration or transformation, such as performing ETL (Extract, Transform, Load) operations or data cleansing.
      - Management server (m): This indicates that the server is used for management or administration, such as providing monitoring or security functions.
      - Web server (w): This indicates that the server is used for web presentation or delivery, such as hosting web pages or static content.
  - Virtualization: This component indicates the server type of the server. It can be one of the following values:
      - Virtual server (v): This indicates that the server is a virtual machine or a container, running on a physical host or a cloud platform.
      - Physical server (p): This indicates that the server is a physical machine or a bare metal server, running on dedicated hardware or a data center.
  - Operating System: This component indicates the operating system of the server. It can be one of the following values:
      - Windows (w): This indicates that the server is running on a Windows operating system, such as Windows Server or Windows 10.
      - Appliance with proprietary OS (x): This indicates that the server is running on a proprietary operating system, such as a network appliance or a security device.
      - Redhat (r): This indicates that the server is running on a Redhat operating system, such as Redhat Enterprise Linux or Redhat OpenShift.
      - SuSE (s): This indicates that the server is running on a SuSE operating system, such as SuSE Linux Enterprise or SuSE Cloud.
      - KMS appliance with proprietary OS (k): This indicates that the server is running on a proprietary operating system, specifically for a Key Management System (KMS) appliance.
  - Application: This component indicates the application identifier of the server. It can be a unique 3 or 4 character identifier for the application type, such as tns for Tenable, kms for Key Management System, etc.
  - Server: This component indicates the server identifier of the server. It can be a two-digit number indicating the server identifier within its specific application or type, such as 01, 02, 03, etc.
  - Suffix: This component is optional and indicates the intra/inter network, the suffix environment, and the sensitive values XXX, TLD, and YY of the server. It can be one of the following formats:
      - intraprd.XXX.TLD.YY: This indicates that the server is in the intranet network, the suffix environment is production, and the sensitive values are XXX, TLD, and YY. For example, intraprd.abc.com.sg.
      - interqat.XXX.TLD.YY: This indicates that the server is in the internet network, the suffix environment is quality or training, and the sensitive values are XXX, TLD, and YY. For example, interqat.abc.com.sg.

The environment, segment, intra_inter, and suffix_env must be consistent. For example, if the environment is production, the suffix_env must be prd. If the segment is intranet, the intra_inter must be intra. The suffix components must match the sensitive values for XXX, TLD, and YY. For example, if XXX is abc, TLD is com, and YY is sg, the suffix must be intraprd.abc.com.sg or interprd.abc.com.sg. The hostname must be converted to lowercase using casefold() before matching the regex and the specifications. This is to avoid case sensitive issues. For example, P2EAVWAABC01.INTRAPRD.ABC.COM.SG and p2eavwaabc01.intraprd.abc.com.sg are considered the same hostname.

## 6. Test Cases and Scenarios
The program should be tested with various test cases and scenarios to ensure its correctness and robustness. The following are some examples of test cases and scenarios that can be used to test the program:

### 6.1 Test Case 1: Simple Command String
The input CSV file contains a simple command string that does not have any components that need to be simplified or replaced. The program should not modify the command string or generate any references. For example, the input dataframe before processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo hello |  |

The input dataframe after processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo hello |  |

The references dataframe should be empty:

| Index | Value | Count |
| ----- | ----- | ----- |

The pivot table should contain:

| Command/Events | Reference |
| -------------- | --------- |
| echo hello | 1 |

### 6.2 Test Case 2: Command String with ALPHANUM8
The input CSV file contains a command string that has a double quote enclosed block of 8 characters consisting of both upper and lowercase alphanumeric characters, underscore and dash. The program should replace the block with the string "ALPHANUM8" and generate a reference for it. For example, the input dataframe before processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo "aBcD_1-2" |  |

The input dataframe after processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo ALPHANUM8 | [1] |

The references dataframe should contain:

| Index | Value | Count |
| ----- | ----- | ----- |
| 1 | "aBcD_1-2" | 1 |

The pivot table should contain:

| Command/Events | Reference |
| -------------- | --------- |
| echo ALPHANUM8 | 1 |

### 6.3 Test Case 3: Command String with PATH
The input CSV file contains a command string that has a path that resembles a UNIX path under the default directories. The program should replace the path with the string "PATH" and generate a reference for it. For example, the input dataframe before processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo /usr/bin/python |  |

The input dataframe after processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo PATH | [1] |

The references dataframe should contain:

| Index | Value | Count |
| ----- | ----- | ----- |
| 1 | /usr/bin/python | 1 |

The pivot table should contain:

| Command/Events | Reference |
| -------------- | --------- |
| echo PATH | 1 |

### 6.4 Test Case 4: Command String with NUMERIC
The input CSV file contains a command string that has a number between 5 and 12 digits long that follows the word "echo". The program should replace the number with the string "NUMERIC" and generate a reference for it. For example, the input dataframe before processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo 123456789 |  |

The input dataframe after processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo NUMERIC | [1] |

The references dataframe should contain:

| Index | Value | Count |
| ----- | ----- | ----- |
| 1 | 123456789 | 1 |

The pivot table should contain:

| Command/Events | Reference |
| -------------- | --------- |
| echo NUMERIC | 1 |

### 6.5 Test Case 5: Command String with HOSTNAME
The input CSV file contains a command string that has a valid hostname that follows the regex pattern and the specifications. The program should replace the hostname with the string "HOSTNAME" and generate a reference for it. For example, the input dataframe before processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo p2eavwaabc01.intraPRD.abc.com.sg |  |

The input dataframe after processing:

| Command/Events | Reference |
| -------------- | --------- |
| echo HOSTNAME | [1] |

The references dataframe should contain:

| Index | Value | Count |
| ----- | ----- | ----- |
| 1 | p2eavwaabc01.intraPRD.abc.com.sg | 1 |

The pivot table should contain:

| Command/Events | Reference |
| -------------- | --------- |
| echo HOSTNAME | 1 |
