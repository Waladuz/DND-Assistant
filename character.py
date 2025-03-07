import sqlite3

import item
import shared_data
import shared_data as sd
from item import item_database
import re
import random
from typing import Dict, List


class Character:
    def __init__(self, character_id):
        self.ID = character_id
        self.data = self.get_character_from_id(character_id)
        if self.data is None:
            print("no matching character found")
            return

        self.Base_Name = self.data[1]
        self.Base_Level = self.data[2]
        self.Base_Exp = self.data[3]
        self.Base_Race = self.data[4]
        self.Base_Class = self.data[5]
        self.Base_Initiative = self.data[6]
        self.Base_Speed = self.data[7]
        self.Base_Background = self.data[8]
        self.Base_Alignment = self.data[9]
        self.Base_PlayerName = self.data[47]
        self.Base_AC = self.data[52]

        self.Bases_Array = []

        self.Attribute_Strength = self.data[10]
        self.Attribute_Dexterity = self.data[11]
        self.Attribute_Constitution = self.data[12]
        self.Attribute_Intelligence = self.data[13]
        self.Attribute_Wisdom = self.data[14]
        self.Attribute_Charisma = self.data[15]

        self.Attributes_Array = []

        self.Skill_Acrobatics = self.data[16]
        self.Skill_AnimalHandling = self.data[17]
        self.Skill_Arcana = self.data[18]
        self.Skill_Athletics = self.data[19]
        self.Skill_Deception = self.data[20]
        self.Skill_History = self.data[21]
        self.Skill_Insight = self.data[22]
        self.Skill_Intimidation = self.data[23]
        self.Skill_Investigation = self.data[24]
        self.Skill_Medicine = self.data[25]
        self.Skill_Nature = self.data[26]
        self.Skill_Perception = self.data[27]
        self.Skill_Performance = self.data[28]
        self.Skill_Persuasion = self.data[29]
        self.Skill_Religion = self.data[30]
        self.Skill_SleightOfHand = self.data[31]
        self.Skill_Stealth = self.data[32]
        self.Skill_Survival = self.data[33]

        self.Skills_Array = []

        self.Death_Saves_Successes = self.data[34]
        self.Death_Saves_Failures = self.data[35]

        self.Saving_Throw_Strength = self.data[36]
        self.Saving_Throw_Dexterity = self.data[37]
        self.Saving_Throw_Constitution = self.data[38]
        self.Saving_Throw_Intelligence = self.data[39]
        self.Saving_Throw_Wisdom = self.data[40]
        self.Saving_Throw_Charisma = self.data[41]

        self.Lore_Personality = self.data[42]
        self.Lore_Ideals = self.data[43]
        self.Lore_Bonds = self.data[44]
        self.Lore_Flaws = self.data[45]

        self.Portrait_ID = self.data[48]
        self.Level_Up_Notes = self.data[49]

        self.Battle_HP = self.data[50]
        self.Battle_HP_Max = self.data[51]

        self.Money = self.data[53]

        self.Inventory = {}
        self.Equipment_Weapons = []
        self.Equipment_Armors = []

        self.Spells = []

        self.Shopping_List: List[item.Item] = []

        self.Magic_Points: Dict[int, int] = {}
        self.Max_Magic_Points: Dict[int, int] = {}

        self.Temp_Coordinate = (0, 0)
        self.set_magic_points()

        self.recalculate_arrays()
        self.load_spells_from_db()
        self.get_inventory_from_db()

    def recalculate_arrays(self):
        self.Bases_Array = [
            self.ID, self.Base_Name, self.Base_Race, self.Base_Class,
            self.Base_Level, self.Base_Exp, self.Base_Alignment, self.Base_PlayerName, self.Battle_HP_Max,
            self.Base_Initiative, self.Base_Speed, self.Base_AC, self.Money
        ]
        self.Attributes_Array = [
            self.Attribute_Strength,
            self.Attribute_Dexterity,
            self.Attribute_Constitution,
            self.Attribute_Intelligence,
            self.Attribute_Wisdom,
            self.Attribute_Charisma
        ]
        self.Skills_Array = [
            self.Skill_Acrobatics,
            self.Skill_AnimalHandling,
            self.Skill_Arcana,
            self.Skill_Athletics,
            self.Skill_Deception,
            self.Skill_History,
            self.Skill_Insight,
            self.Skill_Intimidation,
            self.Skill_Investigation,
            self.Skill_Medicine,
            self.Skill_Nature,
            self.Skill_Perception,
            self.Skill_Performance,
            self.Skill_Persuasion,
            self.Skill_Religion,
            self.Skill_SleightOfHand,
            self.Skill_Stealth,
            self.Skill_Survival
        ]

    def add_item_to_shopping_cart(self, new_item: item.Item):
        if new_item in self.Shopping_List:
            return

        self.Shopping_List.append(new_item)
        list(set(self.Shopping_List))

    def remove_item_to_shopping_cart(self, new_item: item.Item):
        if new_item not in self.Shopping_List:
            return

        self.Shopping_List.remove(new_item)

    def set_magic_points(self):
        if self.Base_Class not in shared_data.MP_BY_CLASS.keys():
            return

        mp_list: List[int] = shared_data.MP_BY_CLASS[self.Base_Class][int(self.Base_Level)]
        self.Magic_Points.clear()
        self.Max_Magic_Points.clear()

        for i in range(len(mp_list)):
            self.Max_Magic_Points[i + 1] = mp_list[i]
            self.Magic_Points[i + 1] = mp_list[i]

    def change_magic_points(self, level: int, amount: int):
        if len(self.Magic_Points) == 0 or level not in list(range(1, 21)):
            return

        current_value = self.Magic_Points[level]
        current_max = self.Max_Magic_Points[level]

        current_value += amount
        current_value = max(0, min(current_value, current_max))
        self.Magic_Points[level] = current_value

    def get_current_ac(self):
        text = ""

        total = self.Base_AC
        text += f"Base: {self.Base_AC}"
        for armor in self.Equipment_Armors:
            armor_total, dex_mod = armor.get_modified_armor_class(self)
            total += int(armor_total)
            text += f"\n{armor.Item_Name}: {armor_total}"
            if abs(dex_mod) > 0:
                text += f" (DEX:{dex_mod:+d})"

        return total, text

    def load_spells_from_db(self):
        self.Spells = []

        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()
        sql_query = "SELECT * FROM character_spells WHERE character_ID = ?"
        cursor.execute(sql_query, (self.ID,))
        for row in cursor.fetchall():
            spell = sd.magic_table.id_magic_dictionary[row[1]]
            self.Spells.append(spell)

    def add_item(self, item_id, amount):
        for inventory_id, inventory_amount in self.Inventory.items():
            if inventory_id == item_id:
                self.Inventory[inventory_id] += amount
                return

        self.Inventory[item_id] = amount
        self.Inventory = dict(sorted(self.Inventory.items()))

    def remove_item(self, item_id, amount):
        for inventory_id, inventory_amount in self.Inventory.items():
            print(f"{item_id}")
            if inventory_id == item_id:
                print("Some Case")
                if inventory_amount > amount:
                    self.Inventory[inventory_id] -= amount  # Decrease the amount if sufficient quantity exists
                elif inventory_amount == amount:
                    self.Inventory.pop(item_id)  # Remove item if amount matches exactly
                    self.Inventory = dict(sorted(self.Inventory.items()))
                return

    def apply_changes_to_stats(self, new_base_array, new_attributes_array, new_skills_array):
        self.ID = new_base_array[0]
        self.Base_Name = new_base_array[1]
        self.Base_Race = new_base_array[2]
        self.Base_Class = new_base_array[3]
        self.Base_Level = int(new_base_array[4])
        self.Base_Exp = int(new_base_array[5])
        self.Base_Alignment = new_base_array[6]
        self.Base_PlayerName = new_base_array[7]
        self.Battle_HP_Max = int(new_base_array[8])
        self.Base_Initiative = int(new_base_array[9])
        self.Base_Speed = int(new_base_array[10])
        self.Base_AC = int(new_base_array[11])
        self.Money = int(new_base_array[12])

        self.Attribute_Strength = int(new_attributes_array[0])
        self.Attribute_Dexterity = int(new_attributes_array[1])
        self.Attribute_Constitution = int(new_attributes_array[2])
        self.Attribute_Intelligence = int(new_attributes_array[3])
        self.Attribute_Wisdom = int(new_attributes_array[4])
        self.Attribute_Charisma = int(new_attributes_array[5])

        self.Skill_Acrobatics = int(new_skills_array[0])
        self.Skill_AnimalHandling = int(new_skills_array[1])
        self.Skill_Arcana = int(new_skills_array[2])
        self.Skill_Athletics = int(new_skills_array[3])
        self.Skill_Deception = int(new_skills_array[4])
        self.Skill_History = int(new_skills_array[5])
        self.Skill_Insight = int(new_skills_array[6])
        self.Skill_Intimidation = int(new_skills_array[7])
        self.Skill_Investigation = int(new_skills_array[8])
        self.Skill_Medicine = int(new_skills_array[9])
        self.Skill_Nature = int(new_skills_array[10])
        self.Skill_Perception = int(new_skills_array[11])
        self.Skill_Performance = int(new_skills_array[12])
        self.Skill_Persuasion = int(new_skills_array[13])
        self.Skill_Religion = int(new_skills_array[14])
        self.Skill_SleightOfHand = int(new_skills_array[15])
        self.Skill_Stealth = int(new_skills_array[16])
        self.Skill_Survival = int(new_skills_array[17])

    def save_changes_to_databank(self):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        Base_Dictionary = {
            "ID": self.ID,
            "Name": self.Base_Name,
            "Race": self.Base_Race,
            "Class": self.Base_Class,
            "Level": self.Base_Level,
            "Exp": self.Base_Exp,
            "Alignment": self.Base_Alignment,
            "PlayerName": self.Base_PlayerName,
            "Max HP": self.Battle_HP_Max,
            "Initiative": self.Base_Initiative,
            "Speed": self.Base_Speed,
            "AC": self.Base_AC,
            "Money": self.Money
        }

        self.Attributes_Dictionary = {
            "Strength": self.Attribute_Strength,
            "Dexterity": self.Attribute_Dexterity,
            "Constitution": self.Attribute_Constitution,
            "Intelligence": self.Attribute_Intelligence,
            "Wisdom": self.Attribute_Wisdom,
            "Charisma": self.Attribute_Charisma
        }

        Skills_Dictionary = {
            "Acrobatics": self.Skill_Acrobatics,
            "AnimalHandling": self.Skill_AnimalHandling,
            "Arcana": self.Skill_Arcana,
            "Athletics": self.Skill_Athletics,
            "Deception": self.Skill_Deception,
            "History": self.Skill_History,
            "Insight": self.Skill_Insight,
            "Intimidation": self.Skill_Intimidation,
            "Investigation": self.Skill_Investigation,
            "Medicine": self.Skill_Medicine,
            "Nature": self.Skill_Nature,
            "Perception": self.Skill_Perception,
            "Performance": self.Skill_Performance,
            "Persuasion": self.Skill_Persuasion,
            "Religion": self.Skill_Religion,
            "SleightOfHand": self.Skill_SleightOfHand,
            "Stealth": self.Skill_Stealth,
            "Survival": self.Skill_Survival
        }

        additional_fields = {
            "level_up_notes": self.Level_Up_Notes
        }

        # Base
        for key, value in Base_Dictionary.items():
            column_name = sd.DATABANK_BASE[key]
            sql_query = f"UPDATE character SET {column_name} = ? WHERE id = ?"
            cursor.execute(sql_query, (value, self.ID))

        # Attributes
        for key, value in self.Attributes_Dictionary.items():
            column_name = sd.DATABANK_ATTRIBUTES[key]
            sql_query = f"UPDATE character SET {column_name} = ? WHERE id = ?"
            cursor.execute(sql_query, (value, self.ID))

        # Skills
        for key, value in Skills_Dictionary.items():
            column_name = sd.DATABANK_SKILLS[key]
            sql_query = f"UPDATE character SET {column_name} = ? WHERE id = ?"
            cursor.execute(sql_query, (value, self.ID))

        for key, value in additional_fields.items():
            column_name = key
            sql_query = f"UPDATE character SET {column_name} = ? WHERE id = ?"
            cursor.execute(sql_query, (value, self.ID))

        sql_query = f"UPDATE character SET portrait_id = ? WHERE id = ?"
        cursor.execute(sql_query, (self.Portrait_ID, self.ID))

        # Commit the changes to the database
        connection.commit()

        self.save_inventory_and_equipment_to_db()
        self.save_spells_to_db()

    def save_spells_to_db(self):
        connection = sqlite3.connect("assets.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM character_spells WHERE character_id = ?", (self.ID,))

        for spell in self.Spells:
            cursor.execute("INSERT INTO character_spells (character_id, magic_id) VALUES (?, ?)",
                                (self.ID, spell.Magic_ID))

        connection.commit()

    def save_inventory_and_equipment_to_db(self):
        connection = sqlite3.connect("assets.db")
        cursor = connection.cursor()
        cursor.execute("DELETE FROM equipment WHERE player_id = ?", (self.ID,))
        cursor.execute("DELETE FROM inventory WHERE characterId = ?", (self.ID,))

        # Insert new equipment items from self.Equipment_Weapons
        for item in self.Equipment_Weapons:
            cursor.execute("INSERT INTO equipment (player_id, item_id) VALUES (?, ?)",
                                (self.ID, item.ID))
        for item in self.Equipment_Armors:
            cursor.execute("INSERT INTO equipment (player_id, item_id) VALUES (?, ?)",
                                (self.ID, item.ID))

        for item_id, amount in self.Inventory.items():
            cursor.execute("INSERT INTO inventory (characterId, itemId, amount) VALUES (?, ?, ?)",
                           (self.ID, item_id, amount))

        connection.commit()

    def add_equipment(self, item, mode):
        if mode == 1:
            if item.Item_Type != "weapon":
                return
            self.Equipment_Weapons.append(item)

        if mode == 2:
            if item.Item_Type != "armor":
                return
            self.Equipment_Armors.append(item)

    def get_inventory_from_db(self):
        connection = sqlite3.connect('assets.db')
        self.Inventory = {}

        cursor = connection.cursor()
        sql_query = "SELECT * FROM inventory WHERE characterID = ?"

        cursor.execute(sql_query, (self.ID,))

        for row in cursor.fetchall():
            self.Inventory[row[1]] = row[3]

        self.Inventory = dict(sorted(self.Inventory.items()))

        cursor = connection.cursor()

        self.Equipment_Weapons = []
        self.Equipment_Armors = []

        sql_query = "SELECT * FROM equipment WHERE player_ID = ?"
        cursor.execute(sql_query, (self.ID,))
        for row in cursor.fetchall():
            item = item_database.get_item_from_id_in_table(row[1])
            if item.Item_Type == "weapon":
                self.Equipment_Weapons.append(item)
                print(item.Item_Name)
            if item.Item_Type == "armor":
                self.Equipment_Armors.append(item)

        connection.close()

    def save_inventory_to_db(self):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        # Step 1: Delete all inventory items for the given character ID
        delete_query = "DELETE FROM inventory WHERE characterID = ?"
        cursor.execute(delete_query, (self.ID,))
        connection.commit()

        insert_query = """
                INSERT INTO inventory (characterID, itemID, isEquipped, amount)
                VALUES (?, ?, NULL, ?)
                """

        for item_id, amount in self.Inventory.items():
            cursor.execute(insert_query, (self.ID, item_id, amount))

        connection.commit()

    def get_inventory_items_as_dictionary(self):
        items_object_dictionary = {}

        for key, amount in self.Inventory.items():
            items_object_dictionary[item_database.get_item_from_id_in_table(key)] = amount

        return items_object_dictionary

    def refresh_equipment(self, mode):
        if mode == 0:
            self.Equipment_Weapons = []
            connection = sqlite3.connect('assets.db')
            cursor = connection.cursor()
            sql_query = "SELECT * FROM equipment WHERE player_ID = ?"
            cursor.execute(sql_query, (self.ID,))
            for row in cursor.fetchall():
                item = item_database.get_item_from_id_in_table(row[1])
                if item.Item_Type == "weapon":
                    self.Equipment_Weapons.append(item)
            return self.Equipment_Weapons
        if mode == 1:
            self.Equipment_Armors = []
            connection = sqlite3.connect('assets.db')
            cursor = connection.cursor()
            sql_query = "SELECT * FROM equipment WHERE player_ID = ?"
            cursor.execute(sql_query, (self.ID,))
            for row in cursor.fetchall():
                item = item_database.get_item_from_id_in_table(row[1])
                if item.Item_Type == "armor":
                    self.Equipment_Armors.append(item)
            return self.Equipment_Armors

    def get_current_level_bonuses_dictionary(self):
        bonuses = {}

        if self.Base_Class not in sd.SKILLS_CLASS_TO_BONUSES:
            return bonuses

        bonus_dictionary = sd.SKILLS_CLASS_TO_BONUSES[self.Base_Class]

        for level, skill_name in bonus_dictionary.items():
            if level <= self.Base_Level:
                bonuses[level] = skill_name

        return bonuses

    def deal_damage(self, amount):
        self.Battle_HP -= amount
        self.Battle_HP = min([max([self.Battle_HP, 0]), self.Battle_HP_Max])

    def get_hp_as_text(self):
        if self.Battle_HP == 0:
            return "DEAD"

        return f"{self.Battle_HP}/{self.Battle_HP_Max}"

    @staticmethod
    def get_character_from_id(character_id):
        try:
            connection = sqlite3.connect('assets.db')
            cursor = connection.cursor()

            query = "SELECT * FROM character WHERE id = ?"
            cursor.execute(query, (character_id,))
            result = cursor.fetchone()  # Fetch one result
            connection.close()
            if result:
                return result
            else:
                return None
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return None


class Enemy:
    def __init__(self, enemy_id):
        enemy_data = self.get_enemy_from_id(enemy_id)

        self.ID = enemy_data[0]
        self.Enemy_Name = enemy_data[1]
        self.Enemy_Alignment = enemy_data[2]
        self.Enemy_WeightType = enemy_data[3]

        self.Enemy_HP = enemy_data[4]
        self.Enemy_HP_Roll = enemy_data[4]
        self.Enemy_Speed = enemy_data[5]
        self.Enemy_AC_Base = enemy_data[6]
        self.XP_On_Defeat = enemy_data[7]

        self.Portrait_ID = enemy_data[37]

        self.Attribute_Strength = enemy_data[8]
        self.Attribute_Dexterity = enemy_data[9]
        self.Attribute_Constitution = enemy_data[10]
        self.Attribute_Intelligence = enemy_data[11]
        self.Attribute_Wisdom = enemy_data[12]
        self.Attribute_Charisma = enemy_data[13]

        self.Battle_Ability = enemy_data[32]
        self.Battle_Damage_Immunity = enemy_data[33]
        self.Battle_Condition_Immunity = enemy_data[34]
        self.Battle_Condition_Senses = enemy_data[35]
        self.Battle_Languages = enemy_data[36]
        self.Battle_Actions = []

        self.Skill_Acrobatics = enemy_data[14]
        self.Skill_AnimalHandling = enemy_data[15]
        self.Skill_Arcana = enemy_data[16]
        self.Skill_Athletics = enemy_data[17]
        self.Skill_Deception = enemy_data[18]
        self.Skill_History = enemy_data[19]
        self.Skill_Insight = enemy_data[20]
        self.Skill_Intimidation = enemy_data[21]
        self.Skill_Investigation = enemy_data[22]
        self.Skill_Medicine = enemy_data[23]
        self.Skill_Nature = enemy_data[24]
        self.Skill_Perception = enemy_data[25]
        self.Skill_Performance = enemy_data[26]
        self.Skill_Persuasion = enemy_data[27]
        self.Skill_Religion = enemy_data[28]
        self.Skill_SleightOfHand = enemy_data[29]
        self.Skill_Stealth = enemy_data[30]
        self.Skill_Survival = enemy_data[31]

        self.Temp_ID = 0
        self.Temp_CharaName = ""
        self.Temp_HP = 1
        self.Temp_HP_Max = 1

        self.Temp_Coordinate = (0, 0)

        self.get_all_attacks_of_enemy()

    def get_db_dictionary(self):
        values_dictionary = {
            "enemy_id": self.ID,
            "name": self.Enemy_Name,
            "alignment": self.Enemy_Alignment,
            "weight_class": self.Enemy_WeightType,
            "hp": self.Enemy_HP_Roll,
            "speed": self.Enemy_Speed,
            "ac": self.Enemy_AC_Base,
            "xp": self.XP_On_Defeat,
            "att_strength": self.Attribute_Strength,
            "att_dexterity": self.Attribute_Dexterity,
            "att_constitution": self.Attribute_Constitution,
            "att_intelligence": self.Attribute_Intelligence,
            "att_wisdom": self.Attribute_Wisdom,
            "att_charisma": self.Attribute_Charisma,
            "sk_acrobatics": self.Skill_Acrobatics,
            "sk_animal_handling": self.Skill_AnimalHandling,
            "sk_arcana": self.Skill_Arcana,
            "sk_athletics": self.Skill_Athletics,
            "sk_deception": self.Skill_Deception,
            "sk_history": self.Skill_History,
            "sk_insight": self.Skill_Insight,
            "sk_intimidation": self.Skill_Intimidation,
            "sk_investigation": self.Skill_Investigation,
            "sk_medicine": self.Skill_Medicine,
            "sk_nature": self.Skill_Nature,
            "sk_perception": self.Skill_Perception,
            "sk_performance": self.Skill_Performance,
            "sk_persuasion": self.Skill_Persuasion,
            "sk_religion": self.Skill_Religion,
            "sk_soh": self.Skill_SleightOfHand,
            "sk_stealth": self.Skill_Stealth,
            "sk_survival": self.Skill_Survival,
            "info_ability": self.Battle_Ability,
            "info_dam_imm": self.Battle_Damage_Immunity,
            "info_con_imm": self.Battle_Condition_Immunity,
            "info_senses": self.Battle_Condition_Senses,
            "info_languages": self.Battle_Languages,
            "portrait_id": self.Portrait_ID
        }

        return values_dictionary

    def update_values(self, base_array, attribute_array, skills_array, infos_array):
        self.ID = base_array[0]
        self.Enemy_Name = base_array[1]
        self.Enemy_Alignment = base_array[2]
        self.Enemy_WeightType = base_array[3]
        self.Enemy_HP_Roll = base_array[4]
        self.Enemy_Speed = base_array[5]
        self.Enemy_AC_Base = base_array[6]
        self.XP_On_Defeat = base_array[7]

        self.Attribute_Strength = attribute_array[0]
        self.Attribute_Dexterity = attribute_array[1]
        self.Attribute_Constitution = attribute_array[2]
        self.Attribute_Intelligence = attribute_array[3]
        self.Attribute_Wisdom = attribute_array[4]
        self.Attribute_Charisma = attribute_array[5]

        self.Skill_Acrobatics = skills_array[0]
        self.Skill_AnimalHandling = skills_array[1]
        self.Skill_Arcana = skills_array[2]
        self.Skill_Athletics = skills_array[3]
        self.Skill_Deception = skills_array[4]
        self.Skill_History = skills_array[5]
        self.Skill_Insight = skills_array[6]
        self.Skill_Intimidation = skills_array[7]
        self.Skill_Investigation = skills_array[8]
        self.Skill_Medicine = skills_array[9]
        self.Skill_Nature = skills_array[10]
        self.Skill_Perception = skills_array[11]
        self.Skill_Performance = skills_array[12]
        self.Skill_Persuasion = skills_array[13]
        self.Skill_Religion = skills_array[14]
        self.Skill_SleightOfHand = skills_array[15]
        self.Skill_Stealth = skills_array[16]
        self.Skill_Survival = skills_array[17]

        self.Battle_Ability = infos_array[0]
        self.Battle_Damage_Immunity = infos_array[1]
        self.Battle_Condition_Immunity = infos_array[2]
        self.Battle_Condition_Senses = infos_array[3]
        self.Battle_Languages = infos_array[4]

    def save_enemy_to_db(self):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        db_dictionary = self.get_db_dictionary()

        for key, value in db_dictionary.items():
            column_name = key
            sql_query = f"UPDATE enemies SET {column_name} = ? WHERE enemy_id = ?"
            cursor.execute(sql_query, (value, self.ID))

        # Step 1: Delete all inventory items for the given character ID
        delete_query = "DELETE FROM enemy_attacks WHERE enemy_id = ?"
        cursor.execute(delete_query, (self.ID,))
        connection.commit()

        insert_query = """
                    INSERT INTO enemy_attacks (enemy_id, attack_id, attack_name, attack_description)
                    VALUES (?, ?, ?, ?)
                    """

        for attack in self.Battle_Actions:
            cursor.execute(insert_query, (self.ID, attack.ID, attack.name, attack.description))

        connection.commit()

    def get_base_array(self):
        return [self.ID, self.Enemy_Name, self.Enemy_Alignment, self.Enemy_WeightType,
                self.Enemy_HP_Roll, self.Enemy_Speed, self.Enemy_AC_Base, self.XP_On_Defeat]

    def get_attributes_array(self):
        return [self.Attribute_Strength, self.Attribute_Dexterity, self.Attribute_Constitution,
                self.Attribute_Intelligence, self.Attribute_Wisdom, self.Attribute_Charisma]

    def get_battle_info_array(self):
        return [self.Battle_Ability, self.Battle_Damage_Immunity, self.Battle_Condition_Immunity,
                self.Battle_Condition_Senses, self.Battle_Languages, self.Battle_Actions]

    def get_skill_array(self):
        return [self.Skill_Acrobatics, self.Skill_AnimalHandling, self.Skill_Arcana, self.Skill_Athletics,
                self.Skill_Deception, self.Skill_History, self.Skill_Insight, self.Skill_Intimidation,
                self.Skill_Investigation, self.Skill_Medicine, self.Skill_Nature, self.Skill_Perception,
                self.Skill_Performance, self.Skill_Persuasion, self.Skill_Religion, self.Skill_SleightOfHand,
                self.Skill_Stealth, self.Skill_Survival]

    def get_all_attacks_of_enemy(self):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        query = "SELECT * FROM enemy_attacks WHERE enemy_id = ?"
        cursor.execute(query, (self.ID,))
        result = cursor.fetchall()

        self.Battle_Actions = []
        connection.close()

        for attack_data in result:
            self.Battle_Actions.append(EnemyAttack(attack_data))

    def set_new_battle_entity(self, values, auto_hp=True):
        self.Temp_ID = values[0]
        self.Temp_CharaName = values[1]
        self.Temp_HP = values[2]
        self.Temp_HP_Max = values[3]

        if auto_hp:
            self.auto_set_hp()

    def auto_set_hp(self):
        dice_values = self.get_hp_dice_roll_logic()

        if dice_values is None:
            current_sum = 5
        else:
            current_sum = 0
            for i in range(int(dice_values[0])):
                current_sum += random.randint(1, int(dice_values[1]))

            current_sum += int(dice_values[2])

        self.Temp_HP_Max = current_sum
        self.Temp_HP = self.Temp_HP_Max

        print(current_sum)

    def get_highest_id_of_attacks(self):
        if len(self.Battle_Actions) == 0:
            return 1

        highest_value = 0
        for attack in self.Battle_Actions:
            if attack.ID >= highest_value:
                highest_value = attack.ID
                print(highest_value)

        return highest_value + 1

    def remove_attack_by_id(self, attack_id):
        if len(self.Battle_Actions) == 0:
            return

        self.Battle_Actions = [attack for attack in self.Battle_Actions if attack.ID != attack_id]

    def get_attack_by_id(self, attack_id):
        if len(self.Battle_Actions) == 0:
            return None

        hits = [attack for attack in self.Battle_Actions if attack.ID == attack_id]
        if len(hits) == 0:
            return None

        return hits[0]

    def get_hp_dice_roll_logic(self):
        hp_text = self.Enemy_HP_Roll
        pattern = r"(\d+)d(\d+)\s*([+-]?\s*\d+)?"
        match = re.match(pattern, hp_text)

        if match:
            amount_of_dice = int(match.group(1))  # The number of dice
            dice_type = int(match.group(2))  # The type of dice (e.g., 20-sided)
            offset = int(match.group(3).replace(" ", "")) if match.group(3) else 0  # The modifier (+1, -2, etc.)
            return [amount_of_dice, dice_type, offset]
        else:
            return None

    def get_hp_as_text(self):
        if self.Temp_HP == 0:
            return "DEAD"

        return f"{self.Temp_HP}/{self.Temp_HP_Max}"

    def deal_damage(self, amount):
        self.Temp_HP -= amount
        self.Temp_HP = min([max([self.Temp_HP, 0]), self.Temp_HP_Max])

    @staticmethod
    def get_enemy_from_id(character_id):
        try:
            connection = sqlite3.connect('assets.db')
            cursor = connection.cursor()

            query = "SELECT * FROM enemies WHERE enemy_id = ?"
            cursor.execute(query, (character_id,))
            result = cursor.fetchone()  # Fetch one result
            connection.close()
            if result:
                return result
            else:
                return None
        except sqlite3.Error as e:
            print(f"An error occurred: {e}")
            return None


class EnemyAttack:
    def __init__(self, attack_data):
        self.ID = int(attack_data[1])
        self.enemy_id = int(attack_data[0])
        self.name = attack_data[2]
        self.description = attack_data[3]

