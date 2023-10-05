# python3 brut.py

import os
import subprocess


for x in range(4,8):
    for y in range(8):
        for z in range(8):
            # Execute chmod command
            # magic bit : 0, 1 or 4 lol
            os.system(f'sudo chmod 0{x}{y}{z} fiveNine/handshake.exe')

            # Run python3 command and get its output
            result = subprocess.run(['python3', 'Ecorp.py', 'share'], stdout=subprocess.PIPE)
            output = result.stdout.decode('utf-8').strip()
            print(output)
            print(x, y, z)