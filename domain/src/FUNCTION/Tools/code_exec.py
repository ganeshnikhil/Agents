import sys
import subprocess
import importlib
import os
from io import StringIO

class CodeExecutor:
    def __init__(self, required_libraries=None):
        """Initialize the class with a list of required libraries."""
        self.required_libraries = required_libraries or ['pandas', 'numpy', 'matplotlib']
        self.flag_file = './DATA/libraries_installed.txt'

    def get_pip_command(self):
        """Returns the appropriate pip command based on the operating system."""
        if sys.platform == "win32":
            return "pip"  # Windows uses pip
        else:
            return "pip3"  # macOS/Linux uses pip3

    def check_and_install_libraries(self):
        """
        Checks if required libraries are installed and installs any missing ones.
        """
        # Step 1: Check if the flag file exists
        if os.path.exists(self.flag_file) and os.path.getsize(self.flag_file) != 0:
            print("Libraries are already installed.")
            return  # Libraries are already installed, skip installation

        # If flag file does not exist, install missing libraries
        for library in self.required_libraries:
            try:
                importlib.import_module(library)
            except ImportError:
                print(f"Library '{library}' not found. Installing...")
                pip_command = self.get_pip_command()
                subprocess.check_call([sys.executable, "-m", "pip", "install", library])

        # Step 2: Create the flag file to indicate libraries are installed
        with open(self.flag_file, 'w') as f:
            f.write("Libraries installed successfully.")

    def execute_code(self, code):
        """
        Executes the dynamically generated code and ensures that required libraries are installed.
        Args:
            code (str): The Python code to execute.
        
        Returns:
            dict: Dictionary containing the result or error message.
        """
        # Step 1: Install missing libraries if required
        self.check_and_install_libraries()

        # Initialize result dictionary
        result = {
            'output': None,
            'error': None,
        }

        # Step 2: Capture the output of the code execution
        old_stdout = sys.stdout
        sys.stdout = StringIO()

        try:
            # Step 3: Execute the code in a clean context (no interference from the global scope)
            exec_globals = {}
            exec_locals = {}
            exec(code, exec_globals, exec_locals)

            # Step 4: Capture the output from print statements or results
            output = sys.stdout.getvalue()

            # Step 5: Return the result or output
            if not output:
                result['output'] = str(exec_locals)  # If no output, return the result of execution
            else:
                result['output'] = output
        
        except SyntaxError as e:
            result['error'] = f"Syntax Error: {e.msg} on line {e.lineno}"
        except NameError as e:
            result['error'] = f"Name Error: {e.args}"
        except Exception as e:
            result['error'] = f"Error during execution: {str(e)}"
        finally:
            sys.stdout = old_stdout  # Restore the original stdout

        return result

# Example usage:
if __name__ == "__main__":
    executor = CodeExecutor()  # Initialize with default libraries
    code_to_run = """
import pandas as pd
import numpy as np
data = pd.DataFrame({'a': np.random.randn(100), 'b': np.random.randn(100)})
print(data.head())
"""
    result = executor.execute_code(code_to_run)
    if result['error']:
        print(f"Error: {result['error']}")
    else:
        print(f"Output:\n{result['output']}")
