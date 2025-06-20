import tkinter as tk
from collections import Counter
import os
import glob
from tkinter import ttk
import character
import shared_data
from item import item_database, Item, Weapon, Armor
import re
from DataManagers import cm_shared
from typing import List
from PIL import Image, ImageTk
from tktooltip import ToolTip
import random


class OnDemandWindows:
    def __init__(self):
        self.item_list = None
        self.item_list2 = None
        self.item_list3 = None
        self.inventory_list = None
        self.armor_list = None
        self.weapons_list = None

        self.loot_multiplier_entry = None

        self.Listitem_Spell_Dict = {}
        self.Listitem_Spell_Submenu_Dict = {}

        self.Equipment_Item_Weapon_Dict = {}
        self.Equipment_Item_Armor_Dict = {}

        self.level_bonus_window = None

        self.item_creation_window = None
        self.stats_window = None
        self.magic_window = None
        self.inventory_window = None
        self.enemy_attack_info_window = None
        self.dice_window = None
        self.add_item_window = None
        self.loot_window = None

        self.magic_spell_list = None
        self.submenu_spell_list = None

        self.Main_Item_Weapon_Dict = {}
        self.Main_Item_Armor_Dict = {}
        self.Main_Item_BaseItem_Dict = {}

        self.select_weapons_list = None
        self.select_armors_list = None

        self.current_loot_list = []

        # Dice variables
        self.numbers_frame = None
        self.stop_button = None
        self.all_numbers = []
        self.running_numbers = []

        self.face_sum_label = None
        self.judgment_label = None
        self.dice_type_combobox = None
        self.dice_amount_combobox = None
        self.face_number = 6

    def position_window(self, root, sub):
        sub.transient(root)  # Make it a child of the root window
        sub.lift()  # Bring the second window to the top
        sub.focus_set()  # Give focus to the second window

        root_x = root.winfo_x()
        root_y = root.winfo_y()

        sub.geometry(f"+{root_x}+{root_y}")

    def update_treeview(self, event, search_var):
        for item in self.item_list2.get_children():
            self.item_list2.delete(item)

        item_list: List[Item] = item_database.get_list_of_item_with_part_string(search_var.get())

        for item in item_list:
            entries = (item.ID, item.Item_Name, item.Item_Type, item.Item_Weight, item.Item_Value)
            list_item = self.item_list2.insert("", "end", values=entries)
            self.Main_Item_BaseItem_Dict[list_item] = item

    def create_item_search_in_frame(self, frame: ttk.LabelFrame):
        for widget in frame.winfo_children():
            widget.destroy()

        description_label = ttk.Label(frame, text="Type Item Name")
        description_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        search_var = tk.StringVar()
        search_entry = ttk.Entry(frame, textvariable=search_var)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        search_entry.bind("<KeyRelease>", lambda event: self.update_treeview(event, search_var))

        result_frame = ttk.LabelFrame(frame, padding=(0, 0), text="Results", relief="ridge")
        result_frame.grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="e")

        columns = ("ID", "Name", "Type", "Weight", "Value")
        column_widths = [50, 150, 50, 55, 55]

        # Create the Treeview widget with 4 columns
        self.item_list = ttk.Treeview(result_frame, columns=columns, show="headings", height=15,
                                      style="Custom.Treeview")
        for i, col in enumerate(columns):
            self.item_list.heading(col, text=col)
            self.item_list.column(col, width=column_widths[i], anchor="center")

        # Create a vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.item_list.yview)
        self.item_list.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar into the LabelFrame
        self.item_list.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

    def open_loot_window(self, root):
        def validate_positive_integer(new_value):
            return new_value.isdigit()

        def give_selected_items_to_player(chara):
            selected_items = self.item_list3.selection()  # Get all selected items (their IDs)

            if len(selected_items) == 0:
                return

            deleted_values = []

            for item_entry in selected_items:
                item_id = self.item_list3.item(item_entry, "values")[0]
                deleted_values.append(item_id)
                chara.add_item(int(item_id), 1)

            for value in deleted_values:
                self.current_loot_list.remove(value)

            self.refresh_current_loot_window()

            # Reset the old selection if possible
            all_items = self.item_list3.get_children()

            matching_items = []
            for item_id in all_items:
                first_column_value = self.item_list3.item(item_id, "values")[0]  # Get the first column value
                if first_column_value in deleted_values:
                    matching_items.append(item_id)

            # Set the selection
            self.item_list3.selection_set(matching_items)

        def clear_selection_list():
            self.current_loot_list = []
            self.refresh_current_loot_window()

        if self.loot_window is not None:
            if self.loot_window.winfo_exists():
                return

        self.loot_window = tk.Toplevel(root)
        self.loot_window.title(f"Loot Window")

        item_selection_frame = ttk.LabelFrame(self.loot_window, padding=(0, 0), text="Add Item", relief="ridge")
        item_selection_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        item_view_frame = ttk.LabelFrame(self.loot_window, padding=(0, 0), text="Current Loot", relief="ridge")
        item_view_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        loot_split_frame = ttk.LabelFrame(self.loot_window, padding=(0, 0), text="Split Loot", relief="ridge")
        loot_split_frame.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")

        description_label = ttk.Label(item_selection_frame, text="Type Item Name")
        description_label.grid(row=0, column=0, padx=5, pady=5, sticky="w")

        search_var = tk.StringVar()
        search_entry = ttk.Entry(item_selection_frame, textvariable=search_var)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        amount_description_label = ttk.Label(item_selection_frame, text="Multiplier X")
        amount_description_label.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        validate_command = self.loot_window.register(validate_positive_integer)

        self.loot_multiplier_entry = ttk.Entry(item_selection_frame, width=5, validate="key",
                                               validatecommand=(validate_command, "%P"))
        self.loot_multiplier_entry.insert(0, "1")
        self.loot_multiplier_entry.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        search_entry.bind("<KeyRelease>", lambda event: self.update_treeview(event, search_var))

        result_frame = ttk.LabelFrame(item_selection_frame, padding=(0, 0), text="Results", relief="ridge")
        result_frame.grid(row=1, column=0, columnspan=4, padx=5, pady=5, sticky="e")

        columns = ("ID", "Name", "Type", "Weight", "Value")
        column_widths = [50, 150, 50, 55, 55]

        # Create the Treeview widget with 4 columns
        self.item_list2 = ttk.Treeview(result_frame, columns=columns, show="headings", height=7,
                                       style="Custom.Treeview")
        for i, col in enumerate(columns):
            self.item_list2.heading(col, text=col)
            self.item_list2.column(col, width=column_widths[i], anchor="center")

        # Create a vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=self.item_list2.yview)
        self.item_list2.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar into the LabelFrame
        self.item_list2.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        ###################################

        columns = ("ID", "Amount", "Name", "Type", "Weight", "Value")
        column_widths = [50, 50, 150, 50, 55, 55]

        self.item_list3 = ttk.Treeview(item_view_frame, columns=columns, show="headings", height=7,
                                       style="Custom.Treeview")
        for i, col in enumerate(columns):
            self.item_list3.heading(col, text=col)
            self.item_list3.column(col, width=column_widths[i], anchor="center")

        # Create a vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(item_view_frame, orient="vertical", command=self.item_list3.yview)
        self.item_list3.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar into the LabelFrame
        self.item_list3.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        self.item_list2.bind("<Double-1>", lambda event: self.add_item_to_loot_list(event))
        self.item_list3.bind("<Double-1>", lambda event: self.remove_item_to_loot_list(event))

        ###################################

        current_party_ids = cm_shared.get_all_ids_from_available_characters()
        current_party_dict = {}

        for chara_id in current_party_ids:
            current_party_dict[chara_id] = cm_shared.Character_From_ID_Dictionary[chara_id]

        y_pos = 0

        for chara_id, chara in current_party_dict.items():
            give_button = ttk.Button(loot_split_frame, text=chara.Base_Name, width=15,
                                     command=lambda chara=chara: give_selected_items_to_player(chara))
            give_button.grid(row=0, column=y_pos, padx=4, pady=0, sticky="nsew")
            y_pos += 1

        clear_loot_list_button = ttk.Button(loot_split_frame, text="Clear List", command=clear_selection_list)
        clear_loot_list_button.grid(row=1, column=0, columnspan=4, padx=4, pady=5, sticky="nsew")

    def add_item_to_loot_list(self, event):
        tree = event.widget
        selected_item = tree.focus()  # Returns the ID of the clicked item
        item_id = tree.item(selected_item, "values")[0]

        multiplier = int(self.loot_multiplier_entry.get())

        for i in range(multiplier):
            self.current_loot_list.append(item_id)

        self.refresh_current_loot_window()

    def remove_item_to_loot_list(self, event):
        tree = event.widget
        selected_item = tree.focus()  # Returns the ID of the clicked item
        item_id = tree.item(selected_item, "values")[0]

        if item_id in self.current_loot_list:
            self.current_loot_list.remove(item_id)
            self.refresh_current_loot_window()

    def refresh_current_loot_window(self):
        for item in self.item_list3.get_children():
            self.item_list3.delete(item)

        count_dict = Counter(self.current_loot_list)
        final_dict = {}

        for item_id, amount in count_dict.items():
            final_dict[item_database.Item_Dictionary[int(item_id)]] = amount

        for item, amount in final_dict.items():
            entries = (item.ID, amount, item.Item_Name, item.Item_Type, item.Item_Weight, item.Item_Value)
            list_item = self.item_list3.insert("", "end", values=entries)
            self.Main_Item_BaseItem_Dict[list_item] = item

    def open_item_creation_window(self, root):
        def save_fields(combobox):
            field_entries = []
            print(len(option_values))
            fields = entry_fields + option_values

            for field in fields:
                field_entries.append(field.get())

            item_database.add_new_item_to_db(field_entries)

        def update_fields(combobox):
            for widget in options_frame.winfo_children():
                widget.destroy()

            option_values.clear()

            if combobox.get() == "weapon":
                weapon_settings = [
                    ["Weapon Type", ["melee", "far"]],
                    ["Weapon Damage"],
                    ["Damage Type", ["bludgeoning", "slashing", "piercing"]],
                    ["Min. Range"],
                    ["Max. Range"],
                    ["Loading (x)"],
                    ["Throw (x)"],
                    ["Weight Class", ["heavy", "light"]],
                    ["Two-Hands (x)"],
                    ["Finesse (x)"],
                    ["Versatile Damage"],
                    ["Reach (x)"]
                ]

                for row_num, wep in enumerate(weapon_settings):
                    if len(wep) == 1:
                        entry = shared_data.ui_add_label_entry(options_frame, wep[0], row_num, 0, 30)
                    elif len(wep) == 2:
                        entry = shared_data.ui_add_label_combobox(options_frame, wep[0], wep[1], row_num, 0, 30)
                    else:
                        continue

                    option_values.append(entry)

            if combobox.get() == "armor":
                armor_settings = [
                    ["Armor Type", ["light", "medium", "heavy", "shield"]],
                    ["AC"],
                    ["Dex. Modifier (0,1,2)"],
                    ["Strength Requirement"],
                    ["Stealth. Modifier (x)"]
                ]

                for row_num, arm in enumerate(armor_settings):
                    if len(arm) == 1:
                        entry = shared_data.ui_add_label_entry(options_frame, arm[0], row_num, 0, 30)
                    elif len(arm) == 2:
                        entry = shared_data.ui_add_label_combobox(options_frame, arm[0], arm[1], row_num, 0, 30)
                    else:
                        continue

                    option_values.append(entry)

        if self.item_creation_window is not None:
            if self.item_creation_window.winfo_exists():
                return

        self.item_creation_window = tk.Toplevel(root)
        self.item_creation_window.title(f"Item Creation")

        option_values = []

        creation_frame = ttk.LabelFrame(self.item_creation_window, padding=(0, 0), text="Create Item", relief="ridge")
        creation_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        item_labels = ("Item Name", "Type", "Weight", "Value")
        item_types = ["weapon", "armor", "replenishable", "tool"]

        entry_fields = []
        combo_field = None

        for i, label_name in enumerate(item_labels):
            label = ttk.Label(creation_frame, text=label_name)
            label.grid(row=i, column=0, padx=0, pady=0, sticky="nsew")

            if label_name == "Type":
                combo_field = ttk.Combobox(creation_frame, values=item_types, width=18, state="readonly")
                combo_field.grid(row=i, column=1, padx=0, pady=0, sticky="nsew")
                combo_field.bind("<<ComboboxSelected>>", lambda event: update_fields(combo_field))
                entry_fields.append(combo_field)
            else:
                entry_field = ttk.Entry(creation_frame, width=19)
                entry_field.grid(row=i, column=1, padx=0, pady=0, sticky="nsew")
                entry_fields.append(entry_field)

        # LabelFrame for additional options
        actions_frame = ttk.LabelFrame(creation_frame, text="Actions")
        actions_frame.grid(row=len(item_labels), column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        save_button = ttk.Button(actions_frame, text="SAVE", command=lambda: save_fields(combobox=combo_field))
        save_button.pack()

        # LabelFrame for additional options
        options_frame = ttk.LabelFrame(creation_frame, text="More Options")
        options_frame.grid(row=len(item_labels) + 1, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

        base_frame = ttk.LabelFrame(self.item_creation_window, padding=(0, 0), text="Search Item List", relief="ridge")
        base_frame.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        self.create_item_search_in_frame(base_frame)

    def open_virtual_dice(self, root):
        if self.dice_window is not None:
            if self.dice_window.winfo_exists():
                return
        self.dice_window = tk.Toplevel(root)
        self.dice_window.title(f"Virtual Dice")

        setting_frame = ttk.LabelFrame(self.dice_window, padding=(0, 0), text="Setting", relief="ridge")
        setting_frame.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        dice_type = ("d4", "d6", "d8", "d10", "d12", "d20", "d100")
        dice_amount = (1, 2, 3, 4, 5, 6, 7, 8, 9, 10)

        label = ttk.Label(setting_frame, text="Dice Type")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        self.dice_type_combobox = ttk.Combobox(setting_frame, width=15,
                                               values=dice_type,
                                               state="readonly")
        self.dice_type_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        self.dice_type_combobox.current(1)

        label = ttk.Label(setting_frame, text="Dice Amount")
        label.grid(row=0, column=2, padx=5, pady=5, sticky="e")

        self.dice_amount_combobox = ttk.Combobox(setting_frame, width=15,
                                                 values=dice_amount,
                                                 state="readonly")
        self.dice_amount_combobox.grid(row=0, column=3, padx=5, pady=5, sticky="w")

        self.dice_amount_combobox.current(0)

        self.dice_type_combobox.bind("<<ComboboxSelected>>", func=self.create_dice)
        self.dice_amount_combobox.bind("<<ComboboxSelected>>", func=self.create_dice)

        self.numbers_frame = ttk.LabelFrame(self.dice_window, padding=(0, 0), text="Dices", relief="ridge")
        self.numbers_frame.grid(row=1, column=0, padx=0, pady=0, sticky="nsew")

        sum_frame = ttk.LabelFrame(self.dice_window, padding=(0, 0), text="Sum", relief="ridge")
        sum_frame.grid(row=2, column=0, padx=0, pady=0, sticky="nsew")

        self.face_sum_label = ttk.Label(sum_frame, text="0", font=("Helvetica", 30))
        self.face_sum_label.pack(fill="x")
        self.face_sum_label.configure(anchor="center")

        self.judgment_label = ttk.Label(sum_frame, text="", font=("Helvetica", 10))
        self.judgment_label.pack(fill="x")
        self.judgment_label.configure(anchor="center")

        actions_frame = ttk.LabelFrame(self.dice_window, padding=(0, 0), text="Actions", relief="ridge")
        actions_frame.grid(row=3, column=0, padx=0, pady=0, sticky="nsew")

        self.stop_button = ttk.Button(actions_frame, text="Stop!", command=self.stop_single_dice)
        self.stop_button.grid(row=0, column=0)

        redo_button = ttk.Button(actions_frame, text="Redo", command=lambda: self.create_dice(1))
        redo_button.grid(row=0, column=1)

        close_button = ttk.Button(actions_frame, text="Close", command=self.dice_window.destroy)
        close_button.grid(row=0, column=2)

        self.create_dice(None)

    def create_dice(self, event=None):
        self.face_number = int(self.dice_type_combobox.get()[1:])
        dice_amount = int(self.dice_amount_combobox.get())

        self.face_sum_label.config(text=f"{0}")
        self.judgment_label.config(text="")
        self.stop_button.config(state=tk.ACTIVE)

        self.running_numbers = []
        self.all_numbers = []

        for widget in self.numbers_frame.winfo_children():
            widget.destroy()

        for i in range(dice_amount):
            number_label = tk.Label(self.numbers_frame, text="0", font=("Helvetica", 30), width=3)
            number_label.grid(row=0, column=i)

            self.running_numbers.append(number_label)
            self.all_numbers.append(number_label)

        if event is not None:
            self.update_number()

    def stop_single_dice(self):
        if len(self.running_numbers) == 0:
            return

        self.running_numbers[0].config(fg="green")
        self.running_numbers.pop(0)
        sum = 0
        for i in self.all_numbers:
            if i not in self.running_numbers:
                sum += int(i.cget("text"))

        good = ["Yooooo!", "Ficker vom Dienst", "Gepriesen Sei Dein Cock", "Solide wie mein Schwanz",
                "Mehr Glück als Cock", "Anfängerglück"]
        bad = ["Opfa", "Lol", "Nichts drauf außer Zahnbelag", "Spast", ":(", "'Immer han i die pech'",
               "Würfel besser, du aff", "Wirklich?", "Würfelglück wie ein Sturmtruppler",
               "Kill yourself"]

        if len(self.running_numbers) == 0:
            self.stop_button.config(state=tk.DISABLED)
            word = ""
            print(int(.3 * int(self.face_number * len(self.all_numbers))))

            if sum >= int(.85 * int(self.face_number * len(self.all_numbers))):
                word = random.choice(good)
                # self.face_sum_label.config(fg="green")
            elif sum <= int(.3 * int(self.face_number * len(self.all_numbers))):
                word = random.choice(bad)
                # self.face_sum_label.config(fg="red")
            # else:
            # self.face_sum_label.config(fg="blue")

            self.judgment_label.config(text=word)

        self.face_sum_label.config(text=f"{sum}")

    def update_number(self):
        if len(self.running_numbers) > 0:
            for number in self.running_numbers:
                # Generate a random number between 1 and 20
                random_number = random.randint(1, self.face_number)
                # Update the label with the new number
                number.config(text=str(random_number))
                # Schedule the function to run again after 100 milliseconds (0.1 seconds)
            self.dice_window.after(10, self.update_number)

    def open_stats_window(self, chara, party_menu_root):
        if self.stats_window is not None:
            if self.stats_window.winfo_exists():
                return

        self.stats_window = tk.Toplevel(party_menu_root)
        self.stats_window.title(f"Stats ({chara.Base_Name})")

        self.position_window(party_menu_root, self.stats_window)

        attribute_frame = ttk.LabelFrame(self.stats_window, text="Attributes", width=200, padding=(10, 10))
        attribute_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        attributes_labels = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        chara.recalculate_arrays()
        chara_attributes = chara.Attributes_Array

        for i, attribute in enumerate(attributes_labels):
            label = ttk.Label(attribute_frame, text=attribute[:3].upper(), width=5)
            label.grid(row=0, column=i, padx=2, pady=0, sticky="ns")

            label = ttk.Label(attribute_frame, text=f"{chara_attributes[i]}", font=("Helvetica", 12, "bold"))
            label.grid(row=1, column=i, padx=0, pady=0, sticky="ns")

            label = ttk.Label(attribute_frame, text=f" {shared_data.get_attribute_modifier(chara_attributes[i]):+d}"
                              , font=("Helvetica", 10))
            label.grid(row=2, column=i, padx=0, pady=0, sticky="ns")

        skills_frame = ttk.LabelFrame(self.stats_window, text="Skills", width=200, padding=(10, 10))
        skills_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        skills_labels = ["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
                         "History", "Insight", "Intimidation", "Investigation", "Medicine",
                         "Nature", "Perception", "Performance", "Persuasion", "Religion",
                         "Sleight of Hand", "Stealth", "Survival"]
        chara_skills = chara.Skills_Array

        for i, skill in enumerate(skills_labels):
            a = i % 2
            b = i // 2

            label = ttk.Label(skills_frame, text=skill, width=15)
            label.grid(row=2 * b, column=2 * a + 1, padx=0, pady=0, sticky="e")

            label = ttk.Label(skills_frame, text=f"{chara_skills[i]}", font=("Helvetica", 12, "bold"))
            label.grid(row=2 * b, column=2 * a, padx=0, pady=0, sticky="e")

        self.stats_window.mainloop()

    def open_magic_window(self, chara, party_menu_root):
        if self.magic_window is not None:
            if self.magic_window.winfo_exists():
                return

        self.magic_window = tk.Toplevel(party_menu_root)
        self.magic_window.title(f"Magic Window ({chara.Base_Name})")

        self.position_window(party_menu_root, self.magic_window)

        base_frame = ttk.LabelFrame(self.magic_window, text="Magic Points", width=200, padding=(10, 10))
        base_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        for i in range(9):
            label = ttk.Label(base_frame, text=f"Lvl. {i + 1}", font=("Helvetica", 12, "bold"))
            label.grid(row=0, column=2 * i, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Fix this for non-mp classes
        if chara.Base_Class in shared_data.MP_BY_CLASS:
            mp_by_level = list(chara.Max_Magic_Points.values())
            mp_true = list(chara.Magic_Points.values())

            print(mp_true)
        else:
            mp_by_level = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            mp_true = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for i in range(9):
            # Create an entry field for each skill
            entry = ttk.Entry(base_frame, width=2)
            entry.delete(0, tk.END)
            entry.insert(0, f"{mp_true[i]}")
            entry.grid(row=1, column=2 * i, padx=5, pady=5, sticky="w")

            label = ttk.Label(base_frame, text=f"{mp_by_level[i]}")
            label.grid(row=1, column=2 * i + 1, padx=5, pady=5, sticky="nsew")

        spells_frame = ttk.LabelFrame(self.magic_window, text="Spells", width=200, padding=(10, 10))
        spells_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # Create the Treeview widget with 4 columns

        columns = ("Name", "Lvl", "School", "Duration", "Range", "AOE", "Save", "Damage/Effect")
        column_widths = (120, 30, 100, 100, 50, 80, 80, 120)
        i = 0

        self.magic_spell_list = ttk.Treeview(spells_frame, columns=columns, show="headings", height=6,
                                             style="Custom.Treeview")
        for col in columns:
            self.magic_spell_list.heading(col, text=col)
            self.magic_spell_list.column(col, width=column_widths[i], anchor="center")
            i += 1

        # Create a vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(spells_frame, orient="vertical", command=self.magic_spell_list.yview)
        self.magic_spell_list.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar into the LabelFrame
        self.magic_spell_list.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        scrollbar.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

        detail_frame = ttk.LabelFrame(self.magic_window, text="Description", padding=(10, 10))
        detail_frame.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        detail_text_box = tk.Text(detail_frame, height=5, wrap="word")
        detail_text_box.pack(side="left", expand=True, fill="both")

        # Create a Scrollbar and associate it with the Text widget
        scrollbar = ttk.Scrollbar(detail_frame, orient="vertical", command=detail_text_box.yview)
        scrollbar.pack(side="right", fill="y")

        # Configure the Text widget to work with the scrollbar
        detail_text_box.config(yscrollcommand=scrollbar.set)

        self.magic_spell_list.bind("<<TreeviewSelect>>",
                                   lambda event: self.set_magic_detail_info(event, chara, detail_text_box))

        action_frame = ttk.LabelFrame(self.magic_window, text="Actions", padding=(10, 10))
        action_frame.grid(row=4, column=0, padx=10, pady=10, sticky="nsew")

        add_magic_button = ttk.Button(action_frame, text="Add Spell",
                                      command=lambda: self.open_add_spell_window(chara))
        add_magic_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        add_magic_button = ttk.Button(action_frame, text="Remove Spell",
                                      command=lambda: self.remove_spell_to_chara(chara))
        add_magic_button.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        self.load_magic_spells_for_chara(chara)

        self.magic_window.mainloop()

    def update_magic_treeview(self, event, search_var):
        for item in self.submenu_spell_list.get_children():
            self.submenu_spell_list.delete(item)

        spell_dictionary = shared_data.magic_table.id_magic_dictionary
        self.Listitem_Spell_Submenu_Dict = {}
        final_spell_list: List[shared_data.Spell] = []

        all_spell_list: List[shared_data.Spell] = list(spell_dictionary.values())
        if search_var.get() != "":
            final_spell_list = [spell for spell in all_spell_list
                                if search_var.get().lower() in spell.Magic_Name.lower()]
        else:
            final_spell_list = all_spell_list

        for spell in final_spell_list:
            list_item = self.submenu_spell_list.insert("", "end",
                                                       values=(spell.Magic_ID, spell.Magic_Name, spell.Magic_Level))
            self.Listitem_Spell_Submenu_Dict[list_item] = spell

    def open_add_spell_window(self, chara):
        spell_browse_window = tk.Toplevel(self.magic_window)
        spell_browse_window.title(f"Add A Spell ({chara.Base_Name})")

        self.position_window(self.magic_window, spell_browse_window)

        frame = ttk.LabelFrame(spell_browse_window, text="Search for Spell", width=200, padding=(10, 10))
        frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        description_label = ttk.Label(frame, text="Type Spell Name")
        description_label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        search_var = tk.StringVar()
        search_entry = ttk.Entry(frame, textvariable=search_var)
        search_entry.grid(row=0, column=1, padx=5, pady=5, sticky="e")

        base_frame = ttk.LabelFrame(spell_browse_window, text="Spell List", width=200, padding=(10, 10))
        base_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        sub_menu_columns = ("ID", "Name", "Lvl")
        sub_menu_column_widths = (50, 150, 50)
        i = 0

        self.submenu_spell_list = ttk.Treeview(base_frame, columns=sub_menu_columns, show="headings", height=6,
                                               style="Custom.Treeview")
        for col in sub_menu_columns:
            self.submenu_spell_list.heading(col, text=col)
            self.submenu_spell_list.column(col, width=sub_menu_column_widths[i], anchor="center")
            i += 1

        # Create a vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(base_frame, orient="vertical", command=self.submenu_spell_list.yview)
        self.submenu_spell_list.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar into the LabelFrame
        self.submenu_spell_list.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        scrollbar.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        action_frame = ttk.LabelFrame(spell_browse_window, text="", width=200, padding=(10, 10))
        action_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        add_magic_button = ttk.Button(action_frame, text="Add", command=lambda: self.add_spell_to_chara(chara))
        add_magic_button.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        search_entry.bind("<KeyRelease>", lambda event: self.update_magic_treeview(event, search_var))
        self.update_magic_treeview(None, search_var)

    def remove_spell_to_chara(self, chara):
        selected_items = self.magic_spell_list.selection()

        if len(selected_items) == 0 or len(self.Listitem_Spell_Dict) == 0:
            return

        for item in selected_items:
            spell = self.Listitem_Spell_Dict[item]
            if spell in chara.Spells:
                chara.Spells.remove(spell)

        self.load_magic_spells_for_chara(chara)

    def add_spell_to_chara(self, chara):
        selected_items = self.submenu_spell_list.selection()

        if len(selected_items) == 0 or len(self.Listitem_Spell_Submenu_Dict) == 0:
            return

        for item in selected_items:
            spell = self.Listitem_Spell_Submenu_Dict[item]
            print(spell.Magic_Name)
            if spell not in chara.Spells:
                chara.Spells.append(spell)

        self.load_magic_spells_for_chara(chara)

    def set_magic_detail_info(self, event, chara, textbox):
        selected_items = self.magic_spell_list.selection()
        if len(selected_items) == 0:
            return

        spell_listitem = selected_items[0]

        spell = self.Listitem_Spell_Dict[spell_listitem]

        textbox.delete("1.0", tk.END)
        textbox.insert(tk.END, spell.Magic_Detail)

        textbox.tag_config("bold", font=("Helvetica", 12, "bold"))

        textbox.tag_remove("bold", "1.0", tk.END)

        content = textbox.get("1.0", tk.END)

        pattern = r'\b(\d+)?d\d+\b'

        for match in re.finditer(pattern, content):
            start_index = match.start()
            end_index = match.end()

            # Convert the start and end indexes to Tkinter text indices
            start = f"1.0 + {start_index} chars"
            end = f"1.0 + {end_index} chars"

            # Add the tag "bold" to the matching text
            textbox.tag_add("bold", start, end)

        for match in re.finditer("At Higher Levels", content):
            start_index = match.start()
            end_index = match.end()

            # Convert the start and end indexes to Tkinter text indices
            start = f"1.0 + {start_index} chars"
            end = f"1.0 + {end_index} chars"

            # Add the tag "bold" to the matching text
            textbox.tag_add("bold", start, end)

    def load_magic_spells_for_chara(self, chara):
        if self.magic_window is None:
            return

        spells = chara.Spells

        print(len(spells))

        for item in self.magic_spell_list.get_children():
            self.magic_spell_list.delete(item)

        for spell in spells:
            list_item = self.magic_spell_list.insert("", "end",
                                                     values=(spell.Magic_Name, spell.Magic_Level,
                                                             spell.Magic_School, spell.Magic_Duration,
                                                             spell.Magic_Range, spell.Magic_Area,
                                                             spell.get_saving_throw_type(), spell.Magic_Damage_Type))
            self.Listitem_Spell_Dict[list_item] = spell

    def open_bonus_window(self, chara, party_menu_root):
        if self.level_bonus_window is not None:
            if self.level_bonus_window.winfo_exists():
                return

        def save_character_notes(chara, text_field):
            chara.Level_Up_Notes = text_field.get("1.0", tk.END)

        self.level_bonus_window = tk.Toplevel(party_menu_root)
        self.level_bonus_window.title(f"Bonus Window ({chara.Base_Name})")

        self.position_window(party_menu_root, self.level_bonus_window)

        base_frame = ttk.LabelFrame(self.level_bonus_window, text="Bonuses", width=200, padding=(10, 10))
        base_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        if character is None:
            return

        bonuses = chara.get_current_level_bonuses_dictionary()

        label = ttk.Label(base_frame, text=f"Level", font=("Helvetica", 12, "bold"))
        label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        label = ttk.Label(base_frame, text=f"Skills", font=("Helvetica", 12, "bold"))
        label.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        i = 1

        for level, skill in bonuses.items():
            label = ttk.Label(base_frame, text=f"Level {level}")
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            print(skill)

            label = ttk.Label(base_frame, text=f"{skill["name"]}")
            label.grid(row=i, column=1, padx=5, pady=5, sticky="w")

            ToolTip(label, msg=lambda skill=skill: skill["description"], delay=.2)

            i += 1

        notes_frame = ttk.LabelFrame(self.level_bonus_window, text="Notes", width=200, padding=(10, 10))
        notes_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.bonus_notes_entry = tk.Text(notes_frame, height=5)
        self.bonus_notes_entry.pack(side="top", expand=True, fill="both")

        self.bonus_notes_entry.insert(tk.END, chara.Level_Up_Notes)

        save_button = ttk.Button(notes_frame, text="Save",
                                 command=lambda: save_character_notes(text_field=self.bonus_notes_entry,
                                                                      chara=chara))
        save_button.pack(pady=2, side="bottom")

        self.level_bonus_window.mainloop()

    def refresh_inventory_lists(self, chara):
        if self.inventory_window is None:
            return

        for item in self.weapons_list.get_children():
            self.weapons_list.delete(item)

        for item in self.armor_list.get_children():
            self.armor_list.delete(item)

        for item in self.inventory_list.get_children():
            self.inventory_list.delete(item)

        weapons = chara.Equipment_Weapons
        armors = chara.Equipment_Armors

        inventory = chara.get_inventory_items_as_dictionary()

        itemized_list = []
        self.Main_Item_Weapon_Dict = {}
        self.Main_Item_Armor_Dict = {}
        self.Main_Item_BaseItem_Dict = {}

        for weapon in weapons:
            list_item = self.weapons_list.insert("", "end", values=(weapon.Item_Name, weapon.Weapon_Type,
                                                                    f"{weapon.Weapon_Damage} ("
                                                                    f"{shared_data.get_attribute_modifier(chara.Attribute_Strength):+d})",
                                                                    weapon.Weapon_DamageType,
                                                                    f"{weapon.Weapon_Range_Min}/{weapon.Weapon_Range_Max}",
                                                                    weapon.get_additional_info_as_text(
                                                                        chara)))
            self.Main_Item_Weapon_Dict[list_item] = weapon

        for armor in armors:
            total, modified = armor.get_modified_armor_class(chara)
            armour_class_text = f"{total}"
            if modified != 0:
                armour_class_text += f" ({modified:+d})"
            list_item = self.armor_list.insert("", "end", values=(armor.Item_Name, armor.Armor_Type,
                                                                  armour_class_text,
                                                                  armor.get_additional_info_as_text()))
            self.Main_Item_Armor_Dict[list_item] = armor

        for item, amount in inventory.items():
            entries = (item.Item_Name, item.Item_Type, item.Item_Weight, item.Item_Value, amount)
            list_item = self.inventory_list.insert("", "end", values=entries)
            self.Main_Item_BaseItem_Dict[list_item] = item

    def open_inventory_window(self, chara, party_menu_root):
        if self.inventory_window is not None:
            if self.inventory_window.winfo_exists():
                return

        self.inventory_window = tk.Toplevel(party_menu_root)
        self.inventory_window.title(f"Inventory [{chara.Base_Name}]")

        self.position_window(party_menu_root, self.inventory_window)

        equip_frame = ttk.LabelFrame(self.inventory_window, text="Equipment", width=200, padding=(10, 10))
        equip_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        columns = ("Name", "Type", "Damage", "Damage Type", "Range", "Properties")
        armour_columns = ("Name", "Type", "AC", "Properties")

        ttk.Label(equip_frame, text="Weapon", anchor='w').pack(fill='both')
        # Create the first list (Treeview) with 6 columns
        self.weapons_list = ttk.Treeview(equip_frame, columns=columns, show="headings", height=3,
                                         style="Custom.Treeview")
        for col in columns:
            if col == "Properties":
                width = 150
            else:
                width = 75
            self.weapons_list.heading(col, text=col)
            self.weapons_list.column(col, width=width, anchor="center")

        # Pack the first list into the LabelFrame
        self.weapons_list.pack(fill="x", padx=10, pady=5)

        # Create a Add Item Button to close the window
        add_weapon_button = ttk.Button(equip_frame, text="Equip Weapon",
                                       command=lambda: self.open_equipment_weapon_window(chara=chara))
        add_weapon_button.pack(pady=5)

        # Create a Remove Item Button to close the window
        remove_weapon_button = ttk.Button(equip_frame, text="Unequip Weapon",
                                          command=lambda: self.remove_equipped_weapon(chara))
        remove_weapon_button.pack(pady=5)

        ttk.Label(equip_frame, text="Armor", anchor='w').pack(fill='both')
        # Create the second list (Treeview) with 6 columns
        self.armor_list = ttk.Treeview(equip_frame, columns=armour_columns, show="headings", height=3,
                                       style="Custom.Treeview")
        for col in armour_columns:
            self.armor_list.heading(col, text=col)
            self.armor_list.column(col, width=100, anchor="center")

        # Pack the second list into the LabelFrame
        self.armor_list.pack(fill="x", padx=10, pady=5)

        # Create a Add Item Button to close the window
        add_armor_button = ttk.Button(equip_frame, text="Equip Armor",
                                      command=lambda: self.open_equipment_armor_window(chara=chara))
        add_armor_button.pack(pady=5)

        # Create a Remove Item Button to close the window
        remove_armor_button = ttk.Button(equip_frame, text="Unequip Armor",
                                         command=lambda: self.remove_equipped_armor(chara))
        remove_armor_button.pack(pady=5)

        inventory_frame = ttk.LabelFrame(self.inventory_window, text="Inventory", width=200, padding=(10, 10))
        inventory_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        money_frame = ttk.LabelFrame(inventory_frame, text="Money", padding=(10, 10))
        money_frame.pack(fill='x', expand=False)

        ttk.Label(money_frame, text=f"Current Money: {chara.Money} cp", anchor='w').pack(fill='both', expand=True)

        columns = ("Name", "Type", "Weight", "Value", "Amount")
        widths = (150, 100, 50, 50, 70)

        ttk.Label(inventory_frame, text=f"All Items (Double-Click To Change Amount)", anchor='w').pack(fill='both')
        self.inventory_list = ttk.Treeview(inventory_frame, columns=columns, show="headings", height=6,
                                           style="Custom.Treeview")
        for i, col in enumerate(columns):
            self.inventory_list.heading(col, text=col)
            self.inventory_list.column(col, width=widths[i], anchor="center")

        scrollbar = ttk.Scrollbar(inventory_frame, orient="vertical", command=self.inventory_list.yview)
        self.inventory_list.configure(yscrollcommand=scrollbar.set)

        self.inventory_list.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        self.refresh_inventory_lists(chara)

        add_item_button = ttk.Button(inventory_frame, text="Add Item",
                                     command=lambda: self.open_add_item_window(chara, party_menu_root))
        add_item_button.pack(side="bottom", pady=5)

        self.inventory_list.bind("<Double-1>", lambda event: self.open_item_slot_window(event, chara, party_menu_root))

        self.inventory_window.mainloop()

    def open_equipment_weapon_window(self, chara, event=None):
        second_window = tk.Toplevel(self.inventory_window)
        second_window.title(f"Add Weapon ({chara.Base_Name})")
        second_window.geometry("800x300")

        self.position_window(self.inventory_window, second_window)

        second_window.columnconfigure(0, weight=1)

        # Create a LabelFrame for list
        list_frame = ttk.LabelFrame(second_window, text="Item Selection", padding=(10, 10))
        list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        columns = ("Name", "Type", "Damage", "Damage Type", "Range", "Properties", "Amount")

        ttk.Label(list_frame, text="Weapon", anchor='w').pack(fill='both')
        # Create the first list (Treeview) with 6 columns
        self.select_weapons_list = ttk.Treeview(list_frame, columns=columns, show="headings", height=4,
                                                style="Custom.Treeview")
        self.select_weapons_list.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)

        # Create a vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.select_weapons_list.yview)
        self.select_weapons_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=5)

        for col in columns:
            if col == "Properties":
                width = 150
            else:
                width = 75
            self.select_weapons_list.heading(col, text=col)
            self.select_weapons_list.column(col, width=width, anchor="center")

        # Create a Add Item Button to close the window
        equip_weapon_button = ttk.Button(second_window, text="Equip", command=lambda: self.equip_selected_weapon(chara))
        equip_weapon_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.equipment_list_weapons(chara)

    def equipment_list_weapons(self, chara):
        for item in self.select_weapons_list.get_children():
            self.select_weapons_list.delete(item)

        available_list = []
        self.Equipment_Item_Weapon_Dict = {}

        for item, amount in chara.get_inventory_items_as_dictionary().items():
            if item.Item_Type == "weapon":
                available_list.append((item, amount))

        for item in available_list:
            weapon = item[0]
            list_item = self.select_weapons_list.insert("", "end", values=(weapon.Item_Name, weapon.Weapon_Type,
                                                                           f"{weapon.Weapon_Damage} ("
                                                                           f"{shared_data.get_attribute_modifier(chara.Attribute_Strength):+d})",
                                                                           weapon.Weapon_DamageType,
                                                                           f"{weapon.Weapon_Range_Min}/{weapon.Weapon_Range_Max}",
                                                                           weapon.get_additional_info_as_text(chara),
                                                                           item[1]))
            self.Equipment_Item_Weapon_Dict[list_item] = weapon

    def equip_selected_weapon(self, chara):
        selected_items = self.select_weapons_list.selection()
        if len(selected_items) == 0:
            return

        for list_item in selected_items:
            weapon = self.Equipment_Item_Weapon_Dict[list_item]
            chara.Equipment_Weapons.append(weapon)
            chara.remove_item(weapon.ID, 1)

        self.refresh_inventory_lists(chara)
        self.equipment_list_weapons(chara)

    def remove_equipped_weapon(self, chara):
        selected_items = self.weapons_list.selection()
        if len(selected_items) == 0:
            return

        for list_item in selected_items:
            weapon = self.Main_Item_Weapon_Dict[list_item]
            if weapon in chara.Equipment_Weapons:
                chara.Equipment_Weapons.remove(weapon)
                chara.add_item(weapon.ID, 1)

        self.refresh_inventory_lists(chara)

    def open_equipment_armor_window(self, chara, event=None, ):
        second_window = tk.Toplevel(self.inventory_window)
        second_window.title(f"Add Armor ({chara.Base_Name})")
        second_window.geometry("800x300")

        self.position_window(self.inventory_window, second_window)

        second_window.columnconfigure(0, weight=1)

        # Create a LabelFrame for list
        list_frame = ttk.LabelFrame(second_window, text="Item Selection", padding=(10, 10))
        list_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        columns = ("Name", "Type", "AC", "Properties", "Amount")

        ttk.Label(list_frame, text="Armor", anchor='w').pack(fill='both')
        # Create the first list (Treeview) with 6 columns
        self.select_armors_list = ttk.Treeview(list_frame, columns=columns, show="headings", height=4,
                                               style="Custom.Treeview")
        self.select_armors_list.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)

        # Create a vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.select_armors_list.yview)
        self.select_armors_list.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=5)

        for col in columns:
            if col == "Properties":
                width = 150
            else:
                width = 75
            self.select_armors_list.heading(col, text=col)
            self.select_armors_list.column(col, width=width, anchor="center")

        # Create a Add Item Button to close the window
        equip_weapon_button = ttk.Button(second_window, text="Equip", command=lambda: self.equip_selected_armor(chara))
        equip_weapon_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.equipment_list_armors(chara)

    def equipment_list_armors(self, chara):
        for item in self.select_armors_list.get_children():
            self.select_armors_list.delete(item)

        available_list = []
        self.Equipment_Item_Weapon_Dict = {}

        for item, amount in chara.get_inventory_items_as_dictionary().items():
            if item.Item_Type == "armor":
                available_list.append((item, amount))

        for item in available_list:
            armor = item[0]
            total, modified = armor.get_modified_armor_class(chara)
            armour_class_text = f"{total}"
            if modified != 0:
                armour_class_text += f" ({modified:+d})"

            list_item = self.select_armors_list.insert("", "end", values=(armor.Item_Name, armor.Armor_Type,
                                                                          armour_class_text,
                                                                          armor.get_additional_info_as_text(), item[1]))
            self.Equipment_Item_Armor_Dict[list_item] = armor

    def equip_selected_armor(self, chara):
        selected_items = self.select_armors_list.selection()
        if len(selected_items) == 0:
            return

        for list_item in selected_items:
            armor = self.Equipment_Item_Armor_Dict[list_item]
            chara.Equipment_Armors.append(armor)
            chara.remove_item(armor.ID, 1)

        self.refresh_inventory_lists(chara)
        self.equipment_list_armors(chara)

    def remove_equipped_armor(self, chara):
        selected_items = self.armor_list.selection()
        if len(selected_items) == 0:
            return

        for list_item in selected_items:
            armor = self.Main_Item_Armor_Dict[list_item]
            if armor in chara.Equipment_Armors:
                chara.Equipment_Armors.remove(armor)
                chara.add_item(armor.ID, 1)

        self.refresh_inventory_lists(chara)

    def open_item_slot_window(self, event, chara, party_root):
        def set_number(item_ID, current_value, new_value, window):
            diff = new_value - current_value
            if diff > 0:
                chara.add_item(item_ID, diff)
            elif diff < 0:
                chara.remove_item(item_ID, abs(diff))

            self.refresh_inventory_lists(chara)
            window.destroy()

        selected_items = self.inventory_list.selection()

        if len(selected_items) == 0:
            return

        inventory_edit_window = tk.Toplevel(party_root)
        inventory_edit_window.title("Change Amount")

        self.position_window(self.inventory_window, inventory_edit_window)

        selected_item = selected_items[0]
        item = self.Main_Item_BaseItem_Dict[selected_item]
        current_value = chara.Inventory[item.ID]

        label = ttk.Label(inventory_edit_window, text="Change To:")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry = ttk.Entry(inventory_edit_window, width=10)
        entry.grid(row=0, column=1, padx=5, pady=5, sticky="e")
        entry.insert(0, f"{current_value}")

        set_number_button = ttk.Button(inventory_edit_window, text="Confirm",
                                       command=lambda: set_number(item.ID, int(current_value),
                                                                  int(entry.get()), inventory_edit_window))
        set_number_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        close_button = ttk.Button(inventory_edit_window, text="close",
                                  command=inventory_edit_window.destroy)
        close_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    def open_add_item_window(self, chara, party_menu_root):
        def add_item():
            item_id = int(item_combobox.get().split()[0])
            amount = int(entry_amount.get())
            chara.add_item(item_id=item_id, amount=amount)
            self.refresh_inventory_lists(chara)
            self.add_item_window.destroy()

        if self.add_item_window is not None:
            if self.add_item_window.winfo_exists():
                return

        self.add_item_window = tk.Toplevel(party_menu_root)
        self.add_item_window.title(f"Add Item [{chara.Base_Name}]")

        base_frame = ttk.LabelFrame(self.add_item_window, text="Choose Item and Amount", padding=(10, 10))
        base_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.position_window(party_menu_root, self.add_item_window)

        item_dictionary = item_database.Item_Dictionary
        item_list_values = []

        for item_id, item in item_dictionary.items():
            item_list_values.append(f"{item_id} - {item.Item_Name}")

        item_combobox = ttk.Combobox(base_frame, width=25, values=item_list_values, state="readonly")
        item_combobox.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        item_combobox.current(0)

        entry_amount = ttk.Entry(base_frame, width=10)
        entry_amount.grid(row=0, column=1, padx=5, pady=5, sticky="w")

        confirm_button = ttk.Button(base_frame, text="Accept", command=add_item)
        confirm_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        close_button = ttk.Button(base_frame, text="Close", command=self.add_item_window.destroy)
        close_button.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

    def open_enemy_attack_description(self, event=None, enemy_attack=None, root=None):
        def change_name_and_description(texts):
            enemy_attack.name = texts[1].get("1.0", "end-1c")
            enemy_attack.description = texts[2].get("1.0", "end-1c")

        if enemy_attack is None:
            return

        if self.enemy_attack_info_window is not None:
            if self.enemy_attack_info_window.winfo_exists():
                return

        self.enemy_attack_info_window = tk.Toplevel(root)
        self.enemy_attack_info_window.title(f"Attack Info ({enemy_attack.name})")

        if root is not None:
            self.position_window(root, self.enemy_attack_info_window)

        attack_info_frame = ttk.LabelFrame(self.enemy_attack_info_window, text="Info", padding=(10, 10))
        attack_info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        attack_info_labels = ("ID", "Name", "Description")
        attack_info = (enemy_attack.ID, enemy_attack.name, enemy_attack.description)
        box_heights = (1, 1, 10)
        text_boxes = []

        for i in range(len(attack_info)):
            detail_label = ttk.Label(attack_info_frame, text=attack_info_labels[i])
            detail_label.grid(row=i, column=0, sticky="e")

            detail_text_box = tk.Text(attack_info_frame, height=box_heights[i], width=100, wrap="word")
            detail_text_box.grid(row=i, column=1, sticky="w")

            text_boxes.append(detail_text_box)

            detail_text_box.delete("1.0", tk.END)
            detail_text_box.insert(tk.END, attack_info[i])

            if attack_info_labels[i] == "Description":
                detail_text_box.tag_config("bold", font=("Helvetica", 12, "bold"))

                detail_text_box.tag_remove("bold", "1.0", tk.END)

                content = detail_text_box.get("1.0", tk.END)

                pattern = r'\b(\d+)?d\d+\b'

                for match in re.finditer(pattern, content):
                    start_index = match.start()
                    end_index = match.end()

                    # Convert the start and end indexes to Tkinter text indices
                    start = f"1.0 + {start_index} chars"
                    end = f"1.0 + {end_index} chars"

                    # Add the tag "bold" to the matching text
                    detail_text_box.tag_add("bold", start, end)

        attack_action_frame = ttk.LabelFrame(self.enemy_attack_info_window, text="Action", padding=(10, 10))
        attack_action_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        add_attack_button = ttk.Button(attack_action_frame, text="Save Change", width=20,
                                       command=lambda: change_name_and_description(text_boxes))
        add_attack_button.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        remove_attack_button = ttk.Button(attack_action_frame, text="Close", width=20,
                                          command=self.enemy_attack_info_window.destroy)
        remove_attack_button.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")


dude = cm_shared.Character_From_ID_Dictionary[1]

window_manager = OnDemandWindows()
# window_manager.open_inventory_window(dude)

# window_manager.open_magic_window(dude)
# window_manager.open_bonus_window(dude)
# window_manager.open_stats_window(dude)