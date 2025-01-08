import subprocess
import time

# List of Python scripts and their respective ports
services = [
    ("auth.py", 8010),
    ("All_vehicles/map_server.py", 8000),
    ("Single_Vehicle/Fetch.py", 8080),
    ("naya/app.py", 8003),
    ("nayasim/sim.py", 8004),
    ("nayaemp/emp.py", 8005),
    ("nayavehicle/vehicle.py", 8006),
    ("nayacomp/comp.py", 8007),
    ("comb_data.py",8008),
    ("nayadriver/driver.py", 8009)
]

processes = []

try:
    for script, port in services:
        # Launch each Python script with the specified port
        p = subprocess.Popen(["python", script, str(port)])
        processes.append(p)
        time.sleep(1)  # Give each process time to start

    # Keep the control script running
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    # On interruption, terminate all running processes
    for p in processes:
        p.terminate()
