import numpy as np
import sounddevice as sd
from time import sleep, time
import threading
from queue import Queue
from CircularBuffer import CircularBuffer

class NoiseSoundSource:
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