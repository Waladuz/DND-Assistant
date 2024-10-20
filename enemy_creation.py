import tkinter as tk
import os
import glob
from tkinter import ttk
import character
from DataManagers import cm_shared, em_shared
from PIL import Image, ImageTk
from OnDemandWindows import window_manager


class EnemyCreationWindow:
    def __init__(self):
        self.portrait_combobox = None
        self.creation_window = None
        self.new_attack_window = None

        self.current_enemy = None

        self.base_entries = []
        self.attribute_entries = []
        self.skill_entries = []
        self.battle_info_entries = []
        self.attack_creation_entries = []
        self.portrait_label = None
        self.enemy_selection_combobox = None
        self.attack_list = None

    def new_character(self):
        new_id = em_shared.create_new_enemy_with_id()
        em_shared.create_enemy_from_database()
        enemy = em_shared.id_to_enemy_dictionary[new_id]
        self.load_enemy_selected(None, enemy)

    def save_enemy_select(self):
        base_data = []
        attribute_data = []
        skill_data = []
        infos_data = []

        for i in range(len(self.base_entries)):
            base_data.append(self.base_entries[i].get())

        for i in range(len(self.attribute_entries)):
            attribute_data.append(self.attribute_entries[i].get())

        for i in range(len(self.skill_entries)):
            skill_data.append(self.skill_entries[i].get())

        for i in range(len(self.battle_info_entries)):
            infos_data.append(self.battle_info_entries[i].get("1.0", "end-1c"))

        self.current_enemy.Portrait_ID = self.portrait_combobox.get()

        self.current_enemy.update_values(base_data, attribute_data, skill_data, infos_data)
        self.current_enemy.save_enemy_to_db()

    def load_enemy_selected(self, event, force_enemy=None, call_from_battle=False):
        if force_enemy is None:
            combo_entry = self.enemy_selection_combobox.get()
            enemy_id = int(combo_entry.split()[0])

            if enemy_id not in em_shared.id_to_enemy_dictionary.keys():
                return

            enemy = em_shared.id_to_enemy_dictionary[enemy_id]
        else:
            enemy = force_enemy
            if not call_from_battle:
                self.enemy_selection_combobox.set(f"{force_enemy.ID} - New Enemy")

        self.current_enemy = enemy
        base = enemy.get_base_array()
        attributes = enemy.get_attributes_array()
        skills = enemy.get_skill_array()
        infos = enemy.get_battle_info_array()

        for i, entry in enumerate(self.base_entries):
            if i in [2, 3]:
                if base[i] is not None:
                    self.base_entries[i].set(base[i])
                if call_from_battle:
                    self.base_entries[i].config(state="disabled")
                continue

            self.base_entries[i].delete(0, tk.END)
            self.base_entries[i].insert(0, base[i])
            if call_from_battle:
                self.base_entries[i].config(state="readonly")

        for i, entry in enumerate(self.attribute_entries):
            self.attribute_entries[i].delete(0, tk.END)
            self.attribute_entries[i].insert(0, attributes[i])
            if call_from_battle:
                self.attribute_entries[i].config(state="readonly")

        for i, entry in enumerate(self.skill_entries):
            self.skill_entries[i].delete(0, tk.END)
            self.skill_entries[i].insert(0, skills[i])
            if call_from_battle:
                self.skill_entries[i].config(state="readonly")

        for i, entry in enumerate(self.battle_info_entries):
            self.battle_info_entries[i].delete("1.0", "end")
            self.battle_info_entries[i].insert("1.0", infos[i])
            if call_from_battle:
                self.battle_info_entries[i].config(state="disabled")

        self.current_enemy.get_all_attacks_of_enemy()
        if not call_from_battle:
            self.enemy_selection_combobox['values'] = em_shared.get_ids_and_names_as_string()
        self.load_enemy_attack_list()
        self.load_portrait(is_preview=False, call_from_battle=call_from_battle)

    def remove_selected_element(self):
        selected_item = self.attack_list.selection()
        if selected_item:
            attack = self.attack_list.item(selected_item)
            attack_id = attack["values"][0]
            self.current_enemy.remove_attack_by_id(attack_id)
            self.load_enemy_attack_list()

    def load_portrait(self, event=None, is_preview=True, call_from_battle=False):
        if is_preview:
            image_name = self.portrait_combobox.get()
        else:
            image_name = self.current_enemy.Portrait_ID
            self.portrait_combobox.set(image_name)
            if call_from_battle:
                self.portrait_combobox.config(state="disabled")

        if not os.path.exists(rf"enemy/{image_name}") or image_name == "":
            return

        image = Image.open(rf"enemy/{image_name}").resize((200, 200))
        tk_image = ImageTk.PhotoImage(image)

        self.portrait_label.configure(image=tk_image, relief="sunken")
        self.portrait_label.image = tk_image

    def get_list_of_portraits(self, event=None):
        images_folder_path = os.path.join(os.getcwd(), 'enemy')

        jpg_files = glob.glob(os.path.join(images_folder_path, '*.jpg'))
        png_files = glob.glob(os.path.join(images_folder_path, '*.png'))

        file_names_a = [os.path.basename(file) for file in jpg_files]
        file_names_b = [os.path.basename(file) for file in png_files]

        file_names = file_names_a + file_names_b

        file_names_without_end = []

        for name in file_names:
            file_names_without_end.append(name[:])

        self.portrait_combobox['values'] = file_names_without_end

        return file_names_without_end

    def info_on_selected_attack(self, event=None):
        selected_item = self.attack_list.selection()
        if selected_item:
            attack_item = self.attack_list.item(selected_item)
            attack_id = attack_item["values"][0]
            attack = self.current_enemy.get_attack_by_id(attack_id)

            if attack is None:
                return

            window_manager.open_enemy_attack_description(None, attack, self.creation_window)

    def add_new_attack(self, event=None, preload_attack=None):
        if self.new_attack_window is not None:
            if self.new_attack_window.winfo_exists():
                return

        self.new_attack_window = tk.Toplevel(self.creation_window)
        self.new_attack_window.title(f"Add New Attack")

        info_labels = ("ID", "Attack Name", "Attack Description")
        heights = [1, 1, 5]
        self.attack_creation_entries = []

        battle_into_frame = ttk.LabelFrame(self.new_attack_window, text="Data", padding=(10, 10))
        battle_into_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew", rowspan=1)

        for i, info_label in enumerate(info_labels):
            # Create a label for each attribute
            label = ttk.Label(battle_into_frame, text=info_label)
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            entry = tk.Text(battle_into_frame, width=50, height=heights[i])
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="e")
            self.attack_creation_entries.append(entry)

        save_attack_button = ttk.Button(battle_into_frame, text="Save", width=20,
                                        command=self.save_new_attack)
        save_attack_button.grid(row=3, column=0, padx=5, pady=5, sticky="nsew", columnspan=2)

        close_attack_button = ttk.Button(battle_into_frame, text="Close", width=20,
                                         command=self.new_attack_window.destroy)
        close_attack_button.grid(row=4, column=0, padx=5, pady=5, sticky="nsew", columnspan=2)

        if preload_attack is None:
            new_id = self.current_enemy.get_highest_id_of_attacks()
            self.attack_creation_entries[0].insert("1.0", new_id)

    def save_new_attack(self):
        values = [int(self.current_enemy.ID)]
        for entry in self.attack_creation_entries:
            values.append(entry.get("1.0", "end-1c"))

        self.current_enemy.Battle_Actions.append(character.EnemyAttack(values))
        self.new_attack_window.destroy()
        self.load_enemy_attack_list()

    def load_enemy_attack_list(self):
        if self.attack_list is None:
            return

        for item in self.attack_list.get_children():
            self.attack_list.delete(item)

        attack_list = self.current_enemy.Battle_Actions

        for attack in attack_list:
            entries = (attack.ID, attack.name, attack.description)
            self.attack_list.insert("", "end", values=entries)

    def open_enemy_creation_window(self, main_window, call_from_battle=False):
        if self.creation_window is not None:
            if self.creation_window.winfo_exists():
                return

        self.creation_window = tk.Toplevel(main_window)
        self.creation_window.title(f"Enemy Creation Window")

        base_names = ("ID", "Name", "Alignment", "Weight", "HP", "Speed", "AC", "EXP")

        alignments = [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ]

        sizes = ("Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan")

        base_frame = ttk.LabelFrame(self.creation_window, text="Base", padding=(10, 10))
        base_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        portrait_frame = ttk.LabelFrame(base_frame, text="Portrait", padding=(10, 10))
        portrait_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10, columnspan=2)

        self.portrait_label = ttk.Label(portrait_frame, image=None, relief="sunken")
        self.portrait_label.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")

        self.portrait_combobox = ttk.Combobox(portrait_frame, width=15, values=[0, 2, 3, 5], state="readonly")
        self.portrait_combobox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.portrait_combobox.bind("<FocusIn>", self.get_list_of_portraits)
        self.portrait_combobox.bind("<<ComboboxSelected>>", func=lambda event: self.load_portrait(is_preview=True))

        self.portrait_combobox.config(state="disabled")
        self.get_list_of_portraits()

        self.base_entries = []
        self.attribute_entries = []
        self.skill_entries = []
        self.battle_info_entries = []

        for i, base_text in enumerate(base_names):
            # Create a label for each attribute
            label = ttk.Label(base_frame, text=base_text)
            label.grid(row=i + 1, column=0, padx=5, pady=5, sticky="e")

            if base_text == "Alignment":
                alignment_combobox = ttk.Combobox(base_frame, width=20, values=alignments, state="readonly")
                alignment_combobox.grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")
                alignment_combobox.current(0)
                self.base_entries.append(alignment_combobox)
            elif base_text == "Weight":
                weight_combobox = ttk.Combobox(base_frame, width=20, values=sizes, state="readonly")
                weight_combobox.grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")
                weight_combobox.current(0)
                self.base_entries.append(weight_combobox)
            else:
                # Create an entry field for each attribute
                entry = ttk.Entry(base_frame, width=20)
                entry.grid(row=i + 1, column=1, padx=5, pady=5, sticky="w")
                # Store the entry widgets in a list for future access
                self.base_entries.append(entry)

        base_names = ("ID", "Name", "Alignment", "Weight", "HP", "Speed", "AC", "EXP")
        attributes_labels = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

        attributes_frame = ttk.LabelFrame(self.creation_window, text="Attributes", padding=(10, 10))
        attributes_frame.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        for i, attribute_text in enumerate(attributes_labels):
            a = i % 2
            b = i // 2

            # Create a label for each attribute
            label = ttk.Label(attributes_frame, text=attribute_text)
            label.grid(row=b, column=2 * a, padx=5, pady=5, sticky="e")

            entry = ttk.Entry(attributes_frame, width=5)
            entry.grid(row=b, column=2 * a + 1, padx=5, pady=5, sticky="e")
            self.attribute_entries.append(entry)

        info_labels = ("Ability", "Dam. Immunity", "Con. Immunity", "Senses", "Languages")
        heights = [5, 2, 2, 3, 1]

        battle_into_frame = ttk.LabelFrame(self.creation_window, text="Enemy List", padding=(10, 10))
        battle_into_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew", rowspan=1)

        for i, info_label in enumerate(info_labels):
            # Create a label for each attribute
            label = ttk.Label(battle_into_frame, text=info_label)
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            entry = tk.Text(battle_into_frame, width=35, height=heights[i])
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="e")
            self.battle_info_entries.append(entry)

        skills_labels = ["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
                         "History", "Insight", "Intimidation", "Investigation", "Medicine",
                         "Nature", "Perception", "Performance", "Persuasion", "Religion",
                         "Sleight of Hand", "Stealth", "Survival"]

        skills_frame = ttk.LabelFrame(attributes_frame, text="Enemy Skills", padding=(10, 10))
        skills_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew", columnspan=4)

        for i, skill in enumerate(skills_labels):
            a = i % 2
            b = i // 2

            # Create a label for each attribute
            label = ttk.Label(skills_frame, text=skill)
            label.grid(row=b, column=2 * a, padx=5, pady=0, sticky="e")

            entry = ttk.Entry(skills_frame, width=5)
            entry.grid(row=b, column=2 * a + 1, padx=5, pady=0, sticky="e")
            self.skill_entries.append(entry)

        file_frame = ttk.LabelFrame(self.creation_window, text="File", padding=(10, 10))
        file_frame.grid(row=0, column=4, padx=10, pady=10, sticky="nsew", columnspan=1)

        if not call_from_battle:
            selection_label = ttk.Label(file_frame, text="Select")
            selection_label.grid(row=0, column=0, sticky="e")

            self.enemy_selection_combobox = ttk.Combobox(file_frame, width=15,
                                                         values=em_shared.get_ids_and_names_as_string(), state="readonly")
            self.enemy_selection_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")
            self.enemy_selection_combobox.current(0)

            self.enemy_selection_combobox.bind("<<ComboboxSelected>>", func=self.load_enemy_selected)

            save_enemy_button = ttk.Button(file_frame, text="Save Data", width=20, command=self.save_enemy_select)
            save_enemy_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

            load_enemy_button = ttk.Button(file_frame, text="Load Data", width=20,
                                           command=lambda: self.load_enemy_selected(None))
            load_enemy_button.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

            new_enemy_button = ttk.Button(file_frame, text="Create New", width=20, command=self.new_character)
            new_enemy_button.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

            close_window_button = ttk.Button(file_frame, text="Close", width=20, command=self.creation_window.destroy)
            close_window_button.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")

        attack_list_frame = ttk.LabelFrame(battle_into_frame, text="Attack List", padding=(10, 10))
        attack_list_frame.grid(row=6, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)

        columns = ("ID", "Name", "Description")

        # Create the first list (Treeview) with 6 columns
        self.attack_list = ttk.Treeview(attack_list_frame, columns=columns, show="headings", height=4,
                                        style="Custom.Treeview")
        self.attack_list.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        self.attack_list.bind("<Double-1>", func=self.info_on_selected_attack)

        # Create a vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(attack_list_frame, orient="vertical", command=self.attack_list.yview)
        self.attack_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        if not call_from_battle:
            add_attack_button = ttk.Button(attack_list_frame, text="New Attack", width=20,
                                           command=self.add_new_attack)
            add_attack_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

            remove_attack_button = ttk.Button(attack_list_frame, text="Remove Attack", width=20,
                                              command=self.remove_selected_element)
            remove_attack_button.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        for col in columns:
            if col == "Description":
                width = 200
            else:
                width = 75
            self.attack_list.heading(col, text=col)
            self.attack_list.column(col, width=width, anchor="center")

        self.load_enemy_selected(None, force_enemy=self.current_enemy, call_from_battle=call_from_battle)


enemy_creator = EnemyCreationWindow()
