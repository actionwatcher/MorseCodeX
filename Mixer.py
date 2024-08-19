import numpy as np
import sounddevice as sd
import threading
from CircularBuffer import CircularBuffer
from time import sleep

class Mixer:
    def __init__(self, sample_rate=44100, interval=0.1):
        self.sources = []
        self.interval = interval
        self.sample_rate = sample_rate
        self.playing = False
        self.queue = CircularBuffer(self.sample_rate)  # Limit the queue size to prevent excessive memory usage
        self.interval_samples = int(self.interval * sample_rate)
        self.mixing_thread = None
        self.playing_thread = None

    def add_source(self, sound_source):
        self.sources.append(sound_source)

    def start(self):
        if self.playing:
            return
        self.playing = True
        self.mixing_thread = threading.Thread(target=self._mix_audio)
        self.playing_thread = threading.Thread(target=self._play_audio)
        self.mixing_thread.start()
        self.playing_thread.start()

    def _mix_audio(self):
        while self.playing:
            mixed_audio = np.zeros(self.interval_samples)
            for source in self.sources:
                if not source.active:
                    continue
                audio_segment = source.get_audio_segment(self.interval)
                #if mixed_audio.shape == audio_segment.shape:
                mixed_audio += audio_segment
            self.queue.put(mixed_audio)

    def _play_audio(self):
        def callback(outdata, frames, time, status):
            outdata[:] = self.queue.get(frames).reshape(-1, 1)

        with sd.OutputStream(samplerate=self.sample_rate, channels=1, dtype='float32', callback=callback):
            while self.playing or not self.queue.is_empty():
                sleep(0.001)  # Keep the main thread alive and responsive
        sd.stop()

    def stop(self):
        self.playing = False
        if self.mixing_thread:
            self.mixing_thread.join()
        if self.playing_thread:
            self.playing_thread.join()
