import subprocess

# Upgrade pip
subprocess.run(['pip', 'install', '--upgrade', 'pip'])

# Installation der notwendigen Pakete
subprocess.run(['pip', 'install', '--upgrade', 'matplotlib'])
subprocess.run(['pip', 'install', '--upgrade', 'pillow'])
subprocess.run(['pip', 'install', 'scipy==1.12.0'])
subprocess.run(['pip', 'install', '--upgrade', 'scikit-learn'])

