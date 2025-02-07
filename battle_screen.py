import os
import copy
import glob
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import character_overview
import enemy_creation
from DataManagers import em_shared, Map, mm_shared, cm_shared
from PIL import Image, ImageTk
from tktooltip import ToolTip
from OnDemandWindows import window_manager
from character_overview import party_menu
from battle_manager import BattleManager
from character import Character, Enemy
from shared_data import get_attribute_modifier
from item import item_database


class BattleScreenManager:
    def __init__(self):
        self.main_window = None
        self.menu = None
        self.current_map = None
        self.map_image = None
        self.main_battle_window = None
        self.enemy_addition_window = None
        self.battle_screen_initiative_window = None
        self.combat_window = None
        self.add_loot_window = None
        self.split_loot_window = None

        self.copied_battle_window = None

        self.map_frame = None
        self.info_frame = None
        self.action_frame = None
        self.loot_split_frame = None

        self.item_loot_list = None
        self.enemy_list = None
        self.enemy_entry_fields = []

        self.main_canvas = None
        self.secondary_canvas = None

        self.map_image_combobox = None
        self.map_selection_combobox = None
        self.enemy_selection_combobox = None
        self.dice_roll_label = None
        self.entry_interval = None
        self.entry_map_name = None
        self.entry_map_id = None
        self.entry_map_money = None

        self.new_enemy = None
        self.list_of_enemies = []

        self.map_size = 800
        self.interval = 50

        self.placed_images = {}
        self.images_list = []
        self.line_array = []

        self.battle_manager = None

        self.battle_info_frame = None
        self.battle_action_frame = None
        self.info_portrait_label = None
        self.battle_status_label = None
        self.current_highlight = None
        self.entries_entity_info = []
        self.entries_battle_initiatives = []
        self.battle_portraits = []

        self.loot_list = []

    def start_battle(self):
        if len(self.list_of_enemies) == 0:
            return
        if self.interval <= len(self.list_of_enemies):
            return

        self.battle_manager = BattleManager()
        self.battle_manager.start_battle(self.list_of_enemies)

        i = 0
        for entity in (self.battle_manager.player_list + self.battle_manager.enemy_list):
            entity.Temp_Coordinate = [i, 0]
            i += 1

        self.set_all_entities()
        self.action_frame.destroy()

        self.battle_info_frame = ttk.LabelFrame(self.main_battle_window, text="Battle Info", padding=(10, 10))
        self.battle_info_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        selected_entity_frame = ttk.LabelFrame(self.battle_info_frame, text="Selected Chara", padding=(10, 10))
        selected_entity_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        image_path = rf"images\001.png"
        image = Image.open(image_path).resize((150, 150))
        tk_image = ImageTk.PhotoImage(image)

        self.info_portrait_label = ttk.Label(selected_entity_frame, image=tk_image, relief="sunken")
        self.info_portrait_label.grid(row=0, column=0, padx=5, pady=5, sticky="nswe", columnspan=4)

        labels = ("Name", "Team", "HP", "AC", "Speed", "Status")
        self.entries_entity_info = []

        for k in range(len(labels)):
            a = k % 3
            b = k // 3

            label = ttk.Label(selected_entity_frame, text=labels[k])
            label.grid(row=a + 1, column=2 * b, padx=5, pady=0, sticky="e")

            entry = ttk.Label(selected_entity_frame, text="-", font=("Helvetica", 10, "bold"))
            entry.grid(row=a + 1, column=2 * b + 1, padx=5, pady=0, sticky="w")

            self.entries_entity_info.append(entry)

        self.battle_action_frame = ttk.LabelFrame(self.battle_info_frame, text="Action Sequence", padding=(10, 10))
        self.battle_action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        set_initiative_button = ttk.Button(self.battle_action_frame, text="Roll/Set Initiative",
                                           command=self.open_initiative_roll_map)
        set_initiative_button.grid(row=0, column=0, sticky="ew", columnspan=3)

        battle_status_frame = ttk.LabelFrame(self.battle_info_frame, text="Battle State", padding=(10, 10))
        battle_status_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        battle_status_label = ttk.Label(battle_status_frame, text="Status:")
        battle_status_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.battle_status_label = ttk.Label(battle_status_frame, text="Status:")
        self.battle_status_label.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        end_battle_frame = ttk.LabelFrame(self.battle_info_frame, text="End Battle", padding=(10, 10))
        end_battle_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        button_split_loot = ttk.Button(end_battle_frame, text="Split Loot", command=self.open_loot_split_window)
        button_split_loot.pack(fill='both', expand=True)

        self.load_selected_entity_info()
        self.refresh_battle_status()

    def refresh_battle_status(self):
        if self.battle_manager is None or self.battle_status_label is None:
            return

        match self.battle_manager.current_battle_state:
            case 0:
                status_text = "None"
            case 1:
                status_text = "Place Entities"
            case 2:
                status_text = "Set Initiatives"
            case 3:
                status_text = "Battle Sequence"
            case 3:
                status_text = "Battle Complete"
            case _:
                status_text = "None"

        self.battle_status_label.config(text=status_text)

    def load_selected_entity_info(self):
        labels = ("Name", "Team", "HP", "AC", "Speed", "Status")
        entity = self.battle_manager.current_selected_entity

        if entity is None:
            return

        if type(entity) == Character:
            image_path = f"images/{entity.Portrait_ID}.png"
        else:
            image_path = f"enemy/{entity.Portrait_ID}"

        if type(entity) == Character:
            values = (entity.Base_Name, "Player", f"{entity.Battle_HP}/{entity.Battle_HP_Max}",
                      entity.get_current_ac()[0], entity.Base_Speed, "-")
        else:
            values = (entity.Temp_CharaName, "Enemy", f"{entity.Temp_HP}/{entity.Temp_HP_Max}",
                      entity.Enemy_AC_Base, entity.Enemy_Speed, "-")

        for i, value in enumerate(values):
            if value is None:
                continue
            self.entries_entity_info[i].config(text=value)

        image = Image.open(image_path).resize((200, 200))
        tk_image = ImageTk.PhotoImage(image)

        self.info_portrait_label.configure(image=tk_image, relief="sunken")
        self.info_portrait_label.image = tk_image

        self.set_highlight(entity)

    def set_highlight(self, entity):
        coord = entity.Temp_Coordinate

        grid_size = self.main_canvas.winfo_width() // self.interval

        grid_x = coord[0] * grid_size
        grid_y = coord[1] * grid_size

        # Remove the previous highlight if it exists
        if self.current_highlight:
            self.main_canvas.delete(self.current_highlight)

        self.current_highlight = self.main_canvas.create_rectangle(
            grid_x, grid_y,
            grid_x + grid_size, grid_y + grid_size,
            outline="yellow", width=3
        )

    def open_enemy_details(self, other_entity):
        enemy_creation.enemy_creator.current_enemy = other_entity
        enemy_creation.enemy_creator.open_enemy_creation_window(self.main_window, True)

    def open_combat_window(self, other_entity):
        if self.combat_window is not None:
            if self.combat_window.winfo_exists():
                return

        self.combat_window = tk.Toplevel(self.main_battle_window)
        self.combat_window.title("Combat Menu")

        window_manager.position_window(self.main_battle_window, self.combat_window)

        entity_attacking = ttk.LabelFrame(self.combat_window, text="Attacker", padding=(10, 10))
        entity_attacking.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        entity_defending = ttk.LabelFrame(self.combat_window, text="Defender", padding=(10, 10))
        entity_defending.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.battle_portraits = []

        self.load_entity_to_combat_window(entity_attacking, self.battle_manager.current_selected_entity)
        self.load_entity_to_combat_window(entity_defending, other_entity)

        damage_attacker_frame = ttk.LabelFrame(self.combat_window, text="Damage To Attacker", padding=(10, 10))
        damage_attacker_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        entry_damage_attacker = ttk.Entry(damage_attacker_frame)
        entry_damage_attacker.insert(0, f"{0}")
        entry_damage_attacker.pack()

        damage_defender_frame = ttk.LabelFrame(self.combat_window, text="Damage To Defender", padding=(10, 10))
        damage_defender_frame.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

        entry_damage_defender = ttk.Entry(damage_defender_frame)
        entry_damage_defender.insert(0, f"{0}")
        entry_damage_defender.pack()

        damage_confirm_frame = ttk.LabelFrame(self.combat_window, text="Confirm", padding=(10, 10))
        damage_confirm_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew", columnspan=2)

        confirm_button = ttk.Button(damage_confirm_frame,text="Confirm",
                                    command= lambda :self.deal_damage_to_entities([self.battle_manager.current_selected_entity, int(entry_damage_attacker.get())],
                                                                                  [other_entity, int(entry_damage_defender.get())]))
        confirm_button.pack(fill="x", expand=True)

    def deal_damage_to_entities(self, attacker_and_damage, defender_and_damage):
        def get_text(entity, amount):
            if type(entity) == Character:
                name = entity.Base_Name
            else:
                name = entity.Temp_CharaName

            if amount == 0:
                return ""
            else:
                return f"{name} recieved {amount} damage!\n"

        attacker_and_damage[0].deal_damage(attacker_and_damage[1])
        defender_and_damage[0].deal_damage(defender_and_damage[1])

        attacker_text = get_text(attacker_and_damage[0], attacker_and_damage[1])
        defender_text = get_text(defender_and_damage[0], defender_and_damage[1])

        messagebox.showinfo("DAMAGE", attacker_text+defender_text)
        self.combat_window.destroy()
        self.refresh_sequence_list()
        party_menu.create_party_elements()

    def load_entity_to_combat_window(self, frame, entity):
        selected_entity_frame = ttk.LabelFrame(frame, text="Selected Chara", padding=(10, 10))
        selected_entity_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        attack_names = []
        attack_descriptions = []

        if type(entity) == Character:
            image_path = f"images/{entity.Portrait_ID}.png"
            entity.recalculate_arrays()
            attributes = entity.Attributes_Array
            main_values = (entity.Base_Name, "Player", f"{entity.Battle_HP}/{entity.Battle_HP_Max}",
                      entity.get_current_ac()[0], entity.Base_Speed, "-")
            for weapon in entity.Equipment_Weapons:
                attack_names.append(weapon.Item_Name)
                attack_descriptions.append(f"Damage: {weapon.Weapon_Damage}"
                                           f"\nRange: {weapon.Weapon_Range_Min}/{weapon.Weapon_Range_Max}"
                                           f"\nDetails: {weapon.get_additional_info_as_text(entity)}")
            for spell in entity.Spells:
                attack_names.append(spell.Magic_Name)
                attack_descriptions.append(spell.Magic_Detail)

        else:
            image_path = f"enemy/{entity.Portrait_ID}"
            attributes = entity.get_attributes_array()
            main_values = (entity.Temp_CharaName, "Enemy", f"{entity.Temp_HP}/{entity.Temp_HP_Max}",
                      entity.Enemy_AC_Base, entity.Enemy_Speed, "-")

            for enemy_attack in entity.Battle_Actions:
                attack_names.append(enemy_attack.name)
                attack_descriptions.append(enemy_attack.description)

        image = Image.open(image_path).resize((200, 200))
        tk_image = ImageTk.PhotoImage(image)

        info_portrait_label = ttk.Label(selected_entity_frame, image=tk_image, relief="sunken")
        info_portrait_label.grid(row=0, column=0, padx=5, pady=5, sticky="nswe", columnspan=4)

        self.battle_portraits.append(tk_image)

        labels = ("Name", "Team", "HP", "AC", "Speed", "Status")

        for k in range(len(labels)):
            a = k % 3
            b = k // 3

            label = ttk.Label(selected_entity_frame, text=labels[k])
            label.grid(row=a + 1, column=2 * b, padx=5, pady=0, sticky="e")

            entry = ttk.Label(selected_entity_frame, text=f"{main_values[k]}", font=("Helvetica", 10, "bold"))
            entry.grid(row=a + 1, column=2 * b + 1, padx=5, pady=0, sticky="w")

        attributes_frame = ttk.LabelFrame(frame, text="Attributes", padding=(10, 10))
        attributes_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        labels = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

        for k in range(len(labels)):
            a = k % 3
            b = k // 3

            label = ttk.Label(attributes_frame, text=labels[k][:3].upper())
            label.grid(row=a, column=2 * b, padx=5, pady=0, sticky="e")

            entry = ttk.Label(attributes_frame, text=f"{attributes[k]:02} ({get_attribute_modifier(int(attributes[k])):+d})",
                              font=("Helvetica", 10, "bold"))
            entry.grid(row=a, column=2 * b + 1, padx=5, pady=0, sticky="w")

        attacks_frame = ttk.LabelFrame(frame, text="Attacks", padding=(10, 10))
        attacks_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        for i, attack in enumerate(attack_names):
            label = ttk.Label(attacks_frame, text=attack)
            label.grid(row=i, column=0, padx=5, pady=0, sticky="e")
            ToolTip(label, msg=attack_descriptions[i], delay=.3)

    def on_right_click(self, event):
        if self.battle_manager is None:
            return
        if self.battle_manager.current_battle_state != 3:
            return

        x = event.x
        y = event.y

        grid_x = x // (self.main_canvas.winfo_width() // self.interval)
        grid_y = y // (self.main_canvas.winfo_width() // self.interval)

        coord = [grid_x, grid_y]

        found_entity = None

        for entity in (self.battle_manager.player_list + self.battle_manager.enemy_list):
            if entity.Temp_Coordinate == coord:
                found_entity = entity

        self.menu = tk.Menu(self.main_canvas, tearoff=0, relief="ridge")
        if found_entity != self.battle_manager.current_selected_entity:
            self.menu.add_command(label="Engage in Combat", command=lambda: self.open_combat_window(found_entity))
        if type(found_entity) == Enemy:
            self.menu.add_command(label="See Enemy Details", command=lambda: self.open_enemy_details(found_entity))
        self.menu.post(event.x_root, event.y_root)

    def on_left_click(self, event):
        x = event.x
        y = event.y

        grid_x = x // (self.main_canvas.winfo_width() // self.interval)
        grid_y = y // (self.main_canvas.winfo_width() // self.interval)

        coord = [grid_x, grid_y]

        found_entity = None

        for entity in (self.battle_manager.player_list + self.battle_manager.enemy_list):
            if entity.Temp_Coordinate == coord:
                found_entity = entity

        if 4 > self.battle_manager.current_battle_state > 0:
            if found_entity is not None:
                self.battle_manager.current_selected_entity = found_entity
                self.load_selected_entity_info()
                return

            if self.battle_manager.current_selected_entity is None:
                return

            self.battle_manager.current_selected_entity.Temp_Coordinate = coord

            self.set_all_entities()
            self.set_highlight(self.battle_manager.current_selected_entity)

    def set_all_entities(self):
        self.placed_images = {}

        self.images_list = []

        for entity in (self.battle_manager.player_list + self.battle_manager.enemy_list):
            grid_size = self.main_canvas.winfo_width() // self.interval

            grid_x_pos = entity.Temp_Coordinate[0] * grid_size
            grid_y_pos = entity.Temp_Coordinate[1] * grid_size

            if type(entity) == Character:
                image_path = f"images/{entity.Portrait_ID}.png"
            else:
                image_path = f"enemy/{entity.Portrait_ID}"

            new_image = Image.open(fr"{image_path}").resize((grid_size, grid_size))  # Replace with your new image path
            new_photo_image = ImageTk.PhotoImage(new_image, master=self.main_window)

            image_id = self.main_canvas.create_image(grid_x_pos, grid_y_pos, image=new_photo_image, anchor="nw")
            self.placed_images[(grid_x_pos, grid_y_pos)] = image_id
            self.images_list.append(new_photo_image)

    def read_new_interval(self):
        entry_content = self.entry_interval.get()

        if entry_content.isdigit():
            self.interval = int(entry_content)
            self.create_grid(self.map_size, self.map_size)
        else:
            self.entry_interval.delete(0, tk.END)
            self.entry_interval.insert(0, self.interval)

    def create_grid(self, width, height):
        for line in self.line_array:
            self.main_canvas.delete(line)

        """Draw grid lines on the canvas."""
        for i in range(0, width, self.map_size // self.interval):
            line = self.main_canvas.create_line([(i, 0), (i, height)], tag='grid', fill='blue')
            self.line_array.append(line)
        for i in range(0, height, self.map_size // self.interval):
            line = self.main_canvas.create_line([(0, i), (width, i)], tag='grid', fill='blue')
            self.line_array.append(line)

    def get_list_of_maps(self):
        images_folder_path = os.path.join(os.getcwd(), 'maps')
        png_files = glob.glob(os.path.join(images_folder_path, '*.png'))
        jpg_files = glob.glob(os.path.join(images_folder_path, '*.jpg'))
        file_names = [os.path.basename(file) for file in png_files + jpg_files]

        return file_names

    def load_image_from_folder(self, event, main_window, force_value=None):
        if force_value is not None:
            file_name = force_value
        else:
            file_name = self.map_image_combobox.get()
        new_image = Image.open(fr"maps/{file_name}").resize(
            (self.map_size, self.map_size))  # Replace with your image path
        new_map_image = ImageTk.PhotoImage(new_image, master=main_window)

        self.main_canvas.itemconfigure(self.map_image, image=new_map_image)
        self.main_canvas.image = new_map_image

        self.read_new_interval()

    def get_list_of_enemies(self):
        return em_shared.get_ids_and_names_as_string()

    def open_enemy_add_window(self):
        if self.enemy_addition_window is not None:
            if self.enemy_addition_window.winfo_exists():
                return

        self.enemy_addition_window = tk.Toplevel(self.main_battle_window)
        self.enemy_addition_window.title("Add Enemy")

        window_manager.position_window(root=self.main_battle_window, sub=self.enemy_addition_window)

        main_frame = ttk.LabelFrame(self.enemy_addition_window, text="Enemy List", padding=(10, 10))
        main_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        label = ttk.Label(main_frame, text="Creature Type", width=20)
        label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.enemy_selection_combobox = ttk.Combobox(main_frame, width=15,
                                                     values=self.get_list_of_enemies(),
                                                     state="readonly")
        self.enemy_selection_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.enemy_selection_combobox.current(0)
        self.enemy_selection_combobox.bind("<<ComboboxSelected>>",
                                           func=lambda event: self.load_enemy_in_preview(event, main_frame))

        labels = ("ID", "Ind. Name", "Max HP")

        self.enemy_entry_fields = []

        for i, label in enumerate(labels):
            label = ttk.Label(main_frame, text=label, width=20)
            label.grid(row=i + 1, column=0, padx=5, pady=5, sticky="e")

            entry = ttk.Entry(main_frame, width=20)
            entry.grid(row=i + 1, column=1, padx=5, pady=5, sticky="e")
            self.enemy_entry_fields.append(entry)

        self.dice_roll_label = ttk.Label(main_frame, text="", width=20)
        self.dice_roll_label.grid(row=3, column=2, padx=5, pady=5, sticky="e")

        action_frame = ttk.LabelFrame(self.enemy_addition_window, text="Actions", padding=(10, 10))
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        save_button = ttk.Button(action_frame, text="Add", padding=(10, 10),
                                 command=self.add_current_enemy_to_list)
        save_button.grid(row=0, column=0, sticky="nsew")

        close_button = ttk.Button(action_frame, text="Close", padding=(10, 10),
                                  command=self.enemy_addition_window.destroy)
        close_button.grid(row=0, column=1, sticky="nsew")

        self.load_enemy_in_preview(None, main_frame)

    def add_current_enemy_to_list(self):
        if self.new_enemy is None:
            return

        self.list_of_enemies.append(self.new_enemy)
        self.refresh_enemy_list()
        self.enemy_addition_window.destroy()

    def refresh_enemy_list(self):
        if self.enemy_list.winfo_exists():
            for item in self.enemy_list.get_children():
                self.enemy_list.delete(item)

        index = 0

        for enemy in self.list_of_enemies:
            enemy.Temp_ID = index
            entries = (enemy.Temp_ID, enemy.Temp_CharaName, enemy.Enemy_Name, enemy.Temp_HP_Max)
            list_item = self.enemy_list.insert("", "end", values=entries)
            index += 1

    def remove_enemy_at_index(self):
        selected_item = self.enemy_list.selection()
        if selected_item:
            enemy = self.enemy_list.item(selected_item)
            enemy_id = enemy["values"][0]
            self.list_of_enemies = [enemy for enemy in self.list_of_enemies if enemy.Temp_ID != enemy_id]
            self.refresh_enemy_list()

    def save_map_to_db(self):
        map_entity = Map([self.entry_map_id.get(), self.map_image_combobox.get(),
                          self.entry_map_name.get(), self.interval, int(self.entry_map_money.get())])
        map_entity.set_enemy_list(self.list_of_enemies)
        map_entity.loot_list = self.loot_list
        map_entity.save_to_db()
        mm_shared.reload_all_maps_from_db()
        self.map_selection_combobox.set(f"{self.entry_map_id.get()} - {self.entry_map_name.get()}")
        self.map_selection_combobox['values'] = self.load_list_of_maps()

    def load_list_of_maps(self):
        map_dict = mm_shared.id_to_map_dict
        map_list = []

        for map_id, map_object in map_dict.items():
            map_list.append(f"{map_id} - {map_object.map_name}")

        return map_list

    def load_enemy_in_preview(self, event, main_frame):
        combo_entry = self.enemy_selection_combobox.get()
        enemy_id = int(combo_entry.split()[0])

        creature = em_shared.id_to_enemy_dictionary[enemy_id]
        self.new_enemy = copy.copy(creature)

        new_id = len(self.list_of_enemies) + 1
        creature_name = creature.Enemy_Name
        ind_name = f"{creature.Enemy_Name} {new_id}"

        self.new_enemy.set_new_battle_entity([new_id, ind_name, 5, 5])

        new_values = [new_id, ind_name, self.new_enemy.Temp_HP_Max]

        for i, entry in enumerate(self.enemy_entry_fields):
            entry.delete(0, tk.END)
            entry.insert(0, new_values[i])

        self.dice_roll_label.config(text=f"({self.new_enemy.Enemy_HP_Roll})")

    def load_selected_map(self, event=None, main_window=None):
        combo_entry = self.map_selection_combobox.get()
        map_id = int(combo_entry.split()[0])

        self.current_map = mm_shared.id_to_map_dict[map_id]

        print(len(self.list_of_enemies))

        self.load_image_from_folder(event=None, main_window=main_window,
                                    force_value=self.current_map.image_name)

        self.list_of_enemies = self.current_map.enemy_list
        self.refresh_enemy_list()
        self.loot_list = self.current_map.loot_list
        self.load_loot_list()

        self.interval = self.current_map.grid_interval
        self.entry_interval.delete(0, tk.END)
        self.entry_interval.insert(0, self.interval)
        self.read_new_interval()

        self.entry_map_money.delete(0, tk.END)
        self.entry_map_money.insert(0, self.current_map.money_loot)

        self.entry_map_name.delete(0, tk.END)
        self.entry_map_name.insert(0, self.current_map.map_name)

        self.entry_map_id.delete(0, tk.END)
        self.entry_map_id.insert(0, self.current_map.ID)

        self.map_selection_combobox['values'] = self.load_list_of_maps()

    def open_initiative_roll_map(self):
        if self.battle_screen_initiative_window is not None:
            if self.battle_screen_initiative_window.winfo_exists():
                return

        self.refresh_battle_status()
        self.battle_screen_initiative_window = tk.Toplevel(self.main_battle_window)
        self.battle_screen_initiative_window.title("Roll Initiative")

        window_manager.position_window(self.main_battle_window, self.battle_screen_initiative_window)

        self.entries_battle_initiatives = []

        base_frame = ttk.LabelFrame(self.battle_screen_initiative_window, text="Roll Values", padding=(10, 10))
        base_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        for i, entity in enumerate(self.battle_manager.player_list + self.battle_manager.enemy_list):
            if type(entity) == Character:
                entity_name = entity.Base_Name
            else:
                entity_name = entity.Temp_CharaName

            label = ttk.Label(base_frame, text=entity_name, width=30)
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            entry = ttk.Entry(base_frame, width=5)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="nsew")
            self.entries_battle_initiatives.append(entry)

        action_frame = ttk.LabelFrame(self.battle_screen_initiative_window, text="Action", padding=(10, 10))
        action_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        initiative_set_button = ttk.Button(action_frame, text="Set Initiatives and Determine Sequence",
                                           command=self.set_initiative)
        initiative_set_button.grid(row=0, column=0, sticky="snwe")

    def set_initiative(self):
        list_of_initiatives = []
        for entry in self.entries_battle_initiatives:
            list_of_initiatives.append(int(entry.get()))

        self.battle_manager.set_initiative(list_of_initiatives)
        self.battle_manager.current_battle_state = 3
        self.refresh_battle_status()
        self.refresh_sequence_list()
        self.battle_screen_initiative_window.destroy()

    def refresh_sequence_list(self):
        for widget in self.battle_action_frame.winfo_children():
            widget.destroy()

        initiative_dict = self.battle_manager.initiative_to_entity_dictionary

        label = ttk.Label(self.battle_action_frame, text="Initiative", font=("Helvetica", 10, "bold"))
        label.grid(row=0, column=0, padx=5, pady=0, sticky="e")

        entry = ttk.Label(self.battle_action_frame, text="Entity Name", font=("Helvetica", 10, "bold"))
        entry.grid(row=0, column=1, padx=5, pady=0, sticky="w")

        entry = ttk.Label(self.battle_action_frame, text="HP", font=("Helvetica", 10, "bold"))
        entry.grid(row=0, column=2, padx=5, pady=0, sticky="w")

        i = 1

        for initiative, entity in initiative_dict.items():
            if type(entity) == Character:
                entity_name = entity.Base_Name
            else:
                entity_name = entity.Temp_CharaName

            label = ttk.Label(self.battle_action_frame, text=initiative)
            label.grid(row=i, column=0, padx=5, pady=0, sticky="e")

            entry = ttk.Label(self.battle_action_frame, text=entity_name)
            entry.grid(row=i, column=1, padx=5, pady=0, sticky="w")

            entry = ttk.Label(self.battle_action_frame, text=entity.get_hp_as_text())
            entry.grid(row=i, column=2, padx=5, pady=0, sticky="w")
            i += 1

    def open_add_loot_window(self):
        def add_item_to_list():
            item_id = int(item_selection_combobox.get().split()[0])
            self.loot_list.append(item_id)
            self.load_loot_list()

        if self.add_loot_window is not None:
            if self.add_loot_window.winfo_exists():
                return

        self.refresh_battle_status()
        self.add_loot_window = tk.Toplevel(self.main_battle_window)
        self.add_loot_window.title("Add Loot")

        window_manager.position_window(self.main_battle_window, self.add_loot_window)

        item_dict = item_database.Item_Dictionary

        items_list_values = []

        for item_id, item in item_dict.items():
            items_list_values.append(f"{item_id} {item.Item_Name}")

        item_selection_combobox = ttk.Combobox(self.add_loot_window, values=items_list_values, state="readonly")
        item_selection_combobox.pack(padx=10, pady=10)

        add_button = ttk.Button(self.add_loot_window, text="Add", command=add_item_to_list)
        add_button.pack()

        remove_button = ttk.Button(self.add_loot_window, text="Close", command=self.add_loot_window.destroy)
        remove_button.pack()

    def remove_selected_loot_item(self):
        selected_item = self.item_loot_list.selection()
        if selected_item:
            item = self.item_loot_list.item(selected_item)
            item_id = item["values"][0]
            self.loot_list.remove(item_id)
            self.load_loot_list()

    def load_loot_list(self):
        if self.item_loot_list.winfo_exists():
            for item in self.item_loot_list.get_children():
                self.item_loot_list.delete(item)

        new_list = []

        for item_id in self.loot_list:
            print(item_id)
            new_list.append([item_id, item_database.get_item_from_id_in_table(item_id).Item_Name])

        for loot in new_list:
            entries = (loot[0], loot[1])
            list_item = self.item_loot_list.insert("", "end", values=entries)

    def open_loot_split_window(self):
        def recalculate_sum(event):
            print("here")

            remainder = total_money
            for entry in money_entry_fields:
                remainder -= int(entry.get())
            sum_label.config(text=f"Total remaining: {remainder}")

        if self.split_loot_window is not None:
            if self.split_loot_window.winfo_exists():
                return

        self.refresh_battle_status()
        self.split_loot_window = tk.Toplevel(self.main_battle_window)
        self.split_loot_window.title("Split Loot")

        window_manager.position_window(self.main_battle_window, self.split_loot_window)

        character_values = ["None"]
        chara_xp = [0]

        for chara_id, chara in cm_shared.Character_From_ID_Dictionary.items():
            character_values.append(f"{chara_id} {chara.Base_Name}")
            chara_xp.append(chara.Base_Exp)

        xp_statistic_frame = ttk.LabelFrame(self.split_loot_window, text="Experience Points", padding=(10, 10))
        xp_statistic_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        total_xp = sum(int(enemy.XP_On_Defeat) for enemy in self.current_map.enemy_list)
        split_xp = total_xp // (len(character_values) - 1)

        label_total_xp = ttk.Label(xp_statistic_frame, text=f"Total XP = {total_xp} ({split_xp} per player)",
                                   font=("Helvetica", 10, "bold"))
        label_total_xp.grid(row=0, column=0, columnspan=4)

        for i, chara in enumerate(character_values):
            if chara == "None":
                continue

            name = chara

            label_xp_name = ttk.Label(xp_statistic_frame, text=f"{name}", width= 15)
            label_xp_name.grid(row=i, column=0, columnspan=1)

            label_current_xp = ttk.Label(xp_statistic_frame, text=f"{chara_xp[i]}", width= 15)
            label_current_xp.grid(row=i, column=1, columnspan=1)

            label_arrow_xp = ttk.Label(xp_statistic_frame, text=f"→", width= 15)
            label_arrow_xp.grid(row=i, column=2, columnspan=1)

            label_current_xp = ttk.Label(xp_statistic_frame, text=f"{chara_xp[i] + split_xp}", width= 15)
            label_current_xp.grid(row=i, column=3, columnspan=1)

        self.loot_split_frame = ttk.LabelFrame(self.split_loot_window, text="Loot List", padding=(10, 10))
        self.loot_split_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        label_charabox_list = []

        for i, item_id in enumerate(self.loot_list):
            item = item_database.get_item_from_id_in_table(item_id)
            all_details = f"Type: {item.Item_Type}" \
                          f"\nWeight: {item.Item_Weight}" \
                          f"\nValue: {item.Item_Value}"

            label = ttk.Label(self.loot_split_frame, text=f"{item_id} {item.Item_Name}", width=30)
            ToolTip(label, all_details, delay=.2)
            label.grid(row=i, column=0, sticky="e")

            chara_combobox = ttk.Combobox(self.loot_split_frame, values=character_values, state="readonly")
            chara_combobox.grid(row=i, column=1)
            chara_combobox.current(0)

            label_charabox_list.append([label, chara_combobox])

        money_frame = ttk.LabelFrame(self.split_loot_window, text="Money", padding=(10, 10))
        money_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        total_money = self.current_map.money_loot

        sum_label = ttk.Label(money_frame, text=f"Total remaining: {total_money}", state="readonly")
        sum_label.grid(row=0, column=1)

        money_entry_fields = []
        money_label_entry_list = []

        for i, chara in enumerate(character_values, start=0):
            if chara == "None":
                continue

            chara_label = ttk.Label(money_frame, text=chara, state="readonly", width=15)
            chara_label.grid(row=i, column=0, sticky="w")

            entry_money_amount = ttk.Entry(money_frame)
            entry_money_amount.insert(0, 0)
            entry_money_amount.grid(row=i, column=1)

            money_entry_fields.append(entry_money_amount)

            entry_money_amount.bind("<Return>", lambda event: recalculate_sum(event))
            money_label_entry_list.append([entry_money_amount, chara_label])

        actions_frame = ttk.LabelFrame(self.split_loot_window, text="Actions", padding=(10, 10))
        actions_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        confirm_button = ttk.Button(actions_frame, text="Confirm",
                                    command=lambda: self.settle_loot_split(label_charabox_list, money_label_entry_list,
                                                                           split_xp))
        confirm_button.pack(fill="both", expand=True)

    def settle_loot_split(self, item_list, money_list, split_xp):
        for money in money_list:
            chara = cm_shared.Character_From_ID_Dictionary[int(money[1].cget("text").split()[0])]
            chara.Money += int(money[0].get())

        for item in item_list:
            if item[1].get() == "None":
                continue
            chara = cm_shared.Character_From_ID_Dictionary[int(item[1].get().split()[0])]
            chara.add_item(int(item[0].cget("text").split()[0]), 1)

        for chara_id, chara in cm_shared.Character_From_ID_Dictionary.items():
            chara.Base_Exp += int(split_xp)

        self.split_loot_window.destroy()
        character_overview.party_menu.create_party_elements()

    def delete_map(self):
        if self.current_map is None:
            return
        messagebox.askokcancel("Delete Map", "Are you sure you want to delete this map, you motherfucking"
                                             " piece of shit?")

        mm_shared.delete_map(self.current_map.ID)
        self.map_selection_combobox.current(0)
        self.load_selected_map(main_window=self.main_window)

    def open_battle_map(self, main_window):
        if self.main_battle_window is not None:
            if self.main_battle_window.winfo_exists():
                return

        if self.copied_battle_window is not None:
            if self.copied_battle_window.winfo_exists():
                return

        self.main_window = main_window

        self.main_battle_window = tk.Toplevel(main_window)
        self.main_battle_window.title("Battle Map")

        window_manager.position_window(main_window, self.main_battle_window)

        self.map_frame = ttk.LabelFrame(self.main_battle_window, text="Map", padding=(10, 10))
        self.map_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        background_image = Image.open(r"maps/map1.png").resize(
            (self.map_size, self.map_size))  # Replace with your image path
        photo_image = ImageTk.PhotoImage(background_image, master=main_window)

        self.main_canvas = tk.Canvas(self.map_frame, width=photo_image.width(), height=photo_image.height())
        self.main_canvas.pack()

        self.main_canvas.bind("<Button-1>", self.on_left_click)
        self.main_canvas.bind("<Button-3>", self.on_right_click)

        self.map_image = self.main_canvas.create_image(0, 0, image=photo_image, anchor="nw")

        self.action_frame = ttk.LabelFrame(self.main_battle_window, text="Map", padding=(10, 10))
        self.action_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        label = ttk.Label(self.action_frame, text="Map Image", padding=(10, 5))
        label.grid(row=0, column=0, sticky="e")

        self.map_image_combobox = ttk.Combobox(self.action_frame,
                                               values=self.get_list_of_maps(),
                                               state="readonly")
        self.map_image_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.map_image_combobox.current(0)
        self.map_image_combobox.bind("<<ComboboxSelected>>",
                                     func=lambda event: self.load_image_from_folder(event, main_window))

        label = ttk.Label(self.action_frame, text="Set Interval", padding=(10, 5))
        label.grid(row=1, column=0, sticky="e")

        self.entry_interval = ttk.Entry(self.action_frame)
        self.entry_interval.grid(row=1, column=1, sticky="w")

        button_change = ttk.Button(self.action_frame, text="Set", command=self.read_new_interval, width=5)
        button_change.grid(row=1, column=2, sticky="w")

        label = ttk.Label(self.action_frame, text="Map ID", padding=(10, 5))
        label.grid(row=2, column=0, sticky="e")

        self.entry_map_id = ttk.Entry(self.action_frame)
        self.entry_map_id.grid(row=2, column=1, sticky="w")

        label = ttk.Label(self.action_frame, text="Map Name", padding=(10, 5))
        label.grid(row=3, column=0, sticky="e")

        self.entry_map_name = ttk.Entry(self.action_frame)
        self.entry_map_name.grid(row=3, column=1, sticky="w")

        label = ttk.Label(self.action_frame, text="Completion Money", padding=(10, 5))
        label.grid(row=4, column=0, sticky="e")

        self.entry_map_money = ttk.Entry(self.action_frame)
        self.entry_map_money.grid(row=4, column=1, sticky="w")

        self.info_frame = ttk.LabelFrame(self.action_frame, text="Info", padding=(10, 5))
        self.info_frame.grid(row=7, column=0, padx=10, pady=10, sticky="nsew", columnspan=3)

        battle_frame = ttk.LabelFrame(self.action_frame, text="Enemy List", padding=(10, 5))
        battle_frame.grid(row=6, column=0, padx=10, pady=10, sticky="nsew", columnspan=3)

        columns = ("ID", "Name", "Creature", "HP")

        self.enemy_list = ttk.Treeview(battle_frame, columns=columns, show="headings", height=5,
                                       style="Custom.Treeview")
        self.enemy_list.grid(row=0, column=0, sticky="nswe")
        scrollbar = ttk.Scrollbar(battle_frame, orient="vertical", command=self.enemy_list.yview)
        self.enemy_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        for col in columns:
            if col == "Name" or col == "Creature":
                width = 120
            else:
                width = 50
            self.enemy_list.heading(col, text=col)
            self.enemy_list.column(col, width=width, anchor="center")

        button_add_enemy = ttk.Button(battle_frame, text="Add Enemy", padding=(5, 5), width=15,
                                      command=self.open_enemy_add_window)
        button_add_enemy.grid(row=1, column=0)

        button_remove_enemy = ttk.Button(battle_frame, text="Remove Enemy", padding=(5, 5), width=15,
                                         command=self.remove_enemy_at_index)
        button_remove_enemy.grid(row=2, column=0)

        columns = ("ID", "Item Name")

        self.item_loot_list = ttk.Treeview(battle_frame, columns=columns, show="headings", height=5,
                                       style="Custom.Treeview")
        self.item_loot_list.grid(row=3, column=0, sticky="nswe")

        scrollbar = ttk.Scrollbar(battle_frame, orient="vertical", command=self.item_loot_list.yview)
        self.item_loot_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=3, column=1, sticky="ns")

        for col in columns:
            if col == "Item Name":
                width = 120
            else:
                width = 50
            self.item_loot_list.heading(col, text=col)
            self.item_loot_list.column(col, width=width, anchor="center")

        button_add_item = ttk.Button(battle_frame, text="Add Item", padding=(5, 5), width=15,
                                      command=self.open_add_loot_window)
        button_add_item.grid(row=4, column=0)

        button_remove_item = ttk.Button(battle_frame, text="Remove Item", padding=(5, 5), width=15,
                                         command=self.remove_selected_loot_item)
        button_remove_item.grid(row=5, column=0)

        file_frame = ttk.LabelFrame(self.action_frame, text="Map", padding=(10, 10))
        file_frame.grid(row=5, column=0, padx=10, pady=10, sticky="nsew", columnspan=3)

        self.map_selection_combobox = ttk.Combobox(file_frame, width=15,
                                                   values=self.load_list_of_maps(),
                                                   state="readonly")
        self.map_selection_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="e")
        self.map_selection_combobox.current(0)
        self.map_selection_combobox.bind("<<ComboboxSelected>>",
                                         func=lambda event: self.load_selected_map(main_window=main_window))

        button_save = ttk.Button(file_frame, text="Save", command=self.save_map_to_db)
        button_save.grid(row=1, column=0)

        button_load = ttk.Button(file_frame, text="Load")
        button_load.grid(row=1, column=1)

        button_delete = ttk.Button(file_frame, text="Delete", command=self.delete_map)
        button_delete.grid(row=1, column=2)

        button_start_battle = ttk.Button(self.info_frame, text="Start Battle", command=self.start_battle)
        button_start_battle.pack(fill='both', expand=True)

        self.main_battle_window.columnconfigure(2, weight=1)  # Used to allow column 1 in some_frame to expand
        self.main_battle_window.columnconfigure(1, weight=1)  # Used to allow column 1 in some_frame to expand
        self.main_battle_window.rowconfigure(0, weight=1)  # Used to allow column 1 in some_frame to expand

        self.read_new_interval()

        main_window.mainloop()


battle_manager = BattleScreenManager()
