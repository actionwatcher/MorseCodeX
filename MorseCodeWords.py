import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
from tkmacosx import Button
import threading
import shelve
from MorseSound import MorseSound

class MorseTrainerUI:
    def __init__(self, root, morse_sound, compare_function):
        self.root = root
        self.morse_sound = morse_sound
        self.compare_function = compare_function
        self.root.title("CW Training Machine")
        self.root.geometry("800x480")  # 5:3 aspect ratio
        self.score = tk.IntVar(value=0)
        self.load_settings()
        self.create_start_screen()

    def load_settings(self):
        with shelve.open('settings') as settings:
            self.init_speed = tk.IntVar(value=settings.get('init_speed', 27))
            self.max_speed = tk.IntVar(value=settings.get('max_speed', 50))
            self.training_word_count = tk.IntVar(value=settings.get('word_count', 50))
            self.file_path_var = tk.StringVar(value=settings.get('file_path', 'MASTER.SCP'))
            self.volume = settings.get('volume', 50)
            self.softness = settings.get('softness', 33)


    def save_settings(self):
        with shelve.open('settings') as settings:
            settings['init_speed'] = self.init_speed.get()
            settings['max_speed'] = self.max_speed.get()
            settings['word_count'] = self.training_word_count.get()
            settings['file_path'] = self.file_path_var.get()
            settings['volume'] = self.volume
            settings['softness'] = self.softness


    def create_start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        start_frame = ttk.Frame(self.root)
        start_frame.pack(fill="both", expand=True)

        # File selection at the top, aligned to the left
        file_frame = ttk.Frame(start_frame)
        file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(file_frame, text="Select File:").grid(row=0, column=0, padx=5, pady=5)
        self.file_path_entry = ttk.Entry(file_frame, textvariable=self.file_path_var, width=40)
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5)
        self.file_select_button = Button(file_frame, text="Browse", command=self.select_file)
        self.file_select_button.grid(row=0, column=2, padx=5, pady=5)

        content_frame = ttk.Frame(start_frame)
        content_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        selection_frame = ttk.LabelFrame(content_frame, text="Training parameters")
        selection_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(selection_frame, text="Initial Speed (WPM):").grid(row=0, column=0, padx=5, pady=5)
        self.init_speed_entry = ttk.Entry(selection_frame, textvariable=self.init_speed)
        self.init_speed_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Max Speed (WPM):").grid(row=1, column=0, padx=5, pady=5)
        self.max_speed_entry = ttk.Entry(selection_frame, textvariable=self.max_speed)
        self.max_speed_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(selection_frame, text="Training words count:").grid(row=2, column=0, padx=5, pady=5)
        self.training_word_count_entry = ttk.Entry(selection_frame, textvariable=self.training_word_count)
        self.training_word_count_entry.grid(row=2, column=1, padx=5, pady=5)

        self.start_button = Button(selection_frame, text="Start", command=self.start_training)
        self.start_button.grid(row=3, column=0, padx=5, pady=5)
        self.start_button.bind("<Return>", lambda event: self.start_training())
        self.start_button.focus_set()

        self.quit_button = Button(selection_frame, text="Quit", command=self.quit_app)
        self.quit_button.grid(row=3, column=1, padx=5, pady=5)

        self.create_sound_frame(content_frame, row=0, col=1, test_button=True)


    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a file",
            initialdir='.',
            filetypes=(("Text files", "*.txt *.scp"), ("All files", "*.*"))
        )
        if file_path:
            self.file_path_var.set(file_path)

    def create_sound_frame(self, main_frame, row=0, col=1, rowspan=4, test_button=False):
        sound_frame = ttk.LabelFrame(main_frame, text="Sound")
        sound_frame.grid(row=row, column=col, rowspan=rowspan, padx=10, pady=5, sticky="w")

        ttk.Label(sound_frame, text="Volume").grid(row=0, column=0, padx=5, pady=5)
        self.volume_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL, command=self.update_volume)
        self.volume_slider.set(self.volume)
        self.volume_slider.grid(row=1, column=0, padx=5, pady=5)

        ttk.Label(sound_frame, text="Softness").grid(row=0, column=1, padx=5, pady=5)
        self.softness_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL, command=self.update_softness)
        self.softness_slider.set(self.softness)
        self.softness_slider.grid(row=1, column=1, padx=5, pady=5)

        if test_button:
            self.test_volume_button = Button(sound_frame, text="Test Volume", command=self.play_volume_test)
            self.test_volume_button.grid(row=2, column=0, columnspan=2, pady=5)


    def create_start_screen___(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        start_frame = ttk.Frame(self.root)
        start_frame.pack(fill="both", expand=True)
        selection_frame = ttk.Frame(start_frame)
        selection_frame.grid(row=0, column=0)


        ttk.Label(selection_frame, text="Initial Speed (WPM):").grid(row=0, column=0, padx=5, pady=5)
        self.init_speed_entry = ttk.Entry(selection_frame, textvariable=self.init_speed)
        self.init_speed_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(selection_frame, text="Max Speed (WPM):").grid(row=1, column=0, padx=5, pady=5)
        self.max_speed_entry = ttk.Entry(selection_frame, textvariable=self.max_speed)
        self.max_speed_entry.grid(row=1, column=1, padx=5, pady=5)

        self.create_volume_frame(start_frame, test_button = True)

        ttk.Label(selection_frame, text="Select File:").grid(row=4, column=0, padx=5, pady=5)
        self.file_path_var = tk.StringVar(value='MASTER.SCP')
        self.file_path_entry = ttk.Entry(selection_frame, textvariable=self.file_path_var, width=40)
        self.file_path_entry.grid(row=4, column=1, padx=5, pady=5)
        self.file_select_button = Button(selection_frame, text="Browse", command=self.select_file)
        self.file_select_button.grid(row=4, column=2, padx=5, pady=5)

        self.start_button = Button(selection_frame, text="Start", command=self.start_training)
        self.start_button.grid(row=5, column=0, padx=5, pady=5)

        # Bind the Enter key to the start button's command
        self.start_button.bind("<Return>", lambda event: self.start_training())

        self.quit_button = Button(selection_frame, text="Quit", command=self.quit_app)
        self.quit_button.grid(row=5, column=1, padx=5, pady=5)

        # Optionally, focus the start button
        self.max_word_cnt = 2
        self.start_button.focus_set()

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Select a file",
            initialdir='.',  # Set to current working directory
            filetypes=(("Text files", "*.txt *.scp"), ("All files", "*.*"))
        )
        if file_path:
            self.file_path_var.set(file_path)

    def create_main_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.received_cnt = int(0)
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill="both", expand=True)

        data_frame = ttk.LabelFrame(main_frame, text="Current Data")
        data_frame.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.speed_label = ttk.Label(data_frame, text=f"Speed: {self.current_speed} WPM")
        self.speed_label.grid(row=0, column=0, padx=5, pady=5)
        
        self.score_label = ttk.Label(data_frame, text=f"Score: {self.score.get()}")
        self.score_label.grid(row=0, column=1, padx=5, pady=5)

        self.count_label = ttk.Label(data_frame, text=f"Count: {self.received_cnt}")
        self.count_label.grid(row=0, column=2, padx=5, pady=5)

        set_data_frame = ttk.LabelFrame(main_frame, text="Set Data")
        set_data_frame.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        ttk.Label(set_data_frame, text=f"Initial Speed: {self.init_speed.get()} WPM").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(set_data_frame, text=f"Max Speed: {self.max_speed.get()} WPM").grid(row=0, column=1, padx=5, pady=5)

        text_frame = ttk.LabelFrame(main_frame, text="Text")
        text_frame.grid(row=2, column=0, padx=5, pady=5, sticky="ew")

        ttk.Label(text_frame, text="Received:").grid(row=0, column=1, padx=5, pady=5)
        self.received_text = tk.Label(text_frame, height=2, width=25, relief="sunken", anchor="e")
        self.received_text.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(text_frame, text="Sent:").grid(row=0, column=0, padx=5, pady=5)
        self.sent_text = tk.Label(text_frame, height=2, width=25, relief="sunken", anchor="w")
        self.sent_text.grid(row=1, column=0, padx=5, pady=5)

        self.entry_field = ttk.Entry(main_frame)
        self.entry_field.grid(row=3, column=0, padx=5, pady=5)
        self.entry_field.bind("<Return>", self.process_entry)
        self.entry_field.focus_set()

        self.create_volume_frame(main_frame)
        

        self.quit_button = Button(main_frame, text="Quit", command=self.quit_app)
        self.quit_button.grid(row=4, column=0, padx=5, pady=5)
        self.root.bind("<F6>", lambda event: self.get_next_word(delay=1, replay=True))

        self.data_source = DataSource(file_path=self.file_path_var.get(), num_words=int(self.training_word_count.get()))
        self.play_volume_test()
        self.get_next_word(3)

    def update_softness(self, event):
        self.softness = self.softness_slider.get()
        softness_value = max(0, 1.0 - float(self.softness)/100.0) * 0.3
        self.morse_sound.set_rise(softness_value)

    def create_volume_frame(self, main_frame, raw=0, col=1, rowspan = 4, test_button = False):
        sound_frame = ttk.LabelFrame(main_frame, text="Sound")
        sound_frame.grid(row=0, column=1, rowspan=4, padx=10, pady=5, sticky="ns")

        ttk.Label(sound_frame, text="Volume").grid(row=0, column=0, padx=5, pady=5)
        self.volume_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL, command=self.update_volume)
        self.volume_slider.set(self.volume)
        self.volume_slider.grid(row=1, column=0, padx=5, pady=5)

        ttk.Label(sound_frame, text="Softness").grid(row=0, column=1, padx=5, pady=5)
        self.softness_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL, command=self.update_softness)
        #self.softness_slider.set((1.0 - self.morse_sound.get_rise()/0.3) * 100)
        self.softness_slider.set(self.softness)
        self.softness_slider.grid(row=1, column=1, padx=5, pady=5)
        if test_button:
            self.test_volume_button = Button(sound_frame, text="Test Volume", command=self.play_volume_test)
            self.test_volume_button.grid(row=2, column=0, columnspan=2, pady=5)


    def create_results_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        results_frame = ttk.Frame(self.root)
        results_frame.pack(fill="both", expand=True)

        ttk.Label(results_frame, text=f"Final Score: {self.score.get()}").pack(padx=5, pady=5)

        self.restart_button = Button(results_frame, text="Restart", command=self.create_start_screen)
        self.restart_button.pack(padx=5, pady=5)
        self.restart_button.bind("<Return>", lambda event: self.create_start_screen())
        self.restart_button.focus_set()
        self.quit_button = Button(results_frame, text="Exit", command=self.quit_app)
        self.quit_button.pack(padx=5, pady=5)

    def update_volume(self, event):
        self.volume = self.volume_slider.get()
        volume = 1.0 - self.volume / 100.0  # Convert percentage to 0-1 scale and invert
        self.morse_sound.set_volume(volume)

    def play_volume_test(self):
        self.morse_sound.play_string("Vvv")

    def start_training(self):
        self.current_speed = (self.init_speed.get())
        morse_sound.set_speed(float(self.current_speed))
        self.save_settings()
        self.create_main_screen()

    def process_entry(self, event, delay=1):
        received_text = self.entry_field.get().upper()
        self.entry_field.delete(0, tk.END)
        sent_text = self.sent_word.upper()
        score, correctness_mask = self.compare_function(sent_text, received_text)

        self.score.set(self.score.get() + score)
        self.received_cnt += 1
        
        if score == len(sent_text):
            c = 'green'
            self.current_speed = min(self.current_speed + 1, self.max_speed.get())
        else:
            c = 'red'
            self.current_speed = max(self.current_speed - 1, self.init_speed.get())
        self.received_text.config(text=received_text, fg=c)
        self.sent_text.config(text=sent_text)
        morse_sound.set_speed(float(self.current_speed))

        self.update_data_frame()
        self.get_next_word(delay)
    
    def update_data_frame(self):
        self.speed_label.config(text=f"Speed: {self.current_speed} WPM")
        self.score_label.config(text=f"Score: {self.score.get()}")
        self.count_label.config(text=f"Count: {self.received_cnt}")

    def get_next_word(self, delay, replay=False):
        if replay == False:
            self.sent_word = self.data_source.get_next_word()
            if not self.sent_word:
                self.create_results_screen()
                return
        threading.Timer(delay, self.morse_sound.play_string, args=[self.sent_word]).start()

    def quit_app(self):
        self.save_settings()
        self.root.quit()

import random

class DataSource:
    def __init__(self, file_path='MASTER.SCP', num_words=50):
        self.words = self._load_words(file_path)
        self.num_words = num_words
        self.reset()

    def _load_words(self, file_path):
        words = []
        try:
            with open(file_path, 'r') as file:
                for line in file:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        words.append(line)
        except FileNotFoundError:
            print(f"File {file_path} not found.")
        return words
    
    def reset(self):
        self.selected_words = random.sample(self.words, k=min(self.num_words, len(self.words)))
        self.index = 0

    def get_next_word(self):
        if self.index >= len(self.selected_words):
            self.index = 0
            return None
        word = self.selected_words[self.index]
        self.index += 1
        return word

# Example usage
# data_source = DataSource(file_path='MASTER.SCP', num_words=10)
# print(data_source.get_next_word())


def compare(sent_word, received_word):
    
    # Compare characters in lowercase
    score = len([1 for s, r in zip(sent_word, received_word) if s == r])
    correctness_mask = [s == r for s, r in zip(sent_word, received_word)]

    # Extend the correctness mask if the received word is longer
    if len(correctness_mask) < len(received_word):
        correctness_mask.extend([False] * (len(received_word) - len(correctness_mask)))

    return score, correctness_mask


# Create main application window
root = tk.Tk()
morse_sound = MorseSound()  # Assuming MorseSound is defined elsewhere
app = MorseTrainerUI(root, morse_sound, compare)
root.mainloop()
