import numpy as np
import sounddevice as sd
from time import sleep, time
import threading
from queue import Queue
from CircularBuffer import CircularBuffer

class NoiseSoundSource:
    def __init__(self, generator=None, audio_segment = None, duration = 1.0, initial_volume=1.0, sample_rate=44100):
        """
        :param generator: Function that generates numpy array of audio samples (will override audio_samples)
        :param audio_segment: numpy array with audio samles (no need for generator) 
        :param duration: Duration of the pre-generated audio segment
        :param initial_volume: Initial volume as a float multiplier (1.0 = original volume)
        :param sample_rate: Sample rate for the audio
        """
        self.generator = generator
        self.duration = duration
        self.sample_rate = sample_rate
        self.volume = initial_volume
        self.active = True
        self.source_audio_segment__ = audio_segment
        self.current_position = 0
        if self.generator is not None:
            self.source_audio_segment__ = self.generator(self.duration, self.sample_rate)
        self.source_audio_segment = self.source_audio_segment__ * self.volume
        self.source_segment_length = len(self.source_audio_segment__)
        
    def set_volume(self, volume):
        if volume == self.volume:
            return
        self.volume = volume
        self.source_audio_segment = self.source_audio_segment__ * self.volume

    def get_audio_segment(self, duration):
        if not self.active:
            return np.zeros(int(duration * self.sample_rate))
        
        segment_length = int(duration * self.sample_rate)
        
        start_position = self.current_position
        end_position = (self.current_position + segment_length) % self.source_segment_length

        if start_position + segment_length <= self.source_segment_length:
            segment = self.source_audio_segment[start_position:start_position + segment_length]
        else:
            segment = np.concatenate((
                self.source_audio_segment[start_position:],
                self.source_audio_segment[:end_position]
            ))

        self.current_position = end_position
        return segment * self.volume

    def deactivate(self):
        self.active = False

    def activate(self):
        self.active = True