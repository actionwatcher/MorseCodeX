import tkinter as tk
from tkinter import ttk, filedialog
from tkinter import messagebox
import platform
if platform.system() == 'Darwin':
    from tkmacosx import Button
    gLeftButton = '<ButtonRelease-2>'
else:
    Button = tk.Button
    gLeftButton = '<ButtonRelease-3>'
import threading
import os
from datetime import datetime, timedelta
import shelve
from SessionDB import Session, SessionDB
from NoiseSoundSource import NoiseSoundSource
from Mixer import Mixer
from MorseSoundSource import MorseSoundSource
from DataSource import DataSource
import numpy as np
import helpers
import time
import csv
    

class MorseCodeXUI:
    shortcuts = {'T':'0', 'A':'1', 'N':'9'}
    speed_range = [10, 65] #WPM
    score_multipliers = helpers.genererate_score_multipliers(speed_range)

    def __init__(self, root, compare_function, base_path, data_path, user_path):
        self.root = root
        self.root.protocol("WM_DELETE_WINDOW", self.quit_app)
        self.root.createcommand("::tk::mac::Quit", self.quit_app)
        self.base_path = base_path
        self.data_path = data_path
        self.user_path = user_path
        self.compare_function = compare_function
        self.root.title("MorseCodeX: code mastery for contests and beyond")
        self.load_settings()
        self.root.geometry(f"{self.ui_width}x{self.ui_height}")
        self.session_db = SessionDB(os.path.join(self.user_path, 'sessions.db'))
        self.t = [0]
        audio_segment, sample_rate = helpers.read_wav(os.path.join(base_path, 'qrn.wav')) # this file will govern sample rate
        self.player = Mixer(sample_rate=sample_rate)
        morse_file = os.path.join(self.base_path, "morse_table.json")
        self.morse_source = MorseSoundSource(morse_mapping_filename = morse_file, wpm=self.init_speed.get(), frequency=self.frequency, rise_time=self.rise_time, volume=self.cw_volume)
        self.player.add_source(self.morse_source)
        qrm_freq = np.random.choice([*range(100, 360, 20), *range(900, 1060, 20)])
        self.qrm_source = MorseSoundSource(morse_mapping_filename = morse_file, wpm=35, frequency=qrm_freq, rise_time=self.rise_time, volume=self.qrm_volume, queue_sz=1)
        self.player.add_source(self.qrm_source)
        
        noise_duration=float(len(audio_segment))/sample_rate
        self.qrn_source = NoiseSoundSource(audio_segment=audio_segment, sample_rate=sample_rate, 
                                       duration=noise_duration, initial_volume=self.qrn_volume)
        self.player.add_source(self.qrn_source)  # qrn.wav
        white_noise = np.random.normal(0, 1.0, int(sample_rate * noise_duration))
        white_noise = helpers.band_pass_filter(white_noise, sampling_rate=sample_rate)
        self.hfnoise_source = NoiseSoundSource(audio_segment=white_noise, duration=noise_duration, 
                                                   sample_rate=sample_rate, initial_volume=self.hfnoise_volume)
        self.player.add_source(self.hfnoise_source)
        
        self.start_enabled = True
        self.speed_increase = True
        self.qrm_thread = []
        self.create_start_screen()

    def load_settings(self):
        with shelve.open(os.path.join(self.user_path,'settings')) as settings:
            self.init_speed = tk.IntVar(value=settings.get('init_speed', 27))
            self.max_speed = tk.IntVar(value=settings.get('max_speed', 50))
            self.training_word_count = tk.IntVar(value=settings.get('word_count', 55))
            self.data_source_file = tk.StringVar(value=settings.get('data_source_file', 'MASTER.SCP'))
            self.use_challenge = tk.BooleanVar(value=settings.get('challenge', False))
            self.data_source_dir = settings.get('data_source_dir', self.data_path)
            self.cw_volume = settings.get('cw_volume', 0.5)
            self.softness = settings.get('softness', 33)
            self.hfnoise_volume = settings.get('hfnoise_volume', 0.33)
            self.ui_width = settings.get('ui_width',808)
            self.ui_height =settings.get('ui_height', 500)
            self.pre_msg_chk = tk.BooleanVar(value=settings.get('pre_msg', False))
            self.tone = settings.get('tone', 50)
            self.generate_ser_num = tk.BooleanVar(value=settings.get('ser_num', False))
            self.generate_rst = tk.BooleanVar(value=settings.get('rst', False))
            self.qrn_volume = settings.get('qrn_volume', 0)
            self.qrm_volume = settings.get('qrm_volume', 0)
            self.sort_by = settings.get('sort_by', 'score')
            self.sort_inverted = settings.get('sort_inverted', False)


    def save_settings(self):
        with shelve.open(os.path.join(self.user_path,'settings')) as settings:
            settings['init_speed'] = self.init_speed.get()
            settings['max_speed'] = self.max_speed.get()
            settings['word_count'] = self.training_word_count.get()
            settings['data_source_file'] = self.data_source_file.get()
            settings['challenge'] = self.use_challenge.get()
            settings['data_source_dir'] = self.data_source_dir
            settings['cw_volume'] = self.morse_source.volume
            settings['softness'] = self.softness
            settings['hfnoise_volume'] = self.hfnoise_source.volume
            settings['ui_width'] = self.ui_width
            settings['ui_height'] = self.ui_height
            settings['pre_msg'] = self.pre_msg_chk.get()
            settings['tone'] = self.tone
            settings['ser_num'] = self.generate_ser_num.get()
            settings['rst'] = self.generate_rst.get()
            settings['qrm_volume'] = self.qrm_source.volume
            settings['qrn_volume'] = self.qrn_source.volume 
            settings['sort_by'] = self.sort_by
            settings['sort_inverted'] = self.sort_inverted
            
    def create_start_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        start_frame = ttk.Frame(self.root)
        start_frame.pack(fill="both", expand=True)

        # File selection at the top, aligned to the left
        file_frame = ttk.Frame(start_frame)
        file_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(file_frame, text="Select File:").grid(row=0, column=0, padx=5, pady=5)
        self.file_path_entry = ttk.Entry(file_frame, textvariable=self.data_source_file, width=40)
        self.file_path_entry.grid(row=0, column=1, padx=5, pady=5)
        self.file_select_button = Button(file_frame, text="Browse", command=self.select_source_file)
        self.file_select_button.grid(row=0, column=2, padx=5, pady=5)
        checkbox1 = ttk.Checkbutton(file_frame, text="Challenge me", variable=self.use_challenge)
        checkbox1.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        content_frame = ttk.Frame(start_frame)
        content_frame.grid(row=1, column=0, padx=5, pady=5, sticky="w")

        selection_frame = ttk.LabelFrame(content_frame, text="Training parameters")
        selection_frame.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        ttk.Label(selection_frame, text="Min/Initial Speed (WPM):").grid(row=0, column=0, padx=5, pady=5)
        speed_checker = helpers.range_checker(self.speed_range[0], self.speed_range[1])
        validate_speed_command = root.register(speed_checker)
        self.init_speed_entry = tk.Spinbox(selection_frame, from_=self.speed_range[0], to=self.speed_range[1],
                                        wrap=False, textvariable=self.init_speed,
                                        validate="key", validatecommand=(validate_speed_command, '%P')
                                        )
        self.init_speed_entry.grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(selection_frame, text="Max Speed (WPM):").grid(row=1, column=0, padx=5, pady=5)
        self.max_speed_entry = tk.Spinbox(selection_frame, from_=self.speed_range[0], to=self.speed_range[1],
                                        wrap=False, textvariable=self.max_speed,
                                        validate="key", validatecommand=(validate_speed_command, '%P')
                                        )
        self.max_speed_entry.grid(row=1, column=1, padx=5, pady=5)

        counts = [5, 8, 13, 21, 34, 55, 89, 144, 233, 377]
        count_checker = helpers.range_checker(counts[0], counts[-1])
        validate_count_command = root.register(count_checker)
        ttk.Label(selection_frame, text="Training messages count:").grid(row=2, column=0, padx=5, pady=5)
        temp = self.training_word_count.get() # this spinbox bug - the default value is not set but overwritten
        self.training_word_count_entry = tk.Spinbox(selection_frame, values=counts,
                                                    wrap=False, textvariable=self.training_word_count,
                                                    validate="key", validatecommand=(validate_count_command, '%P')
                                                    )
        self.training_word_count.set(temp)
        self.training_word_count_entry.grid(row=2, column=1, padx=5, pady=5)

        self.start_button = Button(selection_frame, text="Start", command=self.start_training)
        self.start_button.grid(row=4, column=0, padx=5, pady=5)
        self.start_button.bind("<Return>", lambda event: self.start_training())
        self.start_button.focus_set()

        self.quit_button = Button(selection_frame, text="Quit", command=self.quit_app)
        self.quit_button.grid(row=4, column=1, padx=5, pady=5)

        self.create_sound_frame(content_frame, row=0, col=1, test_button=True)


    def select_source_file(self):
        selected_file = filedialog.askopenfilename(
            title="Select a file",
            initialdir=self.data_source_dir,
            filetypes=(("Text files", "*.txt"), ("SCP", "*.scp"), ("All files", "*.*"))
        )
        if selected_file:
            selected_dir, selected_file = os.path.split(selected_file)
            self.data_source_file.set(selected_file)
            self.data_source_dir = selected_dir

    def create_sound_frame(self, main_frame, row=0, col=1, rowspan=4, test_button=False):
        sound_frame = ttk.LabelFrame(main_frame, text="Sound")
        sound_frame.grid(row=row, column=col, rowspan=rowspan, padx=10, pady=5, sticky="ns")
        volume_col, softness_col, tone_col,noise_col,qrn_col,qrm_col = range(6)
        
        ttk.Label(sound_frame, text="Volume").grid(row=0, column=volume_col, padx=5, pady=5)
        volume_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL)
        volume_slider.bind("<ButtonRelease-1>", lambda s: helpers.slider2source(volume_slider, self.morse_source))
        volume_slider.set(helpers.volume2value(self.morse_source.volume))
        volume_slider.grid(row=1, column=volume_col, padx=5, pady=5)

        ttk.Label(sound_frame, text="Soft").grid(row=0, column=softness_col, padx=5, pady=5)
        self.softness_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL, command=self.update_softness)
        self.softness_slider.set(self.softness)
        self.softness_slider.grid(row=1, column=softness_col, padx=5, pady=5)

        ttk.Label(sound_frame, text="Tone").grid(row=0, column=tone_col, padx=5, pady=5)
        self.tone_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL, command=self.update_tone)
        self.tone_slider.set(self.tone)
        self.tone_slider.grid(row=1, column=tone_col, padx=5, pady=5)

        ttk.Label(sound_frame, text="Noise").grid(row=0, column=noise_col, padx=5, pady=5)
        noise_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL)
        noise_slider.bind("<ButtonRelease-1>", lambda s: helpers.slider2source(noise_slider, self.hfnoise_source))
        noise_slider.set(helpers.volume2value(self.hfnoise_source._volume))
        noise_slider.grid(row=1, column=noise_col, padx=5, pady=5)

        ttk.Label(sound_frame, text="QRN").grid(row=0, column=qrn_col, padx=5, pady=5)
        qrn_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL)
        qrn_slider.bind("<ButtonRelease-1>", lambda s: helpers.slider2source(qrn_slider, self.qrn_source))
        qrn_slider.set(helpers.volume2value(self.qrn_source._volume))
        qrn_slider.grid(row=1, column=qrn_col, padx=5, pady=5)

        ttk.Label(sound_frame, text="QRM").grid(row=0, column=qrm_col, padx=5, pady=5)
        qrm_slider = ttk.Scale(sound_frame, from_=0, to=100, orient=tk.VERTICAL)
        qrm_slider.bind("<ButtonRelease-1>", lambda s: helpers.slider2source(qrm_slider, self.qrm_source))
        qrm_slider.set(helpers.volume2value(self.qrm_source.volume))
        qrm_slider.grid(row=1, column=qrm_col, padx=5, pady=5)

        if test_button:
            # # Add checkboxes to the sound_frame
            chk_frame = ttk.LabelFrame(sound_frame, text="Message options")
            #chk_frame = ttk.Frame(sound_frame)
            chk_frame.grid(row=2, column=0, rowspan=1, columnspan=6, padx=10, pady=5, sticky="we")
            checkbox2 = ttk.Checkbutton(chk_frame, text="SerNumber", variable=self.generate_ser_num)
            checkbox2.grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
            
            checkbox1 = ttk.Checkbutton(chk_frame, text="Pre message", variable=self.pre_msg_chk)
            checkbox1.grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)

            checkbox3 = ttk.Checkbutton(chk_frame, text="RST", variable=self.generate_rst)
            checkbox3.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

            test_sound_button = Button(sound_frame, text="Test Sound", command=self.play_volume_test)
            test_sound_button.grid(row=6, column=0, pady=5, columnspan=6, sticky=tk.W + tk.E)

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
        
        self.current_session = Session(date=datetime.now().isoformat())
        self.score_label = ttk.Label(data_frame, text=f"Score: {self.current_session.score}")
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

        self.create_sound_frame(main_frame, row=0, col=1, rowspan=3)
        

        stop_button = Button(main_frame, text="Stop", command=self.create_session_results_screen)
        stop_button.grid(row=4, column=0, padx=5, pady=5)
        
        self.root.bind("<F7>", lambda event: self.play_word(delay=1, replay=True))
        self.load_challenges()

        self.data_source = DataSource(file_path=os.path.join(self.data_source_dir, self.data_source_file.get()), num_words=int(self.training_word_count.get()), 
                                      pre_message=self.pre_msg_chk.get(), rst = self.generate_rst.get(), serial=self.generate_ser_num.get(),
                                      challenges=self.challenges, challenge_frac=0.25)
        self.player.start()
        self.morse_source.play_string("vvv")
        self.play_word(3)
        self.run_qrm_thread = True # yes, always start. when qrm_source is inactive play_string does nothing, thus thread will be mostly idle(for now)
        def qrm_sender():
            self.qrm_source.play_string("cq test nu6n")
            time.sleep(5)
            while(self.run_qrm_thread):
                self.qrm_source.play_string()
                time.sleep(6)
        self.qrm_thread = threading.Timer(3, qrm_sender)
        self.qrm_thread.start()
  

    def update_softness(self, event):
        self.softness = self.softness_slider.get()
        self.morse_source.set_rise(rise_time=self.rise_time)

    @property
    def rise_time(self):
        return max(0, 1.0 - float(self.softness)/100.0) * 0.3
    
    def update_tone(self, event):
        self.tone = self.tone_slider.get()
        self.morse_source.set_frequency(self.frequency)

    @property
    def frequency(self):
        return int(500 + (1.0 - float(self.tone)/100) * 350) # 500-850 hz
    
    
    def load_challenges(self):
        # open challenges record
        self.challenge_file, _ = os.path.splitext(self.data_source_file.get())
        self.challenge_file += '.chg'
        self.challenges = {}
        if not self.use_challenge.get():
            return
        try:
            with open(os.path.join(self.data_source_dir, self.challenge_file), mode = "r") as challenge_db:
                reader = csv.reader(challenge_db)
                for row in reader:
                    if not row:
                        continue
                    key, val = row
                    self.challenges[key] = int(val)
        except FileNotFoundError:
            pass #legit condition
        except Exception as e:
            print(f"An error occurred: {e}")

    def save_challenges(self):
    # clean and save challenges
        if not self.use_challenge.get():
            return
        with open(os.path.join(self.data_source_dir, self.challenge_file), mode="w") as challenges_db:
            writer = csv.writer(challenges_db)
            for key, value in self.challenges.items():
                if value < 0:
                    continue
                writer.writerow([key, value])

    def remove_challenge(self, sent_text):
        if not self.use_challenge.get():
            return
        if sent_text in self.challenges:
            self.challenges[sent_text] = self.challenges[sent_text] - 1

    def add_challenge(self, sent_text):
        if self.use_challenge.get():
            self.challenges[sent_text] = self.challenges.get(sent_text, 0) + 1
    
    def create_session_results_screen(self):
        self.save_challenges()
        if self.current_session is None:
            messagebox.showerror("Error", "No current session available")
            return
        self.stop_qrm()
        self.player.stop()
        self.morse_source.reset()
        for widget in self.root.winfo_children():
            widget.destroy()
        self.session_db.add_session(self.current_session)
        self.create_details_frame()
        self.selected_session = self.current_session
        self.display_session()

        self.back_button = Button(self.root, text="Done", command=self.create_results_screen)
        self.back_button.pack(side=tk.BOTTOM, fill=tk.X)
        self.back_button.bind("<Return>", lambda event: self.create_results_screen())
        self.back_button.focus_set()

    def create_results_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.session_frame = ttk.Frame(self.root)
        self.session_frame.pack(fill=tk.BOTH, expand=True)

        self.tree = ttk.Treeview(self.session_frame, columns=('score', 'date'), show='headings')
        def create_handler(sort_by):
            def handler():
                if self.sort_by == sort_by:
                    self.sort_inverted = not self.sort_inverted
                else:
                    self.sort_by = sort_by
                    self.sort_inverted = False
                self.populate_tree(self.sort_by)
            return handler
        self.tree.heading('score', text='Score', command=create_handler('score'))
        self.tree.heading('date', text='Date', command=create_handler('date'))
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(self.session_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.tree.bind('<ButtonRelease-1>', self.on_click)
        self.tree.bind(gLeftButton, self.show_context_menu)
        self.populate_tree(self.sort_by)

        self.create_details_frame()

        self.bottom_button_frame = ttk.Frame(self.root)
        self.bottom_button_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.restart_button = Button(self.bottom_button_frame, text="Restart", command=self.create_start_screen)
        self.restart_button.bind("<Return>", lambda event: self.create_start_screen())
        self.restart_button.focus_set()
        self.restart_button.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.quit_button = Button(self.bottom_button_frame, text="Quit", command=self.quit_app)
        self.quit_button.pack(side=tk.RIGHT, fill=tk.X, expand=True)

        self.create_context_menu()

    def create_details_frame(self):
        s = ttk.Style()
        s.configure('Treeview.Heading', foreground="black", background="green3")
        self.detail_frame = ttk.Frame(self.root)
        self.detail_frame.pack(fill=tk.BOTH, expand=True)

        self.session_label = ttk.Label(self.detail_frame, text="")
        self.session_label.pack()

        self.pair_tree = ttk.Treeview(self.detail_frame, columns=('received', 'sent', 'speed', 'duration'), show='headings')
        self.pair_tree.heading('received', text='Received')
        self.pair_tree.heading('sent', text='Sent')
        self.pair_tree.heading('speed', text='Speed')
        self.pair_tree.heading('duration', text='Duration')
        w = max(20, int(self.ui_width*0.1))
        # self.pair_tree.column('speed', width=w)
        # self.pair_tree.column('duration', width=w)
        self.pair_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = ttk.Scrollbar(self.detail_frame, orient=tk.VERTICAL, command=self.pair_tree.yview)
        self.pair_tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)


    def create_context_menu(self):
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Delete", command=self.confirm_delete)

    def show_context_menu(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            self.context_menu.post(event.x_root, event.y_root)

    def confirm_delete(self):
        confirmed = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete selected session(s)?")
        if not confirmed:
            return
        selected_items = self.tree.selection()
        for item in selected_items:
            session_date = self.tree.item(item, 'values')[1]
            self.session_db.delete_session(session_date)
        self.populate_tree(self.sort_by)

    def populate_tree(self, sort_by):
        for item in self.tree.get_children():
            self.tree.delete(item)
        sessions = self.session_db.get_sorted_sessions(sort_by=sort_by, ascending=self.sort_inverted)
        for session in sessions:
            self.tree.insert('', tk.END, values=(session.score, session.date))

    def on_click(self, event):
        try:
            item = self.tree.focus()
            session_date = self.tree.item(item, 'values')[1]
            self.selected_session = self.session_db.get_session(session_date)
            self.display_session()
        except IndexError:
            pass # ignore heading click

    def display_session(self):
        self.pair_tree.tag_configure('incorrect', foreground="red")
        self.pair_tree.tag_configure('correct', foreground="green")
        if self.selected_session:
            self.session_label.config(text=f"Session score: {self.selected_session.score}    Session Date: {self.selected_session.date}")
            for item in self.pair_tree.get_children():
                self.pair_tree.delete(item)
            for received, sent, speed, duration in self.selected_session.items:
                correct, _ = self.compare_function(sent, received, self.shortcuts)
                if correct:
                    t = 'correct'
                else:
                    t = 'incorrect'
                self.pair_tree.insert('', tk.END, values=(received, sent, speed, float(duration)), tags=t)

    def play_volume_test(self):
        if not self.start_enabled:
            return
        self.start_enabled = False
        self.player.start()
        self.current_speed = (self.init_speed.get())
        self.morse_source.set_speed(float(self.current_speed))
        t_morse = self.morse_source.play_string("Vvv")
        t_qrn = self.qrm_source.play_string("QRN QRN")
        root.after(round(1000 * max(t_morse, t_qrn) + 0.5), self.on_sound_test_complete)

    def on_sound_test_complete(self):
        self.player.stop()
        self.morse_source.reset()
        self.qrm_source.reset()
        self.start_enabled = True

    def start_training(self):
        if not self.start_enabled:
            return
        self.current_speed = (self.init_speed.get())
        self.morse_source.set_speed(float(self.current_speed))
        self.save_settings()
        self.create_main_screen()

    def process_entry(self, event, delay=1):
        received_text = self.entry_field.get().upper().strip()
        self.entry_field.delete(0, tk.END)
        sent_text = self.ser_num.upper() + self.sent_word.upper().strip()
        equal, score = self.compare_function(sent_text, received_text, self.shortcuts)
        mult = self.score_multipliers[self.current_speed - self.speed_range[0]]
        score = int(round(score*mult)) if self.speed_increase else int(round(score*mult/3.0))
        
        self.current_session.add_item(received=received_text, sent=sent_text, speed=self.current_speed, duration=1.3)
        self.current_session.set_score(self.current_session.get_score() + score)
        self.received_cnt += 1
        
        if equal:
            c = 'green'
            if self.speed_increase: # first receive was correct
                self.current_speed = min(self.current_speed + 1, self.max_speed.get())
                self.remove_challenge(self.sent_word)
            self.speed_increase = True
        else:
            c = 'red'
            self.current_speed = max(self.current_speed - 1, self.init_speed.get())
            self.add_challenge(self.sent_word)
        self.received_text.config(text=received_text, fg=c)
        self.sent_text.config(text=sent_text)
        self.morse_source.set_speed(float(self.current_speed))
        self.update_data_frame()
        self.play_word(delay)
    
    def update_data_frame(self):
        self.speed_label.config(text=f"Speed: {self.current_speed} WPM")
        self.score_label.config(text=f"Score: {self.current_session.score}")
        self.count_label.config(text=f"Count: {self.received_cnt}")

    def play_word(self, delay, replay=False):
        if replay == False:
            self.pre_msg, self.rst, self.ser_num, self.sent_word = self.data_source.get_next_word()
            if self.sent_word:
                msg = self.pre_msg+self.rst+self.ser_num+self.sent_word
            else:
                self.stop_qrm()
                self.player.stop()
                self.morse_source.reset()
                self.create_session_results_screen()
                return
        else: 
            self.speed_increase = False
            msg = None
        threading.Timer(delay, self.morse_source.play_string, args=[msg]).start()

    def stop_qrm(self):
        if self.qrm_thread:
            self.run_qrm_thread = False
            self.qrm_thread.join()
            self.qrm_thread = []
    
    def quit_app(self):
        self.stop_qrm()
        self.player.stop()
        self.save_settings()
        self.root.quit()


def compare(sent_word, received_word, shortcuts):
    # Compare characters in lowercase
    correctness_mask = [((s == r) or ((s in shortcuts) and r == shortcuts[s])) for s, r in zip(sent_word, received_word)]
    score = sum(correctness_mask)

    # Extend the correctness mask if the received word is longer
    if len(received_word) != len(sent_word):
        correct = False
    else:
        # Determine if sent and received are identical enough
        correct = all(correctness_mask)

    return correct, score


# Create main application window
import sys
import glob
import shutil


# detect running mode and set path accordingly
if getattr(sys, 'frozen', False): # application package
    # Running in a bundle
    bin_path = sys._MEIPASS
    base_path = os.path.join(bin_path, 'conf')
else: # python
    base_path = os.path.abspath(".")
    bin_path = base_path

if platform.system() == 'Darwin':
    user_path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'MorseCodeX', 'configs')
    data_path = os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'MorseCodeX', 'data')
elif platform.system() == 'Windows':
    user_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'MorseCodeX', 'configs')
    data_path = os.path.join(os.path.expanduser('~'), 'AppData', 'Local', 'MorseCodeX', 'data')
elif platform.system() == 'Linux':
    user_path = os.path.join(os.path.expanduser('~'), '.MorseCodeX', 'configs')
    data_path = os.path.join(os.path.expanduser('~'), '.MorseCodeX', 'data')

guard_file = os.path.join(data_path, 'notdone.txt')
if not os.path.exists(data_path): #first time running
    os.makedirs(user_path, exist_ok=True)
    os.makedirs(data_path, exist_ok=True)
    open(guard_file, 'a').close()

#copy data files into user location
if os.path.exists(guard_file):
    conf = os.path.join(base_path, '*.txt')
    for file in glob.glob(conf):
        shutil.copy(file, data_path)
    conf = os.path.join(base_path, '*.SCP')
    for file in glob.glob(conf):
        shutil.copy(file, data_path)
    os.remove(guard_file)

root = tk.Tk()
root.iconbitmap(os.path.join(bin_path, 'MorseCodex.ico'))
app = MorseCodeXUI(root, compare, base_path = base_path, data_path = data_path, user_path = user_path)
root.mainloop()
