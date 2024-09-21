import wave
import numpy as np
import math
import ast
import shutil
import json
import os

def read_wav(file_path):
    with wave.open(file_path, 'rb') as wf:
        sample_rate = wf.getframerate()
        n_channels = wf.getnchannels()
        n_frames = wf.getnframes()
        audio_data = wf.readframes(n_frames)
        audio_segment = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
        if n_channels == 2:
            audio_segment = audio_segment.reshape(-1, 2).mean(axis=1)
    return audio_segment, sample_rate


def band_pass_filter(adata: np.ndarray, bandpass: tuple = (300, 900), sampling_rate: int = 44100) -> np.ndarray:
    # translate bandlimit from Hz to dataindex according to sampling rate and data size
    low_limit_index = int(bandpass[0] * adata.size / sampling_rate)
    high_limit_index = int(bandpass[1] * adata.size / sampling_rate)
    fsig = np.fft.fft(adata)
    fsig[:low_limit_index] = 0
    fsig[high_limit_index:] = 0
    adata_filtered = np.fft.ifft(fsig)
    return np.real(adata_filtered)

def write_wav(file_path, audio_segment, sample_rate):
    # Ensure the audio data is in the correct format
    audio_data = (audio_segment * 32768).astype(np.int16)

    # Create a new wave file
    with wave.open(file_path, 'wb') as wf:
        # Set the parameters for the output file
        wf.setnchannels(1)  # Mono channel
        wf.setsampwidth(2)  # 2 bytes (16 bits)
        wf.setframerate(sample_rate)
        
        # Write the audio data to the file
        wf.writeframes(audio_data.tobytes())

L_min = -40  # Minimum loudness in dB
L_max = 0    # Maximum loudness in dB

def volume2value(volume):
    ''' Tk sliders value that goes from top to bottom '''
    db = Amplitude2dB(volume)
    slider_value = (db - L_min)/(L_max - L_min)
    slider_value = round(100.0*(1 - slider_value))
    return int(max(0, min(100, slider_value)))

def slider2source(slider, obj):
    slider_value = float(100 - slider.get())/100.0
    db = slider_value * (L_max - L_min) + L_min
    obj.volume = dB2Amplitude(db)
    return obj.volume

def dB2Amplitude(db):
    return pow(10.0, db/20.0)

def Amplitude2dB(amplitude):
  return 20.0 * math.log10(max(1.e-6, amplitude))

def genererate_score_multipliers(speed_range):
    min_speed = speed_range[0]
    max_speed = speed_range[1]
    speeds = np.array(range(min_speed, max_speed+1), dtype=np.float32)
    mults = pow((speeds - speeds[0])/(speeds[-1] - speeds[0]), 2) * 7.0 + 1.0
    return mults

def range_checker(lower, upper):
    def binded_checker(val):
        if val.isdigit() and lower <= int(val) <= upper:
            return True
        return False
    return binded_checker

def read_file_to_dict(filename):
    """Reads a text file and converts it into a dictionary with the shortcut and parameters."""
    success = True
    commands_dict = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()
                if line:
                    command, params = line.split(":", 1)
                    command = command.strip().lower()
                    
                    params_list = [param.strip() for param in params.split(",")]

                    # First element is always the shortcut
                    shortcut = params_list[0].upper()
                    # Remaining parameters go into a tuple and evaluated to their correct types
                    params_tuple = tuple(ast.literal_eval(param) for param in params_list[1:])
                    
                    commands_dict[command] = (shortcut, params_tuple)
    except FileNotFoundError:
        success = False

    return success, commands_dict

def write_dict_to_file(commands_dict, filename):
    """Writes a dictionary into a text file."""
    with open(filename, 'w') as file:
        for command, (shortcut, params) in commands_dict.items():
            # Convert the tuple of parameters to a string for writing
            params_str = ', '.join([repr(param) if isinstance(param, str) else str(param) for param in params])
            file.write(f"{command}: {shortcut}, {params_str}\n")

# version update support 
def compare_versions(previous_version, new_version):
    # Split the versions by '.' and convert each part to an integer
    previous_parts = [int(part) for part in previous_version.split('.')]
    new_parts = [int(part) for part in new_version.split('.')]

    # Compare each part
    for prev, new in zip(previous_parts, new_parts):
        if new > prev:
            return 1  # New version is higher
        elif new < prev:
            return -1  # New version is lower
    return 0

# Load JSON data

def apply_updates(current_version, target_version, migrations, src_dir, dst_dir):
    # Get the list of versions between current and target
    version_chain = get_version_chain(current_version, target_version, migrations)

    for version in version_chain:
        changes = migrations[version]
        apply_additions(changes['add'], src_dir, dst_dir)
        apply_deletions(changes['delete'], src_dir, dst_dir)
        apply_modifications(changes['modify'], version, src_dir, dst_dir)
    
    return True

def get_version_chain(current_version, target_version, migrations):
    available_versions = sorted(migrations.keys())  # Ensure versions are sorted for comparison
    version_chain = [ver for ver in available_versions if current_version <= ver <= target_version]
    return version_chain

def apply_additions(additions, src_dir, dst_dir):
    for file_info in additions:
        print(f"Adding file: {file_info['source']} at {file_info['destination']}")
        shutil.copy(os.path.join(src_dir, file_info['source']),
            os.path.join(dst_dir, file_info['destination']))

def apply_deletions(deletions, src_dir, dst_dir):
    for file_info in deletions:
        print(f"Deleting file: {file_info['source']} at {file_info['destination']}")
        try:
            os.remove(filename)
        except OSError:
            pass

def apply_modifications(modifications, version, src_dir, dst_dir):
    for file_info in modifications:
        if version == '0.9.5.0':
            from SessionDB import convert_v0950
            db_name = os.path.join(dst_dir, file_info['destination'])
            log('debug', f"Modifying file: {db_name}")
            convert_v0950(db_name)
        else:
            log('error', "version transition to {version} is not specified")

def update_data(old_version: str, new_version: str, migration_file, src_dir, dst_dir) -> bool:
    if compare_versions(old_version, new_version) < 0:
        log('info', "Data downgrade is not supported")
        return False
    
    if compare_versions(old_version, new_version) == 0:
        log('debug', 'No data upgrade needed')
        return False
    
    # Update data
    try:
        with open(migration_file, "r") as file:
            migrations = json.load(file)

        result = apply_updates(old_version, new_version, migrations, src_dir, dst_dir)
    except Exception as e:
        log('error', e)
        result = False
    log('debug', f'Data update complete with {result}')
    return result


# logging 
from tkinter import messagebox
def null_print(*args):
    pass

log_print = null_print
log_level = 'release' 

def init_log(context: str):
    global log_print
    global log_level
    if context == 'frozen_debug':
        log_print = messagebox.showinfo
        log_level= 'debug'
    elif context == 'frozen_release':
        log_print = messagebox.showinfo
        log_level = 'release'
    else:
        log_level= 'debug'
        log_print = print
    
def log(level: str, *args):
    level = level.lower()
    if level == 'debug' and log_level != 'debug':
        return
    log_print(level, *args)

# Example usage
if __name__ == "__main__":
    import os
    audio_segment, sample_rate = read_wav('configs/qrn.wav')
    # remove first and last 3 seconds
    idx = 3 * sample_rate
    audio_segment = audio_segment[idx:-idx]
    write_wav('output.wav', audio_segment, sample_rate)
    
    # Dictionary read/write test
    commands = {
        "repeat": ("<F7>", (2,)),
        "cq": ("<F1>", (1, "hello", 3.1)),
        "stop": ("<F9>", (0,))
    }
    file1 = 'test_commands.txt'
    write_dict_to_file(commands, file1)
    success, read_commands = read_file_to_dict(file1)
    assert success and commands == read_commands, f"Original and read dictionaries do not match! {commands} != {read_commands}"
    commands["new_command"] = ("<F5>", (4, "new_param", 10.5))
    file2 = 'test_commands_modified.txt'
    write_dict_to_file(commands, file2)
    success, read_modified_commands = read_file_to_dict(file2)
    assert success and commands == read_modified_commands, f"Modified and read dictionaries do not match! {commands} != {read_modified_commands}"
    os.remove(file1)
    os.remove(file2)
    with open('test_migration.json', 'r') as file:
        migrations = json.load(file)
    m = get_version_chain("0.9", "2.5", migrations)
    assert m == ['1.0', '1.1', '2.0']
    update_data("0.9", "1.1", 'test_migration.json', './', './test')
    import random
    random_numbers = random.sample(range(0, 101), 50)
    class test_obj:
        def __init__(self):
            self.volume = -1.0
    class test_slider:
        def __init__(self, n):
            self.n = n
        def get(self):
            return self.n
    for n in random_numbers:
        obj = test_obj()
        slider = test_slider(n)
        vol = slider2source(slider, obj)
        n1 = volume2value(vol)
        assert n == n1, f"Initial: {n}, roundtripped: {n1}, with volume {vol}"
