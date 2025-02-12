import sqlite3
import shared_data
from typing import List, Optional


class Item:
    def __init__(self, item_id):
        self.ID = item_id

        self.Item_Data = self.get_item_from_id(self.ID)
        if self.Item_Data is None:
            return
        self.Item_Name = self.Item_Data[1]
        self.Item_Type = self.Item_Data[2]
        self.Item_Value = self.Item_Data[3]
        self.Item_Weight = self.Item_Data[4]

    def get_details_as_text(self, chara) -> str:
        return ''

    @staticmethod
    def get_item_from_id(item_id):
        # Connect to the SQLite database called "assets.db"
        try:
            connection = sqlite3.connect('assets.db')
            cursor = connection.cursor()

            # Query to select data from the "item" table by id
            query = "SELECT * FROM items WHERE id = ?"

            # Execute the query
            cursor.execute(query, (item_id,))
            result = cursor.fetchone()  # Fetch one result

            # Close the connection
            connection.close()

            # If a character was found, return the result
            if result:
                return result
            else:
                # If no character was found, return None
                return None
        except sqlite3.Error as e:
            # Handle any potential errors
            print(f"An error occurred: {e}")
            return None


class Armor(Item):
    def __init__(self, item_id):
        self.ID = item_id

        self.Item_Data = self.get_item_from_id(self.ID)
        if self.Item_Data is None:
            return
        self.Item_Name = self.Item_Data[1]
        self.Item_Type = self.Item_Data[2]
        self.Item_Value = self.Item_Data[3]
        self.Item_Weight = self.Item_Data[4]

        self.Armor_Type = self.Item_Data[7]
        self.Armor_ArmorClass = self.Item_Data[8]
        self.Armor_DexterityModifier = self.Item_Data[9]
        self.Armor_Strength = self.Item_Data[10]
        self.Armor_StealthReduction = (self.Item_Data[11] == "x")

    def get_details_as_text(self, chara) -> str:
        return (f'AC: {self.get_modified_armor_class(chara)[0]} '
                f'({self.get_modified_armor_class(chara)[1]:+d}), '
                f'{self.Armor_Type}, {self.get_additional_info_as_text()}')

    def get_modified_armor_class(self, chara):
        total_amount = int(self.Armor_ArmorClass)
        dex_modifier = shared_data.get_attribute_modifier(chara.Attribute_Dexterity)
        total_amount += dex_modifier
        return total_amount, dex_modifier

    def get_additional_info_as_text(self):
        properties_text = ""
        if self.Armor_StealthReduction:
            properties_text += "Stealth Disadvantage"
        if self.Armor_Strength != 0 and self.Armor_Strength != "0":
            if properties_text != "":
                properties_text += ", "
            print(self.Armor_Strength)
            properties_text += f"Strength Req: {self.Armor_Strength}"
        if self.Armor_DexterityModifier != 0:
            if properties_text != "":
                properties_text += ", "
            properties_text += "Dex. Modifier"
            if self.Armor_DexterityModifier == 2:
                properties_text += " (Max. 2"

        return properties_text


class Weapon(Item):
    def __init__(self, item_id):
        self.ID = item_id

        self.Item_Data = self.get_item_from_id(self.ID)
        if self.Item_Data is None:
            return
        self.Item_Name = self.Item_Data[1]
        self.Item_Type = self.Item_Data[2]
        self.Item_Value = self.Item_Data[3]
        self.Item_Weight = self.Item_Data[4]

        self.Weapon_Type = self.Item_Data[12]
        self.Weapon_Damage = self.Item_Data[13]
        self.Weapon_DamageType = self.Item_Data[14]

        self.Weapon_Range_Min = self.Item_Data[16]
        self.Weapon_Range_Max = self.Item_Data[17]
        self.Weapon_Range_IsThrow = self.Item_Data[18]
        self.Weapon_Damage_IsLoading = self.Item_Data[19]

        self.Properties_WeightClass = self.Item_Data[20]
        self.Properties_TwoHanded = self.Item_Data[21] == "x"
        self.Properties_Finesse = self.Item_Data[22] == "x"
        self.Properties_Versatile = self.Item_Data[23]
        self.Properties_Reach = self.Item_Data[24] == "x"

    def check_if_ranged(self):
        return self.Weapon_Range_Min > 0

    def get_details_as_text(self, chara) -> str:
        return (f'Damage: {self.Weapon_Damage} ({shared_data.get_attribute_modifier(chara.Attribute_Strength):+d}),'
                f' {self.Weapon_DamageType}, '
                f'\nRange: {self.Weapon_Range_Min}/{self.Weapon_Range_Max}, '
                f'{self.Weapon_Type}, {self.get_additional_info_as_text(chara)}')

    def get_additional_info_as_text(self, chara):
        properties = ""
        if self.Weapon_Range_IsThrow:
            properties += "Throwable"
        if self.Weapon_Damage_IsLoading:
            if properties != "":
                properties += ", "
            properties += "Loading"
        if self.Properties_WeightClass != None:
            if properties != "":
                properties += ", "
            properties += self.Properties_WeightClass.capitalize()
        if self.Properties_Reach:
            if properties != "":
                properties += ", "
            properties += "Reach"
        if self.Properties_Finesse:
            if properties != "":
                properties += ", "
            properties += "Finesse"
        if self.Properties_TwoHanded:
            if properties != "":
                properties += ", "
            properties += "2-Handed"
        if self.Properties_Versatile != "" and self.Properties_Versatile is not None:
            if properties != "":
                properties += ", "
            properties += f"Versatile {self.Properties_Versatile} ({shared_data.get_attribute_modifier(chara.Attribute_Dexterity):+d})"

        return properties


class ItemTable:
    _instance = None  # Class attribute to hold the single instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ItemTable, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        self.Item_Dictionary = {}
        self.refresh_list()

    def get_item_dictionary(self):
        return self.Item_Dictionary

    def refresh_list(self):
        self.Item_Dictionary = {}

        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        query = "SELECT id FROM items"
        cursor.execute(query)
        ids = cursor.fetchall()

        query = "SELECT type FROM items"
        cursor.execute(query)
        types = cursor.fetchall()

        connection.close()

        for i in range(len(ids)):
            self.Item_Dictionary.update({ids[i][0]: self.create_item_for_type(self, ids[i][0], types[i][0])})

    def get_list_of_item_with_part_string(self, part_sting: str) -> List[Item]:
        all_item_list: List[Item] = list(self.Item_Dictionary.values())
        final_item_list: List[Item] = [item for item in all_item_list
                                       if part_sting.lower() in item.Item_Name.lower()]
        return final_item_list

    def add_new_item_to_db(self, item_values: List[any]):
        new_id = [max(self.Item_Dictionary.keys()) + 1]

        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        all_values = new_id + item_values

        column_names = "id, name, type, baseValue, weight"

        if all_values[2] == "weapon":
            column_names = "id, name, type, baseValue, weight, wep_type, wep_dam_dice, wep_dam_type, wep_range_min, wep_range_max, wep_range_thrown, wep_range_loading, wep_prop_weightclass, wep_prop_twohands, wep_prop_finesse, wep_prop_versatile, wep_prop_reach"
        elif all_values[2] == "armor":
            column_names = "id, name, type, baseValue, weight, armor_type, armor_ac, armor_dexmod, armor_strength, armor_stealth"

        amount_of_items = len(column_names.split(","))
        question_mark_list = ""

        for i in range(amount_of_items):
            if i == 0:
                question_mark_list += "?"
            else:
                question_mark_list += ", ?"

        insert_query = f"""
                INSERT INTO items ({column_names})
                VALUES ({question_mark_list})
                """

        cursor.execute(insert_query, all_values)
        connection.commit()
        connection.close()

        self.refresh_list()

    @staticmethod
    def create_item_for_type(self, item_id, item_type):
        if item_type == "weapon":
            return Weapon(item_id)
        if item_type == "armor":
            return Armor(item_id)
        return Item(item_id)

    def get_item_from_id_in_table(self, item_id):
        item = self.Item_Dictionary[item_id]

        if item is not None:
            return item


item_database = ItemTable()
