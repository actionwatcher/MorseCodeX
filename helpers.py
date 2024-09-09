import wave
import numpy as np
import math
import ast

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

def volume2value(volume):
    ''' Tk sliders value that goes from top to bottom '''
    slider_value = round(-Amplitude2dB(volume)/0.4)
    return int(max(0, min(100, slider_value)))

def slider2source(slider, obj):
    slider_value = -float(slider.get())*0.4
    obj.volume = dB2Amplitude(slider_value)

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


# Example usage
if __name__ == "__main__":
    import os
    audio_segment, sample_rate = read_wav('qrn.wav')
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
    read_commands = read_file_to_dict('test_commands.txt')
    assert commands == read_commands, f"Original and read dictionaries do not match! {commands} != {read_commands}"
    commands["new_command"] = ("<F5>", (4, "new_param", 10.5))
    file2 = 'test_commands_modified.txt'
    write_dict_to_file(commands, file2)
    read_modified_commands = read_file_to_dict(file2)
    assert commands == read_modified_commands, f"Modified and read dictionaries do not match! {commands} != {read_modified_commands}"
    os.remove(file1)
    os.remove(file2)