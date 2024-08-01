import subprocess
import os

print("hello! This script is working :)")

# Full path to the Pd executable (adjust this as needed)
pd_executable = '/Applications/Pd-0.55-0.app/Contents/Resources/bin/pd'

# Path to the Pd patch
pd_test_path = '/Users/erika/Documents/Github/transforming-collections/prototype-scripts/test_bootscript/test.pd'

# Check if Pd executable exists
if not os.path.isfile(pd_executable):
    raise FileNotFoundError(f"Pd executable not found at {pd_executable}")

# Check if Pd patch file exists
if not os.path.isfile(pd_test_path):
    raise FileNotFoundError(f"Pd patch file not found at {pd_test_path}")

try:
    # Start Pd with the patch in nogui mode
    pd_process = subprocess.Popen([pd_executable,'-nogui', pd_test_path])
    print("Pd has been started successfully.")
except Exception as e:
    print(f"Failed to start Pd: {e}")
    raise

print("can you hear sound??")

# Optionally, wait for a while to let the patch run
import time
time.sleep(10)

# Terminate the Pd process
pd_process.terminate()
