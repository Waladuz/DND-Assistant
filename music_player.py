from pygame import mixer
import random
import os
import tkinter as tk
from tkinter import ttk


class MusicPlayer:
    def __init__(self):
        self.music_player_window = None

        self.current_song = "None"
        self.current_song_type = "None"

        self.town_songs = []
        self.adventure_songs = []
        self.dungeon_songs = []
        self.battle_songs = []
        self.victory_songs = []

        self.action_buttons = []
        self.song_text_label = None

        self.isPaused = False

        mixer.init()
        self.load_songs_from_directory()

    def scroll_text(self):
        current_text = self.song_text_label['text']
        self.song_text_label['text'] = current_text[1:] + current_text[0]

        # Repeat after a short delay
        self.song_text_label.after(500, self.scroll_text)  # Adjust the delay for speed control

    def play_random_song(self, song_type):
        sort_dict = {
            "town": self.town_songs,
            "adventure": self.adventure_songs,
            "dungeon": self.dungeon_songs,
            "battle": self.battle_songs,
            "victory": self.victory_songs
        }

        if song_type.lower() not in sort_dict.keys():
            return

        self.isPaused = False

        if song_type.lower() == "victory":
            loop = 1
        else:
            loop = -1

        song_list = sort_dict[song_type.lower()]
        random_song = random.choice(song_list)

        self.current_song = random_song
        self.current_song_type = song_type.lower()

        song_path = f"music/{random_song}"
        self.song_text_label.config(text=f" ♪♫♪ Now Playing: {random_song}")
        
        mixer.music.stop()
        mixer.music.load(song_path)
        mixer.music.play(loop)
        self.update_symbols()

    def song_command(self, command_index):
        if command_index == 0:
            if self.isPaused:
                mixer.music.unpause()
                self.isPaused = False
        elif command_index == 1:
            if not self.isPaused:
                mixer.music.pause()
                self.isPaused = True
        elif command_index == 2:
            if self.current_song_type != "None":
                self.play_random_song(self.current_song_type)

        self.update_symbols()

    def update_symbols(self):
        if self.isPaused:
            self.action_buttons[0].config(state=tk.ACTIVE)
            self.action_buttons[1].config(state=tk.DISABLED)
        else:
            self.action_buttons[0].config(state=tk.DISABLED)
            self.action_buttons[1].config(state=tk.ACTIVE)

    def open_music_window(self, main_root):
        if self.music_player_window is not None:
            if self.music_player_window.winfo_exists():
                return

        if main_root is None:
            self.music_player_window = tk.Tk()
        else:
            self.music_player_window = tk.Toplevel(main_root)

        self.music_player_window.title("Music Player ♫")

        base_frame = ttk.LabelFrame(self.music_player_window, text="Play Random Song", width=200, padding=(10, 10))
        base_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        song_type_labels = ["town", "adventure", "dungeon", "battle", "victory"]

        for i, label in enumerate(song_type_labels):
            song_button = ttk.Button(base_frame, text=label.capitalize(), width=15,
                                     command=lambda label=label: self.play_random_song(label))
            song_button.grid(row=0, column=i)

        self.song_text_label = tk.Label(base_frame, text=" Press on a category button to play a random song.",
                         font=('Helvetica', 16), width=40)
        self.song_text_label.grid(row=1, column=0, columnspan=len(song_type_labels))

        action_frame = ttk.LabelFrame(self.music_player_window, text="Actions", width=200, padding=(10, 10))
        action_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        action_labels = ["⏵", "⏸", "⏭"]

        self.action_buttons = []

        for i, label in enumerate(action_labels):
            song_button = ttk.Button(action_frame, text=label.capitalize(), width=5,
                                     command=lambda i=i: self.song_command(i))
            song_button.grid(row=0, column=i)

            self.action_buttons.append(song_button)

        self.update_symbols()
        self.scroll_text()

        self.music_player_window.mainloop()

    def load_songs_from_directory(self):
        self.town_songs = []
        self.adventure_songs = []
        self.dungeon_songs = []
        self.battle_songs = []
        self.victory_songs = []

        sort_dict = {
            "town": self.town_songs,
            "adventure": self.adventure_songs,
            "dungeon": self.dungeon_songs,
            "battle": self.battle_songs,
            "victory": self.victory_songs
        }

        for file_name in os.listdir(f"music"):
            if file_name.endswith(".mp3"):

                for word, array in sort_dict.items():
                    if word in file_name.lower():
                        array.append(file_name)
                        break


music_controller = MusicPlayer()