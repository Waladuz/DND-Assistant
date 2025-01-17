import tkinter as tk
from tkinter import ttk
from OnDemandWindows import window_manager
from character_overview import party_menu
from battle_screen import battle_manager
from enemy_creation import enemy_creator
from music_player import music_controller
from app import website

class MainWindow:
    def __init__(self):
        self.root_window = None
        pass

    def open_main_window(self):
        self.root_window = tk.Tk()
        self.root_window.title("Main Menu")

        base_frame = ttk.LabelFrame(self.root_window, text="Main Menu", width=200, padding=(10, 10))
        base_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        dice_button = ttk.Button(base_frame, text="Dice Menu", width=20,
                                 command=lambda: window_manager.open_virtual_dice(self.root_window))
        dice_button.grid(row=0, column=0)

        party_button = ttk.Button(base_frame, text="Party Menu", width=20,
                                 command=lambda: party_menu.create_overview_panels(self.root_window))
        party_button.grid(row=0, column=1)

        dungeon_map_button = ttk.Button(base_frame, text="Battle Map", width=20,
                                  command=lambda: battle_manager.open_battle_map(self.root_window))
        dungeon_map_button.grid(row=1, column=0)

        enemy_creation_button = ttk.Button(base_frame, text="Enemy Creation", width=20,
                                  command=lambda: enemy_creator.open_enemy_creation_window(self.root_window))
        enemy_creation_button.grid(row=1, column=1)

        music_button = ttk.Button(base_frame, text="♫ Music", width=20,
                                           command=lambda: music_controller.open_music_window(self.root_window))
        music_button.grid(row=2, column=0)

        website_button = ttk.Button(base_frame, text="Website ", width=20,
                                  command=lambda: website.open_window(self.root_window))
        website_button.grid(row=2, column=1)

        item_creation_button = ttk.Button(base_frame, text="Item Creation", width=20,
                                  command=lambda: window_manager.open_item_creation_window(self.root_window))
        item_creation_button.grid(row=3, column=0)

        item_creation_button = ttk.Button(base_frame, text="Loot Window", width=20,
                                          command=lambda: window_manager.open_loot_window(self.root_window))
        item_creation_button.grid(row=3, column=1)

        self.root_window.mainloop()


if __name__ == '__main__':
    main_window = MainWindow()
    main_window.open_main_window()