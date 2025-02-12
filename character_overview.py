import tkinter as tk
from tkinter import ttk
from DataManagers import cm_shared
from PIL import Image, ImageTk
from tktooltip import ToolTip
from OnDemandWindows import window_manager
from GUI_CharacterInfo import charaWindow

class CharacterOverview:
    def __init__(self):
        self.main_overview_window = None
        self.change_health_window = None

        self.base_frame = None

        self.current_party_dict = {}
        self.frame_to_chara_dict = {}

        self.party_member_frames = []

    def create_overview_panels(self, main_window=None):
        if self.main_overview_window is not None:
            if self.main_overview_window.winfo_exists():
                return

        if main_window is None:
            self.main_overview_window = tk.Tk()
        else:
            self.main_overview_window = tk.Toplevel(main_window)

        self.main_overview_window.title("Party Members")

        self.base_frame = ttk.LabelFrame(self.main_overview_window, text="Party", padding=(10, 0))
        self.base_frame.grid(row=0, column=0, padx=1, pady=0, sticky="nsew")

        self.create_party_elements()

        if main_window is None:
            self.main_overview_window.mainloop()

    def save_character_state(self):
        for chara_id, chara in self.current_party_dict.items():
            chara.save_changes_to_databank()
        self.create_party_elements()

    def set_health_from_entry(self, chara, entry_field):
        chara.Battle_HP = int(entry_field.get())
        self.create_party_elements()
        self.change_health_window.destroy()

    def change_chara_health(self, event, chara):
        if self.change_health_window is not None:
            if self.change_health_window.winfo_exists():
                return
        self.change_health_window = tk.Toplevel(self.main_overview_window)
        self.change_health_window.title(f"Change Health {chara.Base_Name}")

        window_manager.position_window(self.main_overview_window, self.change_health_window)

        input_frame = ttk.LabelFrame(self.change_health_window, text="Input", padding=(0, 0))
        input_frame.grid(row=0, column=0, padx=10, pady=0, sticky="nsew")

        entry_field = ttk.Entry(input_frame, width=5)
        entry_field.grid(row=0, column=0, padx=5, pady=0, sticky="e")

        label = ttk.Label(input_frame, text=f"/{chara.Battle_HP_Max}")
        label.grid(row=0, column=1, padx=5, pady=0, sticky="e")

        entry_field.insert(0, chara.Battle_HP)

        action_frame = ttk.LabelFrame(self.change_health_window, text="Action", padding=(0, 0))
        action_frame.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")

        set_button = ttk.Button(action_frame,width=20, text="Set",
                                command=lambda:self.set_health_from_entry(chara, entry_field))
        set_button.pack(fill="x")

    def create_party_elements(self):
        if self.main_overview_window is None:
            return
        if self.main_overview_window is not None:
            if not self.main_overview_window.winfo_exists():
                return

        for frame in self.party_member_frames:
            frame.destroy()

        self.party_member_frames.clear()
        self.frame_to_chara_dict = {}

        current_party_ids = cm_shared.get_all_ids_from_available_characters()
        self.current_party_dict = {}

        for chara_id in current_party_ids:
            self.current_party_dict[chara_id] = cm_shared.Character_From_ID_Dictionary[chara_id]

        magic_buttons = []
        stats_buttons = []

        i = 0

        for chara_id, chara in self.current_party_dict.items():
            mystyle = ttk.Style()
            mystyle.theme_use('alt')  # choose other theme
            mystyle.configure('MyStyle.TLabelframe', borderwidth=4, relief='groove', labelmargins=10)
            mystyle.configure('MyStyle.TLabelframe.Label', font=('Ariel', 13, 'bold'))

            c = i % 2
            d = i // 2

            chara_frame = ttk.LabelFrame(self.base_frame, text=f"{i + 1}", padding=(0, 0))
            chara_frame.grid(row=d, column=c, padx=10, pady=0, sticky="nsew")
            i += 1

            portrait_frame = ttk.LabelFrame(chara_frame, text="", padding=(0, 0), relief="flat")
            portrait_frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

            # LoadImage
            image_path = rf"images\{chara.Portrait_ID}.png"
            image = Image.open(image_path).resize((200, 200))
            tk_image = ImageTk.PhotoImage(image)

            portrait_label = ttk.Label(portrait_frame, image=tk_image, relief="flat")
            portrait_label.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")

            portrait_label.configure(image=tk_image, relief="sunken")
            portrait_label.image = tk_image

            values_frame = ttk.LabelFrame(chara_frame, text=f"{chara.Base_Name}", padding=(0, 0), style='MyStyle.TLabelframe')
            values_frame.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")

            main_label_names = ("Level", "HP", "Race", "Class", "Exp", "AC", "Init", "Speed")
            main_label_values = (chara.Base_Level, f"{chara.Battle_HP}/{chara.Battle_HP_Max}", chara.Base_Race,
                                 chara.Base_Class, chara.Base_Exp,
                                 chara.get_current_ac()[0], chara.Base_Initiative, chara.Base_Speed)

            for k in range(len(main_label_names)):
                a = k % 4
                b = k // 4

                label = ttk.Label(values_frame, text=main_label_names[k])
                label.grid(row=a, column=2*b, padx=5, pady=0, sticky="e")

                label = ttk.Label(values_frame, text=main_label_values[k], font=("Helvetica", 10, "bold"))
                label.grid(row=a, column=2*b+1, padx=5, pady=0, sticky="w")

                if main_label_names[k] == "AC":
                    ToolTip(label, msg=lambda chara=chara: chara.get_current_ac()[1], delay=.2)
                if main_label_names[k] == "HP":
                    label.bind("<Double-1>", lambda event, chara=chara: self.change_chara_health(None,chara=chara))

            actions_frame = ttk.LabelFrame(chara_frame, padding=(0, 0), text="Actions", relief="ridge")
            actions_frame.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")

            # Magic
            magic_button = ttk.Button(actions_frame, text="M", width=4,
                                      command=lambda chara=chara: window_manager.open_magic_window(chara,
                                                                                                   self.main_overview_window))
            magic_button.grid(row=0, column=0, padx=1, pady=0, sticky="nsew")
            ToolTip(magic_button, msg="Magic Menu", delay=.2)

            # Stats
            stats_button = ttk.Button(actions_frame, text="S", width=4,
                                      command=lambda chara=chara: window_manager.open_stats_window(chara,
                                                                                                   self.main_overview_window))
            stats_button.grid(row=0, column=1, padx=1, pady=0, sticky="nsew")
            ToolTip(stats_button, msg="Stats Menu", delay=.2)

            # Bonus
            bonus_button = ttk.Button(actions_frame, text="B", width=4,
                                      command=lambda chara=chara: window_manager.open_bonus_window(chara,
                                                                                                   self.main_overview_window))
            bonus_button.grid(row=0, column=2, padx=1, pady=0, sticky="nsew")
            ToolTip(bonus_button, msg="Level Up Bonus Menu", delay=.2)

            # Inventory
            inventory_button = ttk.Button(actions_frame, text="I", width=4,
                                      command=lambda chara=chara: window_manager.open_inventory_window(chara,
                                                                                                   self.main_overview_window))
            inventory_button.grid(row=0, column=3, padx=1, pady=0, sticky="nsew")
            ToolTip(inventory_button, msg="Equipment and Inventory Menu", delay=.2)

            # Edit
            edit_button = ttk.Button(actions_frame, text="E", width=4,
                                          command=lambda chara=chara: charaWindow.open_window(chara,
                                                                                              self.main_overview_window,
                                                                                              self.create_party_elements))
            edit_button.grid(row=0, column=4, padx=1, pady=0, sticky="nsew")
            ToolTip(edit_button, msg="Character Creation Menu", delay=.2)

        number_of_party_members = len(cm_shared.get_all_ids_from_available_characters())

        refresh_button = ttk.Button(self.base_frame, text="Refresh", width=7, command=self.create_party_elements)
        refresh_button.grid(row=2, column=0, padx=1, pady=0, sticky="nsew")

        save_state_button = ttk.Button(self.base_frame, text="Save\nState", width=7, command=self.save_character_state)
        save_state_button.grid(row=2, column=1, padx=1, pady=0, sticky="nsew")


party_menu = CharacterOverview()
#party_menu.create_overview_panels()
