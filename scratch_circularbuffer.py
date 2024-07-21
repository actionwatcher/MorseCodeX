import numpy as np
import sounddevice as sd
from time import sleep, time
import threading
from queue import Queue
from CircularBuffer import CircularBuffer

class SoundSource:
    def __init__(self, generator, duration, initial_volume=1.0, sample_rate=44100):
        """
        :param generator: Function that generates numpy array of audio samples
        :param duration: Duration of the pre-generated audio segment
        :param initial_volume: Initial volume as a float multiplier (1.0 = original volume)
        :param sample_rate: Sample rate for the audio
        """
        self.generator = generator
        self.duration = duration
        self.sample_rate = sample_rate
        self.volume = initial_volume
        self.active = True
        self.audio_segment = self.generator(self.duration, self.sample_rate) * self.volume

    def set_volume(self, volume):
        self.volume = volume
        self.audio_segment = self.generator(self.duration, self.sample_rate) * self.volume

    def get_audio_segment(self, duration):
        if not self.active:
            return np.zeros(int(duration * self.sample_rate))
        
        #segment_length = int(duration * self.sample_rate)
        return self.generator(duration, self.sample_rate) * self.volume

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True

class ContinuousPlayer:
    def __init__(self, interval=0.1):
        self.sources = []
        self.interval = interval
        self.playing = False
        self.queue = CircularBuffer(44100)  # Limit the queue size to prevent excessive memory usage
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

            #mixed_audio = np.clip(mixed_audio, -1.0, 1.0)
            self.queue.put(mixed_audio)


    def _play_audio(self):
        sample_rate = 44100

        def callback(outdata, frames, time, status):
            outdata[:] = self.queue.get(frames).reshape(-1, 1)

        with sd.OutputStream(samplerate=sample_rate, channels=1, dtype='float32', callback=callback):
            while self.playing or not self.queue.is_empty():
                sleep(0.001)  # Keep the main thread alive and responsive

        sd.stop()

    def stop(self):
        self.playing = False
        if self.mixing_thread:
            self.mixing_thread.join()
        if self.playing_thread:
            self.playing_thread.join()

# Functions to generate Morse code and noise
t = [0]
def generate_morse_code_segment(duration, sample_rate=44100):
    frequency = 1000  # 1000 Hz tone
    global t
    t = np.linspace(0, duration, int(sample_rate * duration), endpoint=False) + t[-1]
    return (0.5 * np.sin(2 * np.pi * frequency * t)) #.astype(np.float32)

def generate_noise_segment1(duration, sample_rate=44100):
    if not hasattr(generate_noise_segment, 'data'):
        generate_noise_segment.data = np.random.normal(0, 0.5, int(sample_rate * duration)).astype(np.float32)
    return generate_noise_segment.data

def generate_noise_segment(duration, sample_rate=44100):
    return np.random.normal(0, 0.5, int(sample_rate * duration))

# Example usage
morse_duration = 10  # Duration for the pre-generated Morse code segment
noise_duration = 10  # Duration for the pre-generated noise segment

morse_source = SoundSource(generator=generate_morse_code_segment, duration=morse_duration, initial_volume=0.5)
noise_source = SoundSource(generator=generate_noise_segment, duration=noise_duration, initial_volume=0.2)



player = ContinuousPlayer()
player.add_source(noise_source)  # Continuous background noise
player.add_source(morse_source)  # Morse code sound

# Start streaming
player.start(duration=5)  # Play for 10 seconds

# To stop manually, you can call:
# player.stop()
