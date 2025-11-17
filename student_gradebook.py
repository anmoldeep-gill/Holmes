# Skill: Comment the Code
# This program demonstrates File Handling and Array Data Structures.

def analyze_grades(input_file, output_file):
    """
    Reads grades from input_file, analyzes them, and writes
    a report to output_file.
    
    Args:
        input_file (str): The name of the file to read (e.g., 'grades.txt')
        output_file (str): The name of the file to write (e.g., 'report.txt')
    """
    
    # Skill: Use Array Data Structures (a list of dictionaries)
    students = []
    
    # Skill: Perform File Handling (Read)
    try:
        with open(input_file, 'r') as f:
            for line in f:
                # Skill: Perform String Manipulation (.strip(),.split())
                line = line.strip()
                if line:  # Avoid errors from blank lines
                    name, grade_str = line.split(',')
                    
                    # Skill: Use Data Types (dict, str, int)
                    student = {
                        'name': name,
                        'grade': int(grade_str)
                    }
                    students.append(student)
    
    except FileNotFoundError:
        print(f"Error: Input file '{input_file}' not found.")
        return
    except ValueError:
        print(f"Error: Data in '{input_file}' is not formatted correctly.")
        return
    
    if not students:
        print("No student data found in file.")
        return

    # --- Calculations ---
    count = len(students)
    
    # Use a list comprehension to get all grades
    grades_list = [s['grade'] for s in students]
    
    # Skill: Use Data Types, Operators, and Expressions
    total = sum(grades_list)
    average = total / count  # Example of '/' operator
    highest = max(grades_list)
    lowest = min(grades_list)

    # Skill: Perform File Handling (Write)
    try:
        with open(output_file, 'w') as f:
            f.write("--- Student Grade Analysis Report ---\n")
            f.write(f"Total Students: {count}\n")
            # Skill: String Manipulation (f-string formatting)
            f.write(f"Average Grade: {average:.2f}\n") 
            f.write(f"Highest Grade: {highest}\n")
            f.write(f"Lowest Grade: {lowest}\n")

        print(f"Report successfully written to '{output_file}'.")
    
    except IOError:
        print(f"Error: Could not write report to '{output_file}'.")

def main():
    # Skill: Apply Variables and Variable Scope
    input_filename = 'grades.txt'
    output_filename = 'report.txt'
    
    # Skill: Use Sequence Structures
    analyze_grades(input_filename, output_filename)

# Skill: Apply Basic Language Syntax Rules
if __name__ == "__main__":
    main()