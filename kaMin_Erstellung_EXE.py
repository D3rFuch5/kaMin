import subprocess

#Installation Pyinstaller
subprocess.run(['pip', 'install','--upgrade', 'pyinstaller'])
# Erstellung EXE
subprocess.run("pyinstaller --noconfirm --windowed --onefile --distpath ./kaMin-Die_k-Means-App --add-data Grafiken/*;Grafiken/ --name kaMin-Die_k-Means-App-Alpha_1_2 --icon Grafiken/logo_k_means.png starte_kaMin.py")