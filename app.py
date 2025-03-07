import re
import queue
from datetime import datetime
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Tuple, Dict, Any, List
import socket
import threading


import item
import shared_data
from character import Character
from item import Item, item_database

import DataManagers

ACCOUNTS = {
    "Tobi": "cockblocker",
    "Nik": "sahnefurz",
    "Nadir": "werwer",
    "Dominik": "bossmang"
}

IDS = {
    "Dominik": 4
}


class WebsiteControl:
    def __init__(self):
        self.local_ip: str = ""
        self.app = Flask(__name__)
        self.app.secret_key = "e447c35316426c234c336ce24f3fc0d4226220c0"

        self.ip_address_label = None
        self.ip_status_label = None

        self.tree = None
        self.event_queue = None

        self.website_window: Optional[tk.Tk] = None

        self.setup_routes()

    def get_local_ip(self):
        """Retrieve the local IP address."""
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # Doesn't have to connect, just opens a socket to a public address
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = "127.0.0.1"  # Fallback to localhost
        finally:
            s.close()
        return ip

    def add_event_to_log_db(self, time_stamp, event_text):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        column_names = "time, event"

        insert_query = f"""
                        INSERT INTO website_log ({column_names})
                        VALUES (?, ?)
                        """

        cursor.execute(insert_query, [time_stamp, event_text])
        connection.commit()
        connection.close()

    def open_window(self, main_window):
        def save_ip_to_clipboard():
            self.website_window.clipboard_clear()
            self.website_window.clipboard_append(f"http://{self.local_ip}:5000")

        if self.website_window is not None:
            if self.website_window.winfo_exists():
                return

        self.website_window = tk.Toplevel(main_window)
        self.website_window.title(f"Website Control")

        base_frame = ttk.LabelFrame(self.website_window, text="Control Panel", padding=(10, 10))
        base_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)

        start_button = ttk.Button(base_frame, text="Start Host", command=self.run_website)
        start_button.grid(row=0, column=0, sticky="nswe", padx=2, pady=2)

        self.ip_status_label = ttk.Label(base_frame, text="Unactive")
        self.ip_status_label.grid(row=0, column=1, sticky="nswe", padx=2, pady=2)

        ip_label = ttk.Label(base_frame, text="IP-Address:")
        ip_label.grid(row=1, column=0, sticky="nswe", padx=2, pady=2)

        self.ip_address_label = ttk.Label(base_frame, text="---.---.-.---")
        self.ip_address_label.grid(row=1, column=1, sticky="nswe", padx=2, pady=2)

        copy_to_clipboard_button = ttk.Button(base_frame, text="📋", width=4, command=save_ip_to_clipboard)
        copy_to_clipboard_button.grid(row=1, column=2, sticky="nswe", padx=2, pady=2)

        self.local_ip = self.get_local_ip()

        self.ip_address_label.configure(text=f"{self.local_ip}")

        log_frame = ttk.LabelFrame(self.website_window, text="Control Panel", padding=(10, 10))
        log_frame.grid(row=1, column=0, sticky="nswe", padx=10, pady=10)

        self.tree = ttk.Treeview(log_frame, columns=("Time", "Event"), show="headings")
        self.tree.heading("Time", text="Time")
        self.tree.heading("Event", text="Event")
        self.tree.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y", pady=5)

        self.event_queue = queue.Queue()

        self.website_window.after(100, self.process_queue)

    def process_queue(self):
        while not self.event_queue.empty():
            event_time, event_description = self.event_queue.get()
            self.tree.insert("", "end", values=(event_time, event_description))
            self.add_event_to_log_db(event_time, event_description)
        self.website_window.after(100, self.process_queue)

    def setup_routes(self):
        @self.app.route("/", methods=["GET", "POST"])
        def login():
            if request.method == "POST":
                username = request.form["username"]
                password = request.form["password"]
                if username in ACCOUNTS and ACCOUNTS[username] == password:
                    session["user"] = username
                    character_id = IDS[username]
                    session["chara_id"] = character_id

                    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    event_description = f"Confirmed Login: {username}"
                    self.event_queue.put((event_time, event_description))

                    return redirect(url_for("character"))
                else:
                    return "Invalid username or password", 401
            return render_template("login.html")

        @self.app.route("/character")
        def character():
            if "user" not in session:
                return redirect(url_for("login"))
            user = session["user"]
            character_id = session["chara_id"]
            test_chara: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            chara_data = self.convert_chara_to_dict(test_chara)

            item_group: list = []

            for item_id, item_obj in item.item_database.Item_Dictionary.items():
                item_group.append({"id": item_id, "name": item_obj.Item_Name})

            return render_template("character.html", character=chara_data,
                                   all_items=item_group, character_id=character_id)

        @self.app.route('/stats', methods=['POST'])
        def stats():
            if "user" not in session:
                return redirect(url_for("login"))

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            chara_data = self.convert_chara_to_dict(character)

            return render_template("stats.html", character=chara_data)

        @self.app.route('/additem', methods=['POST'])
        def additem():
            if "user" not in session:
                return redirect(url_for("login"))

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            chara_data = self.convert_chara_to_dict(character)

            all_items = [{"item_id": listitem.ID, "name": listitem.Item_Name}
                         for listitem in list(item.item_database.Item_Dictionary.values())]
            shopping_list = [{"item_id": shop_item.ID, "name": shop_item.Item_Name} for shop_item in
                             character.Shopping_List]

            return render_template("additem.html", shopping_list=shopping_list, all_items=all_items)

        @self.app.route('/bonus', methods=['POST'])
        def bonus():
            if "user" not in session:
                return redirect(url_for("login"))

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            chara_data = self.convert_chara_to_dict(character)

            bonus_list = []
            bonuses = character.get_current_level_bonuses_dictionary()

            for level, skill in bonuses.items():
                bonus_list.append({"level": level,
                                   "name": skill["name"],
                                   "description": skill["description"]})

            return render_template("bonus.html", character=chara_data, bonus_list=bonus_list)
        @self.app.route('/magic', methods=['POST'])
        def magic():
            if "user" not in session:
                return redirect(url_for("login"))

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            chara_data = self.convert_chara_to_dict(character)

            magic_points = []
            max_mp = character.Max_Magic_Points
            current_mp = character.Magic_Points

            for level in max_mp.keys():
                fill_symbol = "🟢"
                empty_symbol = "⚫"
                bar = current_mp[level] * fill_symbol + (max_mp[level] - current_mp[level]) * empty_symbol

                magic_points.append({"level": level, "amount": bar})

            spell_list = []

            for spell in character.Spells:
                spell_list.append({"name": spell.Magic_Name,
                                   "level": spell.Magic_Level,
                                   "school": spell.Magic_School,
                                   "duration": spell.Magic_Duration,
                                   "range": spell.Magic_Range,
                                   "aoe": spell.Magic_Area,
                                   "save": spell.get_saving_throw_type(),
                                   "damage": spell.Magic_Damage_Type,
                                   "description": spell.Magic_Detail
                                   })

            return render_template("magic.html", character=chara_data, mptable=magic_points,
                                   spells=spell_list)

        @self.app.template_filter("bold_dice")
        def bold_dice_filter(value):
            """Format text: Make dice rolls bold and 'At Higher Levels' bold."""

            dice_pattern = r'\b\d+d\d+\b'  # Matches dice rolls like 3d6, 1d8, 2d20
            level_pattern = r'\bAt Higher Levels\b'  # Matches "At Higher Levels" exactly

            value = re.sub(dice_pattern, r'<strong style="font-size: 1.2em;">\g<0></strong>', value)
            value = re.sub(level_pattern, r'<strong style="color: blue; font-size: 1.3em;">\g<0></strong>', value)
            value = value.replace("\n", "<br>")
            return value

        @self.app.route('/change_mp', methods=['POST'])
        def change_mp_to_level():
            data = request.get_json()

            level = int(data.get("level"))
            amount = int(data.get("amount"))

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            character.change_magic_points(level=level, amount=amount)

            max_mp = character.Max_Magic_Points
            current_mp = character.Magic_Points

            fill_symbol = "🟢"
            empty_symbol = "⚫"
            bar = current_mp[level] * fill_symbol + (max_mp[level] - current_mp[level]) * empty_symbol

            username = session["user"]
            event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            event_description = f"MP Change: {username} | level: {level} change:{amount:+d} "
            self.event_queue.put((event_time, event_description))

            return jsonify(success=True, new_value=bar)

        @self.app.route('/inventory', methods=['POST'])
        def inventory():
            if "user" not in session:
                return redirect(url_for("login"))

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            chara_data = self.convert_chara_to_dict(character)

            test_inventory: dict = character.get_inventory_items_as_dictionary()
            inventory_data: dict = {}
            weapon_data = [{"id": weapon.ID, "name": weapon.Item_Name,
                            "damage": f"{weapon.Weapon_Damage} "
                                      f"({shared_data.get_attribute_modifier(character.Attribute_Strength):+d})",
                            "type": weapon.Weapon_Type,
                            "info": weapon.get_details_as_text(character)}
                           for weapon in character.Equipment_Weapons]

            armor_data = [
                {"id": armor.ID, "name": armor.Item_Name, "ac": f"{armor.get_modified_armor_class(character)[0]}"
                                                                f" ({armor.get_modified_armor_class(character)[1]:+d})",
                 "info": armor.get_details_as_text(character)} for armor in character.Equipment_Armors]

            for item_obj, item_amount in test_inventory.items():
                inventory_data[item_obj.Item_Name] = {"type": item_obj.Item_Type, "amount": item_amount,
                                                      "info": item_obj.get_details_as_text(character),
                                                      "item_id": item_obj.ID}

            current_ac = character.get_current_ac()[0]

            return render_template("inventory.html", character=chara_data, inventory=inventory_data,
                                   character_id=character_id, weaponlist=weapon_data, armorlist=armor_data,
                                   current_ac=current_ac)

        @self.app.route('/unequip_item', methods=['POST'])
        def unequip_item():
            if "user" not in session:
                return redirect(url_for("login"))

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]

            data = request.get_json()
            item_id = int(data.get("item_id"))

            current_item: Item = item_database.Item_Dictionary[int(item_id)]

            if current_item.Item_Type.lower() == "weapon":
                character.Equipment_Weapons.remove(current_item)
                character.add_item(current_item.ID, 1)
            elif current_item.Item_Type.lower() == "armor":
                character.Equipment_Armors.remove(current_item)
                character.add_item(current_item.ID, 1)

            test_inventory: dict = character.get_inventory_items_as_dictionary()
            inventory_data: dict = {}
            weapon_data = [{"id": weapon.ID, "name": weapon.Item_Name,
                            "damage": f"{weapon.Weapon_Damage} "
                                      f"({shared_data.get_attribute_modifier(character.Attribute_Strength):+d})",
                            "type": weapon.Weapon_Type,
                            "info": weapon.get_details_as_text(character)}
                           for weapon in character.Equipment_Weapons]

            armor_data =[
                {"id": armor.ID, "name": armor.Item_Name, "ac": f"{armor.get_modified_armor_class(character)[0]}"
                                                                f" ({armor.get_modified_armor_class(character)[1]:+d})",
                 "info": armor.get_details_as_text(character)} for armor in character.Equipment_Armors]

            for item_obj, item_amount in test_inventory.items():
                inventory_data[item_obj.Item_Name] = {"type": item_obj.Item_Type, "amount": item_amount,
                                                      "info": item_obj.get_details_as_text(character),
                                                      "item_id": item_obj.ID}

            current_ac = character.get_current_ac()[0]

            return jsonify(success=True, inventory=inventory_data, weaponlist=weapon_data, armorlist=armor_data,
                           current_ac=current_ac)

        @self.app.route('/equip_item', methods=['POST'])
        def equip_item():
            if "user" not in session:
                return redirect(url_for("login"))

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]

            data = request.get_json()
            item_id = int(data.get("item_id"))

            current_item: Item = item_database.Item_Dictionary[int(item_id)]

            if current_item.Item_Type.lower() == "weapon":
                character.Equipment_Weapons.append(current_item)
                character.remove_item(current_item.ID, 1)
            elif current_item.Item_Type.lower() == "armor":
                character.Equipment_Armors.append(current_item)
                character.remove_item(current_item.ID, 1)

            test_inventory: dict = character.get_inventory_items_as_dictionary()
            inventory_data: dict = {}
            weapon_data = [{"id": weapon.ID, "name": weapon.Item_Name,
                            "damage": f"{weapon.Weapon_Damage} "
                                      f"({shared_data.get_attribute_modifier(character.Attribute_Strength):+d})",
                            "type": weapon.Weapon_Type,
                            "info": weapon.get_details_as_text(character)}
                           for weapon in character.Equipment_Weapons]

            armor_data = [
                {"id": armor.ID, "name": armor.Item_Name, "ac": f"{armor.get_modified_armor_class(character)[0]}"
                                                                f" ({armor.get_modified_armor_class(character)[1]:+d})",
                 "info": armor.get_details_as_text(character)} for armor in character.Equipment_Armors]

            for item_obj, item_amount in test_inventory.items():
                inventory_data[item_obj.Item_Name] = {"type": item_obj.Item_Type, "amount": item_amount,
                                                      "info": item_obj.get_details_as_text(character),
                                                      "item_id": item_obj.ID}

            current_ac = character.get_current_ac()[0]

            return jsonify(success=True, inventory=inventory_data, weaponlist=weapon_data, armorlist=armor_data,
                           current_ac=current_ac)

        @self.app.route('/remove_item', methods=['POST'])
        def remove_item():
            if "user" not in session:
                return redirect(url_for("login"))

            username = session["user"]

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]

            data = request.get_json()
            item_id = int(data.get("item_id"))

            event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            event_description = f"Item Remove: {username} - {item_database.Item_Dictionary[item_id].Item_Name}"
            self.event_queue.put((event_time, event_description))

            character.remove_item(item_id, abs(1))

            test_inventory: dict = character.get_inventory_items_as_dictionary()
            inventory_data: dict = {}

            for item_obj, item_amount in test_inventory.items():
                inventory_data[item_obj.Item_Name] = {"type": item_obj.Item_Type, "amount": item_amount,
                                                      "info": item_obj.get_details_as_text(character),
                                                      "item_id": item_obj.ID}

            return jsonify(success=True, inventory=inventory_data)

        @self.app.route("/add_to_shopping_list", methods=["POST"])
        def add_to_shopping_list():
            """Add an item to the shopping list"""
            data = request.get_json()
            item_id = int(data.get("item_id"))
            item: Item = next((new_item for new_item in item_database.Item_Dictionary.values() if new_item.ID == item_id), None)

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]

            character.add_item_to_shopping_cart(item)

            shopping_list = [{"item_id": shop_item.ID, "name": shop_item.Item_Name} for shop_item in character.Shopping_List]

            return jsonify(success=True, shopping_list=shopping_list)

        @self.app.route("/remove_from_shopping_list", methods=["POST"])
        def remove_from_shopping_list():
            """Remove an item from the shopping list"""
            data = request.get_json()
            item_id = int(data.get("item_id"))
            item: Item = next((item for item in item_database.Item_Dictionary.values() if item.ID == item_id), None)

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]

            character.remove_item_to_shopping_cart(item)

            shopping_list = [{"item_id": shop_item.ID, "name": shop_item.Item_Name} for shop_item in
                             character.Shopping_List]

            return jsonify(success=True, shopping_list=shopping_list)

        @self.app.route("/add_to_inventory", methods=["POST"])
        def add_to_inventory():
            """Move all shopping list items to inventory"""
            username = session["user"]

            data = request.get_json()
            bought_stuff = data['quantities']

            character_id = session["chara_id"]
            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]

            buy_list = ""
            for stuff_id, amount in bought_stuff.items():
                amount = int(amount)
                stuff_id = int(stuff_id)
                new_item = item_database.Item_Dictionary[stuff_id]
                buy_list += f"\n{amount}X {new_item.Item_Name}"

            result = messagebox.askyesno(f"{username}: Item Request", "This asshole wants:" + buy_list)
            if not result:
                return jsonify(success=False)

            for stuff_id, amount in bought_stuff.items():
                amount = int(amount)
                stuff_id = int(stuff_id)
                new_item = item_database.Item_Dictionary[stuff_id]
                character.add_item(stuff_id, amount)

                event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                event_description = f"Item Added: {username} - {amount} X {new_item.Item_Name}"
                self.event_queue.put((event_time, event_description))

            character.Shopping_List.clear()

            return jsonify(success=True)

        @self.app.route("/search_items", methods=["POST"])
        def search_items():
            """Search for items by name (partial match)"""
            data = request.get_json()
            query = data.get("query", "").lower()

            results: List[Item] = [item for item in item_database.Item_Dictionary.values() if query in item.Item_Name.lower()]

            final_list = []

            for hit in results:
                final_list.append({"name": hit.Item_Name,
                                   "item_id": hit.ID})

            return jsonify(final_list)

        @self.app.route("/denied")
        def denied():
            return render_template("denied.html")

        @self.app.route("/logout")
        def logout():
            session.pop("user", None)
            return redirect(url_for("login"))

    def run_website(self):
        server_thread = threading.Thread(target=self.run_server)
        server_thread.daemon = True  # Daemon thread will close when the main program exits
        server_thread.start()
        self.ip_status_label.configure(text="ACTIVE")

    def run_server(self):
        self.app.run(host="0.0.0.0", port=5000)

    def convert_chara_to_dict(self, chara: Character) -> dict[str, Any]:
        chara.recalculate_arrays()

        attributes_labels = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        attributes_values = chara.Attributes_Array
        attribute_dict = dict(zip(attributes_labels, attributes_values))

        skill_labels = ["Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
                         "History", "Insight", "Intimidation", "Investigation", "Medicine",
                         "Nature", "Perception", "Performance", "Persuasion", "Religion",
                         "Sleight of Hand", "Stealth", "Survival"]
        skill_values = chara.Skills_Array
        skill_dict = dict(zip(skill_labels, skill_values))

        chara_dict = {"name": chara.Base_Name,
                      "race": chara.Base_Race,
                      "class": chara.Base_Class,
                      "hp": chara.get_hp_as_text(),
                      "level": chara.Base_Level,
                      "exp": chara.Base_Exp,
                      "attributes": attribute_dict,
                      "skills": skill_dict}

        return chara_dict


website = WebsiteControl()
