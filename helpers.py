import wave
import numpy as np

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
    return int(max(0, (1.0 - volume) * 100))

def slider2obj(slider, obj):
    slider_value = slider.get()
    obj.volume = max(0, 1.0 - float(slider_value)/100.0)

# Example usage
if __name__ == "__main__":
    audio_segment, sample_rate = read_wav('qrn.wav')
    # remove first and last 3 seconds
    idx = 3 * sample_rate
    audio_segment = audio_segment[idx:-idx]
    write_wav('output.wav', audio_segment, sample_rate)