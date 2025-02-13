import os
import subprocess

# Required: Install PyInstaller before using this script
# Install with: pip install pyinstaller

# This script is used to create a command alias (`ntk`) for running a Python module (`ntk`) more easily.

# To generate an executable using PyInstaller, use the following command:
# python -m PyInstaller --onefile --console .\ntk\installer.py -n n

if __name__ == "__main__":
    subprocess.run(['python', '-m', 'pip', 'install',  'next-theme-kit'])

    # Set up a command alias: 'ntk' will execute 'python -m ntk' with any passed arguments
    os.system("doskey ntk=python -m ntk $*")

    # Open a new command prompt window and keep it open
    os.system("cmd /k")
