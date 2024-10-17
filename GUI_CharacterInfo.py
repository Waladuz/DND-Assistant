import tkinter as tk
import os
import glob
from tkinter import ttk
import character
import shared_data
from DataManagers import cm_shared
from PIL import Image, ImageTk

class CharacterWindow:
    def __init__(self):

        self.select_weapons_list = None
        self.select_armors_list = None
        self.armor_list = None
        self.weapons_list = None
        self.list1 = None
        self.portrait_combobox = None
        self.portrait_frame = None
        self.portrait_label = None
        self.chara_combobox = None
        self.root = None
        self.isOpen = False

        self.ComboboxLocation_To_IDs_Dictionary = {}

        self.fields_base = None
        self.fields_attributes = None
        self.fields_skills = None

        self.current_chara = None

        self.Equipment_Item_Weapon_Dict = {}
        self.Equipment_Item_Armor_Dict = {}

        self.Main_Item_Weapon_Dict = {}
        self.Main_Item_Armor_Dict = {}
        self.Main_Item_BaseItem_Dict = {}

        # Set Style
        '''
        self.style = ttk.Style()
        self.style.element_create("Custom.Treeheading.border", "from", "default")
        self.style.layout("Custom.Treeview.Heading", [
            ("Custom.Treeheading.cell", {'sticky': 'nswe'}),
            ("Custom.Treeheading.border", {'sticky': 'nswe', 'children': [
                ("Custom.Treeheading.padding", {'sticky': 'nswe', 'children': [
                    ("Custom.Treeheading.image", {'side': 'right', 'sticky': ''}),
                    ("Custom.Treeheading.text", {'sticky': 'we'})
                ]})
            ]}),
        ])
        self.style.configure("Custom.Treeview.Heading",
                        background="blue", foreground="white", relief="flat")
        self.style.map("Custom.Treeview.Heading",
                  relief=[('active', 'groove'), ('pressed', 'sunken')])
        '''
        return

    def close_window(self, closing_function=None):
        if closing_function is not None:
            closing_function()
        self.root.destroy()

    def load_character_from_change(self, event):
        self.load_character()

    def load_character(self, force_value=-1):
        if force_value != -1:
            chara = cm_shared.get_dictionary()[int(force_value)]
        else:
            index = self.chara_combobox.current()
            value = self.ComboboxLocation_To_IDs_Dictionary[index]
            chara = cm_shared.get_dictionary()[int(value)]

        self.current_chara = chara
        self.current_chara.recalculate_arrays()

        for i in range(len(self.fields_attributes)):
            self.fields_attributes[i].delete(0, tk.END)
            self.fields_attributes[i].insert(0, chara.Attributes_Array[i])

        for i in range(len(self.fields_skills)):
            self.fields_skills[i].delete(0, tk.END)
            self.fields_skills[i].insert(0, chara.Skills_Array[i])

        for i in range(len(self.fields_base)):
            if i in [2, 3, 6]:
                if chara.Bases_Array[i] is not None:
                    self.fields_base[i].set(chara.Bases_Array[i])
                continue

            self.fields_base[i].delete(0, tk.END)
            if chara.Bases_Array[i] is not None:
                self.fields_base[i].insert(0, chara.Bases_Array[i])

        self.current_chara.refresh_equipment(0)
        self.current_chara.refresh_equipment(1)
        self.reload_portrait()
        self.refresh_inventory_list()

    def save_character(self):
        if self.current_chara is None:
            return

        base_data = []
        attribute_data = []
        skill_data = []

        for i in range(len(self.fields_base)):
            base_data.append(self.fields_base[i].get())

        for i in range(len(self.fields_attributes)):
            attribute_data.append(self.fields_attributes[i].get())

        for i in range(len(self.fields_skills)):
            skill_data.append(self.fields_skills[i].get())

        self.current_chara.apply_changes_to_stats(base_data, attribute_data, skill_data)
        self.current_chara.Portrait_ID = self.portrait_combobox.get()
        self.current_chara.save_changes_to_databank()

    def new_character(self):
        new_id = cm_shared.create_new_character_with_id()
        cm_shared.refresh_available_character_list()
        self.load_character(force_value=new_id)
        self.refresh_player_selection_list(None)

    def refresh_player_selection_list(self, event):
        player_ids, player_names = cm_shared.get_all_ids_and_player_names()
        entries = []
        self.ComboboxLocation_To_IDs_Dictionary = {}

        for i in range(len(player_ids)):
            text_entry = f"{player_ids[i]} - {player_names[i]}"
            entries.append(text_entry)
            self.ComboboxLocation_To_IDs_Dictionary[i] = player_ids[i]

        self.chara_combobox['values'] = entries

    def reload_portrait(self, event=None, is_preview=False):
        # LoadImage
        if is_preview:
            image_path = fr"images\{self.portrait_combobox.get()}.png"
        else:
            image_path = fr"images\{self.current_chara.Portrait_ID}.png"
            self.portrait_combobox.set(self.current_chara.Portrait_ID)
        if image_path is None:
            return
        image = Image.open(image_path).resize((200, 200))
        tk_image = ImageTk.PhotoImage(image)

        self.portrait_label.configure(image=tk_image, relief="sunken")
        self.portrait_label.image = tk_image
        self.get_list_of_portraits()
        self.portrait_combobox['values'] = self.get_list_of_portraits()

    def get_list_of_portraits(self):
        images_folder_path = os.path.join(os.getcwd(), 'images')

        png_files = glob.glob(os.path.join(images_folder_path, '*.png'))

        file_names = [os.path.basename(file) for file in png_files]
        file_names_without_end = []

        for name in file_names:
            file_names_without_end.append(name[:-4])

        return file_names_without_end

    def preview_selected_portrait(self, event=None):
        self.reload_portrait(is_preview=True)

    def refresh_inventory_list(self, event=None):
        if self.current_chara is None:
            return

        for item in self.weapons_list.get_children():
            self.weapons_list.delete(item)

        for item in self.armor_list.get_children():
            self.armor_list.delete(item)

        for item in self.list1.get_children():
            self.list1.delete(item)

        weapons = self.current_chara.Equipment_Weapons
        armors = self.current_chara.Equipment_Armors
        inventory = self.current_chara.get_inventory_items_as_dictionary()

        itemized_list = []
        self.Main_Item_Weapon_Dict = {}
        self.Main_Item_Armor_Dict = {}
        self.Main_Item_BaseItem_Dict = {}

        for weapon in weapons:
            list_item = self.weapons_list.insert("", "end", values=(weapon.Item_Name, weapon.Weapon_Type,
                                                 f"{weapon.Weapon_Damage} ("
                                                 f"{shared_data.get_attribute_modifier(self.current_chara.Attribute_Strength):+d})",
                                                        weapon.Weapon_DamageType,
                                                 f"{weapon.Weapon_Range_Min}/{weapon.Weapon_Range_Max}",
                                                        weapon.get_additional_info_as_text(self.current_chara)))
            self.Main_Item_Weapon_Dict[list_item] = weapon

        for armor in armors:
            total, modified = armor.get_modified_armor_class(self.current_chara)
            armour_class_text = f"{total}"
            if modified != 0:
                armour_class_text += f" ({modified:+d})"
            list_item = self.armor_list.insert("", "end", values=(armor.Item_Name, armor.Armor_Type,
                                                      armour_class_text, armor.get_additional_info_as_text()))
            self.Main_Item_Armor_Dict[list_item] = armor

        for item, amount in inventory.items():
            entries = (item.Item_Name, item.Item_Type, item.Item_Weight, item.Item_Value, amount)
            list_item = self.list1.insert("", "end", values=entries)
            self.Main_Item_BaseItem_Dict[list_item] = item

    def open_equipment_weapon_window(self, event=None, mode=1):
        second_window = tk.Toplevel(self.root)
        second_window.title("Add Weapon")
        second_window.geometry("800x300")

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
        equip_weapon_button = ttk.Button(second_window, text="Equip", command=self.equip_selected_weapon)
        equip_weapon_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.equipment_list_weapons()

    def equipment_list_weapons(self):
        for item in self.select_weapons_list.get_children():
            self.select_weapons_list.delete(item)

        available_list = []
        self.Equipment_Item_Weapon_Dict = {}

        for item, amount in self.current_chara.get_inventory_items_as_dictionary().items():
            if item.Item_Type == "weapon":
                available_list.append((item, amount))

        for item in available_list:
            weapon = item[0]
            list_item = self.select_weapons_list.insert("", "end", values=(weapon.Item_Name, weapon.Weapon_Type,
                                                 f"{weapon.Weapon_Damage} ("
                                                 f"{shared_data.get_attribute_modifier(self.current_chara.Attribute_Strength):+d})",
                                                        weapon.Weapon_DamageType,
                                                 f"{weapon.Weapon_Range_Min}/{weapon.Weapon_Range_Max}",
                                                        weapon.get_additional_info_as_text(self.current_chara), item[1]))
            self.Equipment_Item_Weapon_Dict[list_item] = weapon

    def equip_selected_weapon(self):
        selected_items = self.select_weapons_list.selection()
        if len(selected_items) == 0:
            return

        for list_item in selected_items:
            weapon = self.Equipment_Item_Weapon_Dict[list_item]
            self.current_chara.Equipment_Weapons.append(weapon)
            self.current_chara.remove_item(weapon.ID, 1)

        self.refresh_inventory_list()
        self.equipment_list_weapons()

    def remove_equipped_weapon(self):
        selected_items = self.weapons_list.selection()
        if len(selected_items) == 0:
            return

        for list_item in selected_items:
            weapon = self.Main_Item_Weapon_Dict[list_item]
            if weapon in self.current_chara.Equipment_Weapons:
                self.current_chara.Equipment_Weapons.remove(weapon)
                self.current_chara.add_item(weapon.ID, 1)

        self.refresh_inventory_list()

    def open_equipment_armor_window(self, event=None, mode=1):
        second_window = tk.Toplevel(self.root)
        second_window.title("Add Armor")
        second_window.geometry("800x300")

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
        equip_weapon_button = ttk.Button(second_window, text="Equip", command=self.equip_selected_armor)
        equip_weapon_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.equipment_list_armors()

    def equipment_list_armors(self):
        for item in self.select_armors_list.get_children():
            self.select_armors_list.delete(item)

        available_list = []
        self.Equipment_Item_Weapon_Dict = {}

        for item, amount in self.current_chara.get_inventory_items_as_dictionary().items():
            if item.Item_Type == "armor":
                available_list.append((item, amount))

        for item in available_list:
            armor = item[0]
            total, modified = armor.get_modified_armor_class(self.current_chara)
            armour_class_text = f"{total}"
            if modified != 0:
                armour_class_text += f" ({modified:+d})"

            list_item = self.select_armors_list.insert("", "end", values=(armor.Item_Name, armor.Armor_Type,
                                                      armour_class_text, armor.get_additional_info_as_text(), item[1]))
            self.Equipment_Item_Armor_Dict[list_item] = armor

    def equip_selected_armor(self):
        selected_items = self.select_armors_list.selection()
        if len(selected_items) == 0:
            return

        for list_item in selected_items:
            armor = self.Equipment_Item_Armor_Dict[list_item]
            self.current_chara.Equipment_Armors.append(armor)
            self.current_chara.remove_item(armor.ID, 1)

        self.refresh_inventory_list()
        self.equipment_list_armors()

    def remove_equipped_armor(self):
        selected_items = self.armor_list.selection()
        if len(selected_items) == 0:
            return

        for list_item in selected_items:
            armor = self.Main_Item_Armor_Dict[list_item]
            if armor in self.current_chara.Equipment_Armors:
                self.current_chara.Equipment_Armors.remove(armor)
                self.current_chara.add_item(armor.ID, 1)

        self.refresh_inventory_list()

    def open_item_slot_window(self, event, chara):
        def set_number(item_ID, current_value, new_value, window):
            diff = new_value - current_value
            if diff > 0:
                self.current_chara.add_item(item_ID, diff)
            elif diff < 0:
                self.current_chara.remove_item(item_ID, abs(diff))

            self.refresh_inventory_list()
            window.destroy()

        selected_items = self.list1.selection()

        if len(selected_items) == 0:
            return

        inventory_edit_window = tk.Toplevel(self.root)
        inventory_edit_window.title("Change Amount")

        selected_item = selected_items[0]
        item = self.Main_Item_BaseItem_Dict[selected_item]
        current_value = self.current_chara.Inventory[item.ID]

        label = ttk.Label(inventory_edit_window, text="Change To:")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry = ttk.Entry(inventory_edit_window, width=10)
        entry.grid(row=0, column=1, padx=5, pady=5, sticky="e")
        entry.insert(0, f"{current_value}")

        # Create a Add Item Button to close the window
        set_number_button = ttk.Button(inventory_edit_window, text="Confirm",
                                         command=lambda: set_number(item.ID, int(current_value),
                                                                    int(entry.get()), inventory_edit_window))
        set_number_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")


        # Create a Add Item Button to close the window
        close_button = ttk.Button(inventory_edit_window, text="close",
                                         command=inventory_edit_window.destroy)
        close_button.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")

    def open_window(self, chara = None, other_root = None, refresh_function = None):
        # Create the main window
        if other_root is None:
            self.root = tk.Tk()
        else:
            self.root = tk.Toplevel(other_root)
        self.root.title("Character Sheet Input Window")


        # Configure the main window grid to allow resizing
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=0)
        self.root.columnconfigure(2, weight=1)

        # Create a LabelFrame for the attributes
        base_frame = ttk.LabelFrame(self.root, text="Base", width=200, padding=(10, 10))
        base_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Character Selection
        self.chara_combobox = ttk.Combobox(base_frame, width=15,
                                           values=cm_shared.get_all_ids_from_available_characters(),
                                           state="readonly")
        self.chara_combobox.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.refresh_player_selection_list(None)
        self.chara_combobox.current(0)
        self.chara_combobox.bind("<FocusIn>", self.refresh_player_selection_list)
        self.chara_combobox.bind("<<ComboboxSelected>>", func=self.load_character_from_change)

        self.portrait_frame = ttk.LabelFrame(base_frame, text="Portrait", width=50, padding=(10, 10))
        self.portrait_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        # LoadImage
        image_path = r"images\002.png"
        image = Image.open(image_path).resize((200, 200))

        if other_root is None:
            app_root = self.root
        else:
            app_root = other_root

        tk_image = ImageTk.PhotoImage(image, master=app_root)

        self.portrait_label = ttk.Label(self.portrait_frame, image=tk_image, relief="sunken")
        self.portrait_label.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")

        self.portrait_combobox = ttk.Combobox(self.portrait_frame, width=15,
                                           values=self.get_list_of_portraits,
                                           state="readonly")
        self.portrait_combobox.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.portrait_combobox.bind("<<ComboboxSelected>>", func=self.preview_selected_portrait)

        base_entries = []

        chara_frame = ttk.LabelFrame(base_frame, text="Character Data", width=50, padding=(10, 10))
        chara_frame.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        # Labels and Entry fields for six attributes
        base_labels = ["ID", "Name", "Race", "Class", "Level", "Exp. Points", "Alignment", "Player Name", "HP Max",
                       "Initiative", "Speed", "AC"]
        races = [
            "Dwarf", "Elf", "Halfling", "Human",
            "Dragonborn", "Gnome", "Half-Elf",
            "Half-Orc", "Tiefling"
        ]
        classes = [
            "Barbarian", "Bard", "Cleric", "Druid",
            "Fighter", "Monk", "Paladin", "Ranger",
            "Rogue", "Sorcerer", "Warlock", "Wizard"
        ]
        alignments = [
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ]

        for i, label_text in enumerate(base_labels):
            a = i // 2
            b = i % 2

            label = ttk.Label(chara_frame, text=label_text)
            label.grid(row=a+1, column=2*b, padx=5, pady=5, sticky="e")

            if i == 2:
                alignment_combobox = ttk.Combobox(chara_frame, width=15, values=races, state="readonly")
                alignment_combobox.grid(row=a+1, column=2*b+1, padx=5, pady=5, sticky="nsew")
                base_entries.append(alignment_combobox)
            elif i == 3:
                alignment_combobox = ttk.Combobox(chara_frame, width=15, values=classes, state="readonly")
                alignment_combobox.grid(row=a+1, column=2*b+1, padx=5, pady=5, sticky="nsew")
                base_entries.append(alignment_combobox)
            elif i == 6:
                alignment_combobox = ttk.Combobox(chara_frame, width=15, values=alignments, state="readonly")
                alignment_combobox.grid(row=a+1, column=2*b+1, padx=5, pady=5, sticky="nsew")
                base_entries.append(alignment_combobox)
            else:
                # Create an entry field for each attribute
                entry = ttk.Entry(chara_frame, width=20)
                entry.grid(row=a+1, column=2*b+1, padx=5, pady=5, sticky="e")
                # Store the entry widgets in a list for future access
                base_entries.append(entry)

        self.fields_base = base_entries

        # Create a LabelFrame for the attributes
        #attributes_frame = ttk.LabelFrame(base_frame, text="Attributes", width=10, padding=(10, 10))
        #attributes_frame.grid(column=0, padx=10, pady=10, sticky="nsew")

        # Create a LabelFrame for the Actions
        actions_frame = ttk.LabelFrame(base_frame, text="Actions", width=10, padding=(10, 10))
        actions_frame.grid(column=0, padx=5, pady=5, sticky="nsew")

        # Create a New Button to close the window
        new_button = ttk.Button(actions_frame, text="New Character", command=self.new_character)
        new_button.pack(pady=2, side="left")

        # Create a Save Button to close the window
        save_button = ttk.Button(actions_frame, text="Save Character", command=self.save_character)
        save_button.pack(pady=2, side="left")

        # Create a Load Button to close the window
        load_button = ttk.Button(actions_frame, text="Load Character", command=self.load_character)
        load_button.pack(pady=2, side="left")

        # Create a Close Button to close the window
        close_button = ttk.Button(actions_frame, text="Close", command=lambda:self.close_window(refresh_function))
        close_button.pack(pady=2, side="right")

        # Create a LabelFrame for the skills, placed to the right of the attributes frame
        more_frame = ttk.LabelFrame(self.root, text="More", padding=(10, 10))
        more_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Create a LabelFrame for the skills, placed to the right of the attributes frame
        skills_frame = ttk.LabelFrame(more_frame, text="Skills", padding=(10, 10))
        skills_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Create a LabelFrame for the skills, placed to the right of the attributes frame
        bonus_frame = ttk.LabelFrame(more_frame, text="Bonus", padding=(10, 10))
        bonus_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        label = ttk.Label(bonus_frame, text="Sneeze")
        label.grid(row=0, column=0, padx=5, pady=5, sticky="e")

        # Labels and Entry fields for skills
        skills_labels = ["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
                         "History", "Insight", "Intimidation", "Investigation", "Medicine",
                         "Nature", "Perception", "Performance", "Persuasion", "Religion",
                         "Sleight of Hand", "Stealth", "Survival"]
        skills_entries = []

        # Labels and Entry fields for six attributes
        attributes_labels = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        attributes_entries = []

        for i, label_text in enumerate(attributes_labels):
            # Create a label for each attribute
            label = ttk.Label(skills_frame, text=label_text)
            label.grid(row=i, column=0, padx=5, pady=5, sticky="e")

            # Create an entry field for each attribute
            entry = ttk.Entry(skills_frame, width=5)
            entry.grid(row=i, column=1, padx=5, pady=5, sticky="nsew")
            attributes_entries.append(entry)

            # Store the entry widgets in a list for future access

        self.fields_attributes = attributes_entries

        for i, label_text in enumerate(skills_labels):
            label = ttk.Label(skills_frame, text=label_text)
            label.grid(row=i, column=3, padx=5, pady=5, sticky="e")

            entry = ttk.Entry(skills_frame, width=5)
            entry.grid(row=i, column=4, padx=5, pady=5, sticky="w")

            skills_entries.append(entry)

        self.fields_skills = skills_entries

        # Create a LabelFrame for the items
        items_frame = ttk.LabelFrame(self.root, text="Items", padding=(10, 10))
        items_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        items_frame.columnconfigure(0, weight=1)

        # Equipment
        equip_frame = ttk.LabelFrame(items_frame, text="Equipment", padding=(10, 10), height=200)
        equip_frame.pack(fill="x", expand=True, padx=10, pady=10)

        # Define columns for the lists
        columns = ("Name", "Type", "Damage", "Damage Type", "Range", "Properties")
        armour_columns = ("Name", "Type", "AC", "Properties")

        ttk.Label(equip_frame, text="Weapon", anchor='w').pack(fill='both')
        # Create the first list (Treeview) with 6 columns
        self.weapons_list = ttk.Treeview(equip_frame, columns=columns, show="headings", height=3, style="Custom.Treeview")
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
        add_weapon_button = ttk.Button(equip_frame, text="Equip Weapon", command=self.open_equipment_weapon_window)
        add_weapon_button.pack(pady=5)

        # Create a Remove Item Button to close the window
        remove_weapon_button = ttk.Button(equip_frame, text="Unequip Weapon", command=self.remove_equipped_weapon)
        remove_weapon_button.pack(pady=5)

        ttk.Label(equip_frame, text="Armor", anchor='w').pack(fill='both')
        # Create the second list (Treeview) with 6 columns
        self.armor_list = ttk.Treeview(equip_frame, columns=armour_columns, show="headings", height=3, style="Custom.Treeview")
        for col in armour_columns:
            self.armor_list.heading(col, text=col)
            self.armor_list.column(col, width=100, anchor="center")

        # Pack the second list into the LabelFrame
        self.armor_list.pack(fill="x", padx=10, pady=5)

        # Create a Add Item Button to close the window
        add_armor_button = ttk.Button(equip_frame, text="Equip Armor", command=self.open_equipment_armor_window)
        add_armor_button.pack(pady=5)

        # Create a Remove Item Button to close the window
        remove_armor_button = ttk.Button(equip_frame, text="Unequip Armor", command=self.remove_equipped_armor)
        remove_armor_button.pack(pady=5)

        # All Items
        # Define columns for the list
        columns = ("Name", "Type", "Weight", "Value", "Amount")

        # Create the Treeview widget with 4 columns
        ttk.Label(equip_frame, text="All Items (Double-Click To Change Amount)", anchor='w').pack(fill='both')
        self.list1 = ttk.Treeview(equip_frame, columns=columns, show="headings", height=6, style="Custom.Treeview")
        for col in columns:
            self.list1.heading(col, text=col)
            self.list1.column(col, width=50, anchor="center")

        # Create a vertical scrollbar for the Treeview
        scrollbar = ttk.Scrollbar(equip_frame, orient="vertical", command=self.list1.yview)
        self.list1.configure(yscrollcommand=scrollbar.set)

        # Pack the Treeview and scrollbar into the LabelFrame
        self.list1.pack(side="left", fill="both", expand=True, padx=(0, 5), pady=5)
        scrollbar.pack(side="right", fill="y", pady=5)

        self.list1.bind("<Double-1>", self.open_item_slot_window)

        if chara is None:
            self.load_character_from_change(None)
        else:
            self.load_character(chara.ID)
        # Run the Tkinter event loop

        if other_root is not None:
            self.root.protocol("WM_DELETE_WINDOW", refresh_function)
        else:
            self.root.mainloop()


charaWindow = CharacterWindow()
#charaWindow.open_window()
