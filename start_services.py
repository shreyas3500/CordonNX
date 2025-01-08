# start_services.py
import subprocess
import time

# Start auth.py
subprocess.Popen(["/root/CordonNX/CordonNX/venv/bin/python", "/root/CordonNX/CordonNX/auth.py"])

# Start run_all_services.py
subprocess.Popen(["/root/CordonNX/CordonNX/venv/bin/python", "/root/CordonNX/CordonNX/run_all_services.py"])


while True:
    time.sleep(60)
