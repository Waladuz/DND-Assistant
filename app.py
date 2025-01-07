import queue
from datetime import datetime
import sqlite3
from flask import Flask, render_template, redirect, url_for, request, session
import tkinter as tk
from tkinter import ttk
from typing import Optional, Tuple, Dict, Any
import socket
import threading

import item
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
    "Tobi": 1,
    "Nik": 2,
    "Nadir": 3,
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

                    event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    event_description = f"Confirmed Login: {username}"
                    self.event_queue.put((event_time, event_description))

                    return redirect(url_for("character", character_id=character_id))
                else:
                    return "Invalid username or password", 401
            return render_template("login.html")

        @self.app.route("/character/<int:character_id>")
        def character(character_id):
            if "user" not in session:
                return redirect(url_for("login"))
            user = session["user"]
            test_chara: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            chara_data = self.convert_chara_to_dict(test_chara)
            print(len(test_chara.Inventory))

            test_inventory: dict = test_chara.get_inventory_items_as_dictionary()
            inventory_data: dict = {}
            item_group: list = []

            for item_obj, item_amount in test_inventory.items():
                inventory_data[item_obj.Item_Name] = {"type": item_obj.Item_Type, "amount": item_amount,
                                                      "info": item_obj.get_details_as_text(test_chara),
                                                      "item_id": item_obj.ID}

            for item_id, item_obj in item.item_database.Item_Dictionary.items():
                item_group.append({"id": item_id, "name": item_obj.Item_Name})

            return render_template("character.html", character=chara_data, inventory=inventory_data,
                                   all_items=item_group, character_id=character_id)

        @self.app.route('/add_item/<int:character_id>', methods=['POST'])
        def add_item(character_id, amount=1):
            if "user" not in session:
                return redirect(url_for("login"))

            # Ensure the logged-in user is modifying their own character
            username = session["user"]
            #if IDS[username] != character_id:
            #    return "Unauthorized access", 403

            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            #if not character:
            #    return "Character not found", 404

            item_id = int(request.form.get('item_id'))

            event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            event_description = f"Item Add: {username} - {amount} {item_database.Item_Dictionary[item_id].Item_Name}"
            self.event_queue.put((event_time, event_description))

            character.add_item(item_id, abs(amount))

            return redirect(url_for("character", character_id=character_id))

        @self.app.route('/remove_item/<int:character_id>', methods=['POST'])
        def remove_item(character_id):
            if "user" not in session:
                return redirect(url_for("login"))

            # Ensure the logged-in user is modifying their own character
            username = session["user"]
            # if IDS[username] != character_id:
            #    return "Unauthorized access", 403

            character: Character = DataManagers.cm_shared.get_dictionary()[character_id]
            # if not character:
            #    return "Character not found", 404

            item_id = int(request.form.get('item_id'))

            event_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            event_description = f"Item Remove: {username} - {item_database.Item_Dictionary[item_id].Item_Name}"
            self.event_queue.put((event_time, event_description))

            character.remove_item(item_id, abs(1))

            return redirect(url_for("character", character_id=character_id))

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
