import numpy as np
import sounddevice as sd
import soundfile as sf
from time import sleep, time
import threading
from queue import Queue

class SoundSource:
    def __init__(self, audio_segment, sample_rate=44100, initial_volume=1.0):
        """
        :param audio_segment: Numpy array of audio samples
        :param sample_rate: Sample rate for the audio
        :param initial_volume: Initial volume as a float multiplier (1.0 = original volume)
        """
        self.audio_segment = audio_segment * initial_volume
        self.sample_rate = sample_rate
        self.volume = initial_volume
        self.active = True

    @classmethod
    def from_generator(cls, generator, duration, sample_rate=44100, initial_volume=1.0):
        audio_segment = generator(duration, sample_rate)
        return cls(audio_segment, sample_rate, initial_volume)

    @classmethod
    def from_file(cls, file_path, initial_volume=1.0):
        audio_segment, sample_rate = sf.read(file_path, dtype='float32')
        return cls(audio_segment, sample_rate, initial_volume)

    def set_volume(self, volume):
        self.volume = volume
        self.audio_segment = self.audio_segment * self.volume

    def get_audio_segment(self, duration):
        if not self.active:
            return np.zeros(int(duration * self.sample_rate))
        
        segment_length = int(duration * self.sample_rate)
        return np.tile(self.audio_segment, (segment_length // len(self.audio_segment) + 1))[:segment_length]

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True

class ContinuousPlayer:
    def __init__(self, interval=0.1):
        self.sources = []
        self.interval = interval
        self.playing = False
        self.queue = Queue(maxsize=10)  # Limit the queue size to prevent excessive memory usage
        self.mixing_thread = None
        self.playing_thread = None

    def add_source(self, sound_source):
        self.sources.append(sound_source)

    def start(self, duration=None):
        if self.playing:
            return
        self.playing = True

        self.mixing_thread = threading.Thread(target=self._mix_audio, args=(duration,))
        self.playing_thread = threading.Thread(target=self._play_audio)

        self.mixing_thread.start()
        self.playing_thread.start()

    def _mix_audio(self, duration):
        start_time = time()
        sample_rate = 44100
        interval_samples = int(self.interval * sample_rate)

        while self.playing:
            if duration and (time() - start_time) >= duration:
                self.playing = False
                break

            mixed_audio = np.zeros(interval_samples)
            for source in self.sources:
                audio_segment = source.get_audio_segment(self.interval)
                mixed_audio += audio_segment

            mixed_audio = np.clip(mixed_audio, -1.0, 1.0)
            self.queue.put(mixed_audio)
            sleep(self.interval)

    def _play_audio(self):
        sample_rate = 44100

        def callback(outdata, frames, time, status):
            if status:
                print(status)
            if not self.queue.empty():
                mixed_audio = self.queue.get()
                # Ensure the mixed audio has enough frames
                if len(mixed_audio) < frames:
                    outdata[:len(mixed_audio)] = mixed_audio.reshape(-1, 1)
                    outdata[len(mixed_audio):] = 0
                else:
                    outdata[:] = mixed_audio[:frames].reshape(-1, 1)
                    # If mixed_audio has more frames, put the remaining back to the queue
                    self.queue.put(mixed_audio[frames:])
            else:
                outdata.fill(0)  # Fill with silence if no audio is available

        with sd.OutputStream(samplerate=sample_rate, channels=1, dtype='float32', callback=callback):
            while self.playing or not self.queue.empty():
                sleep(0.01)  # Keep the main thread alive and responsive

        sd.stop()

    def stop(self):
        self.playing = False
        if self.mixing_thread:
            self.mixing_thread.join()
        if self.playing_thread:
            self.playing_thread.join()

# Functions to generate Morse code and noise
def generate_morse_code_segment(duration, sample_rate=44100):
    frequency = 1000  # 1000 Hz tone
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False)
    return 0.5 * np.sin(2 * np.pi * frequency * t)

def generate_noise_segment(duration, sample_rate=44100):
    return np.random.normal(0, 0.5, int(sample_rate * duration))

# Example usage
morse_duration = 10  # Duration for the pre-generated Morse code segment
noise_duration = 10  # Duration for the pre-generated noise segment

morse_source = SoundSource.from_generator(generator=generate_morse_code_segment, duration=morse_duration, initial_volume=0.5)
noise_source = SoundSource.from_generator(generator=generate_noise_segment, duration=noise_duration, initial_volume=0.2)

# Load an audio file (replace 'path/to/audio/file.wav' with your actual file path)
file_source = SoundSource.from_file('path/to/audio/file.wav', initial_volume=0.3)

player = ContinuousPlayer()
player.add_source(noise_source)  # Continuous background noise
player.add_source(morse_source)  # Morse code sound
player.add_source(file_source)   # Audio file sound

# Start streaming
player.start(duration=10)  # Play for 10 seconds

# To stop manually, you can call:
# player.stop()
