import subprocess
import sys

try:
    script_filename = "datagen_script.py"  # Use a temporary path or desired location
    user_email = "23ds3000149@ds.study.iitm.ac.in"

    result = subprocess.run([sys.executable, script_filename, user_email], check=True, capture_output=True, text=True)
    print("Script executed successfully")
    print("Output:", result.stdout)
except subprocess.CalledProcessError as e:
    print(f"Error executing script: {e}")
    print("Error Output:", e.stderr)