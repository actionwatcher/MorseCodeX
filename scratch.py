import sounddevice as sd
import numpy as np
from time import sleep, time
import threading
from queue import Queue
from pydub import AudioSegment
from pydub.generators import Sine, WhiteNoise

class SoundSource:
    def __init__(self, generator=None, initial_volume=0):
        """
        :param generator: Function that generates AudioSegment of desired duration
        :param initial_volume: Initial volume in dB
        """
        self.generator = generator
        self.volume = initial_volume
        self.active = True

    def set_volume(self, volume):
        self.volume = volume

    def get_audio_segment(self, duration):
        if not self.active:
            return AudioSegment.silent(duration=duration)
        audio_segment = self.generator(duration)
        return audio_segment + self.volume

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True

class ContinuousPlayer:
    def __init__(self, interval=100):
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
        while self.playing:
            if duration and (time() - start_time) * 1000 >= duration:
                self.playing = False
                break

            mixed_audio = AudioSegment.silent(duration=self.interval)
            for source in self.sources:
                audio_segment = source.get_audio_segment(self.interval)
                mixed_audio = mixed_audio.overlay(audio_segment)
            
            self.queue.put(mixed_audio.raw_data)

    def _play_audio(self):
        stream = sd.OutputStream(samplerate=44100, channels=1, dtype='int16')
        stream.start()
        while self.playing:
            if self.queue.empty():
                continue
            raw_data = self.queue.get()
            audio_data = np.frombuffer(raw_data, dtype=np.int16)
            stream.write(audio_data)

        stream.stop()
        stream.close()

    def stop(self):
        self.playing = False
        if self.mixing_thread:
            self.mixing_thread.join()
        if self.playing_thread:
            self.playing_thread.join()

# Example usage
def generate_morse_code_segment(duration):
    return Sine(1000).to_audio_segment(duration=duration)

def generate_noise_segment(duration):
    return WhiteNoise().to_audio_segment(duration=duration)

morse_source = SoundSource(generator=generate_morse_code_segment, initial_volume=-20)
noise_source = SoundSource(generator=generate_noise_segment, initial_volume=-20)

player = ContinuousPlayer()
player.add_source(noise_source)  # Continuous background noise
player.add_source(morse_source)  # Morse code sound

# Start streaming
player.start(duration=10000)  # Play for 10 seconds

# To stop manually, you can call:
# player.stop()
