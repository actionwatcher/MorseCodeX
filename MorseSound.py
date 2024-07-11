import numpy as np
import sounddevice as sd

class MorseSound:
    MORSE_CODE_DICT = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.',
        'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
        'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.',
        'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
        'Y': '-.--', 'Z': '--..',
        '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....',
        '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
        ',': '--..--', '.': '.-.-.-', '?': '..--..', '/': '-..-.', '-': '-....-',
        '(': '-.--.', ')': '-.--.-', '=': '-...-', 'AR': '.-.-.', 'BT': '-...-', 'SK': '...-.-'
    }

    def __init__(self, wpm=20, frequency=650, sample_rate=44100, rise_time=0.1):
        self.sample_rate = sample_rate  # Standard audio sample rate in Hz
        self.frequency = frequency
        self.rise_time = rise_time  # Default rise time
        self.volume = 0.5
        self.set_speed(wpm)
    
    def set_speed(self, wpm, slowdown=0):
        # Calculate durations based on WPM
        self.dit_duration = 1.2 / wpm
        self.dah_duration = 3 * self.dit_duration
        self.element_gap = self.dit_duration
        self.symbol_gap = self.dah_duration + slowdown * self.dit_duration
        self.word_gap = 7 * self.dit_duration
        self.wpm = wpm
        
        # Generate the arrays with the current frequency and volume
        self._generate_arrays()
    
    def set_frequency(self, frequency):
        self.frequency = frequency
        # Regenerate the arrays with the new frequency
        self._generate_arrays()

    def set_volume(self, volume):
        self.volume = volume
        # Regenerate the arrays with the new volume
        self._generate_arrays()

    def get_volume(self):
        return self.volume

    def set_rise(self, rise_time):
        self.rise_time = rise_time
        # Regenerate the arrays with the new rise time
        self._generate_arrays()

    def get_rise(self):
        return self.rise_time

    def _generate_arrays(self):
        # Generate time vectors for each element
        t_dit = np.linspace(0, self.dit_duration, int(self.dit_duration * self.sample_rate), endpoint=False)
        t_dah = np.linspace(0, self.dah_duration, int(self.dah_duration * self.sample_rate), endpoint=False)
        
        # Generate the sine wave for each element
        dit_wave = np.sin(2 * np.pi * self.frequency * t_dit)
        dah_wave = np.sin(2 * np.pi * self.frequency * t_dah)
        
        # Apply rise time using a cosine function
        rise_samples = int(self.rise_time * len(t_dit))  # Corrected rise samples calculation

        if rise_samples > 0:
            window_dit = np.ones(len(t_dit))
            window_dah = np.ones(len(t_dah))
            # Apply rise and fall for dit
            window_dit[:rise_samples] = 0.5 * (1 - np.cos(np.pi * np.arange(rise_samples) / rise_samples))
            window_dit[-rise_samples:] = 0.5 * (1 - np.cos(np.pi * np.arange(rise_samples, 0, -1) / rise_samples))
            dit_wave *= window_dit
            # Apply rise and fall for dah
            window_dah[:rise_samples] = 0.5 * (1 - np.cos(np.pi * np.arange(rise_samples) / rise_samples))
            window_dah[-rise_samples:] = 0.5 * (1 - np.cos(np.pi * np.arange(rise_samples, 0, -1) / rise_samples))
            dah_wave *= window_dah

        self.dit_array = self.volume * dit_wave
        self.dah_array = self.volume * dah_wave
        
        # Generate silence arrays for gaps
        self.element_gap_array = np.zeros(int(self.element_gap * self.sample_rate))
        self.symbol_gap_array = np.zeros(int(self.symbol_gap * self.sample_rate))
        self.word_gap_array = np.zeros(int(self.word_gap * self.sample_rate))
    
    def get_speed(self):
        return self.wpm

    def get_frequency(self):
        return self.frequency

    def get_durations(self):
        return {
            "dit_duration": self.dit_duration,
            "dah_duration": self.dah_duration,
            "element_gap": self.element_gap,
            "symbol_gap": self.symbol_gap,
            "word_gap": self.word_gap
        }

    def get_arrays(self):
        return {
            "dit_array": self.dit_array,
            "dah_array": self.dah_array,
            "element_gap_array": self.element_gap_array,
            "symbol_gap_array": self.symbol_gap_array,
            "word_gap_array": self.word_gap_array
        }

    def play_string(self, message):
        morse_code_list = self._convert_to_morse(message)
        if morse_code_list:
            signal = self._generate_signal(morse_code_list)
            sd.play(signal, self.sample_rate)
            sd.wait()
    
    def _convert_to_morse(self, message):
        morse_code = []
        i = 0
        while i < len(message):
            if message[i] == '<':  # Detect start of a prosign
                end = message.find('>', i)
                if end != -1:
                    prosign = message[i+1:end]
                    if prosign in self.MORSE_CODE_DICT:
                        morse_code.append(self.MORSE_CODE_DICT[prosign])
                    i = end
            elif message[i] == ' ':
                morse_code.append(' ')
            else:
                char = message[i].upper()
                if char in self.MORSE_CODE_DICT:
                    morse_code.append(self.MORSE_CODE_DICT[char])
            i += 1
        return morse_code  # Return list of Morse code strings
    
    def _generate_signal(self, morse_code_list):
        signal = []
        for symbol in morse_code_list:
            if symbol == ' ':
                signal.extend(self.word_gap_array)
            else:
                for i, element in enumerate(symbol):
                    if element == '.':
                        signal.extend(self.dit_array)
                    elif element == '-':
                        signal.extend(self.dah_array)
                    if i < len(symbol) - 1:  # Add element gap if not the last element
                        signal.extend(self.element_gap_array)
                signal.extend(self.symbol_gap_array)
        if len(signal) == 0:
            return np.array([])  # Return an empty array if no valid Morse code is generated
        return np.concatenate([np.array(signal)])  # Ensure signal is a list of arrays