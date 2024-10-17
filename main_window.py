import tkinter as tk
import os
import glob
from tkinter import ttk
import character
import shared_data
import re
from DataManagers import cm_shared
from PIL import Image, ImageTk
from tktooltip import ToolTip
from OnDemandWindows import window_manager
from GUI_CharacterInfo import charaWindow
from character_overview import party_menu
from battle_screen import battle_manager
from enemy_creation import enemy_creator


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

        self.root_window.mainloop()


main_window = MainWindow()
main_window.open_main_window()
