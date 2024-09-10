import platform
import subprocess
from update_version import update_version

def run_pyinstaller():
    # Determine the operating system
    current_os = platform.system()

    # Choose the correct .spec file based on the OS
    if current_os == 'Windows':
        spec_file = 'MorseCodeX_win.spec'
    elif current_os == 'Darwin':  # Darwin is the system name for macOS
        spec_file = 'MorseCodeX_mac.spec'
    elif current_os == 'Linux':
        spec_file = 'MorseCodeX_linux.spec'
    else:
        print(f"Unsupported OS: {current_os}")
        return

    update_version()
    command = ['pyinstaller', '--noconfirm', spec_file]

    try:
        # Run the command and capture the output
        result = subprocess.run(command, check=True, capture_output=True, text=True)

        ## Print output and errors, if any
        print(result.stdout)
        print(result.stderr)

        print(f"PyInstaller successfully ran for {spec_file}")
    except subprocess.CalledProcessError as e:
        # Handle errors if PyInstaller fails
        print(f"PyInstaller failed with error: {e.stderr}")

# Example usage:
run_pyinstaller()
