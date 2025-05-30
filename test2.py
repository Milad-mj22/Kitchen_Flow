import subprocess
import time
import os

# Set the base path for user data directories
base_user_data_path ="chrome_user_data"

# Number of Chrome instances to open
number_of_windows = 5

# The URL to open in each window

url = "https://web.whatsapp.com/"

# Chrome executable path (adjust if needed)
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"  # or use full path if not in PATH

# Ensure the profile directory exists
os.makedirs(base_user_data_path, exist_ok=True)

# Launch Chrome instances with different user profiles
for i in range(number_of_windows):
    user_data_dir = os.path.join(base_user_data_path, f"profile_{i}")
    os.makedirs(user_data_dir, exist_ok=True)

    subprocess.Popen([
        chrome_path,
        f"--user-data-dir={user_data_dir}",
        "--new-window",
        url
    ])
    time.sleep(0.5)  # Optional: small delay between launches
