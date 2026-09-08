from character import Character, Enemy, JournalTopic, JournalItem
from datetime import datetime, timezone
from contextlib import closing
from pathlib import Path
from threading import RLock
import sqlite3
import copy


class CharacterManager:
    def __init__(self):
        self.Available_Characters = []
        self.Current_Pary = []

        self.Character_From_ID_Dictionary = {}

        self.refresh_available_character_list()

    def refresh_available_character_list(self):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM character")
        rows = cursor.fetchall()

        ids = [row[0] for row in rows]

        for chara_id in ids:
            if chara_id not in self.Character_From_ID_Dictionary:
                new_character = Character(chara_id)
                self.Character_From_ID_Dictionary[chara_id] = new_character

    def get_all_ids_from_available_characters(self):
        ids = []
        for key, value in self.Character_From_ID_Dictionary.items():
            ids.append(key)

        return ids

    def get_all_ids_and_player_names(self):
        names = []

        for key, value in self.Character_From_ID_Dictionary.items():
            names.append(value.Base_Name)

        return self.get_all_ids_from_available_characters(), names

    def get_dictionary(self):
        self.refresh_available_character_list()
        return self.Character_From_ID_Dictionary

    def delete_character_from_databank(self, character_id):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        sql_query = "DELETE FROM character WHERE id = ?"
        cursor.execute(sql_query, (character_id,))

        connection.commit()

        self.refresh_available_character_list()

        if cursor.rowcount == 0:
            return False
        else:
            return True

    def create_new_character_with_id(self):
        current_max_id = max(self.get_all_ids_from_available_characters())
        current_max_id += 1

        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        sql_query = """
                INSERT INTO character (id, 
                                        att_strength,
                                        att_dexterity,
                                        att_constitution,
                                        att_intelligence,
                                        att_wisdom,
                                        att_charisma,
                                        sk_acrobatics,
                                        sk_animal,
                                        sk_arcana,
                                        sk_athletics,
                                        sk_deception,
                                        sk_history,
                                        sk_insight,
                                        sk_intimidation,
                                        sk_investigation,
                                        sk_medicine,
                                        sk_nature,
                                        sk_perception,
                                        sk_performance,
                                        sk_persuasion,
                                        sk_religion,
                                        sk_sleight,
                                        sk_stealth,
                                        sk_survival
                                        )
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """

        cursor.execute(sql_query, (current_max_id,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1))
        connection.commit()

        return current_max_id


class EnemyManagement:
    def __init__(self):
        self.id_to_enemy_dictionary = {}
        self.create_enemy_from_database()

    def get_ids_of_all_enemies_in_db(self):
        self.create_enemy_from_database()

        return list(self.id_to_enemy_dictionary.keys())

    def create_new_enemy_with_id(self):
        current_max_id = int(max(self.get_ids_of_all_enemies_in_db()))
        current_max_id += 1

        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        sql_query = """
                INSERT INTO enemies (enemy_id)
                VALUES (?)
                """

        cursor.execute(sql_query, (current_max_id,))
        connection.commit()

        return current_max_id

    def get_ids_and_names_as_string(self):
        self.create_enemy_from_database()
        ids_and_names = []

        for enemy_id, enemy in self.id_to_enemy_dictionary.items():
            ids_and_names.append(f"{enemy_id} - {enemy.Enemy_Name}")

        return ids_and_names

    def create_enemy_from_database(self):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()
        cursor.execute("SELECT enemy_id FROM enemies")
        rows = cursor.fetchall()

        ids = [row[0] for row in rows]

        for enemy_id in ids:
            if enemy_id not in self.id_to_enemy_dictionary:
                new_enemy = Enemy(enemy_id)
                self.id_to_enemy_dictionary[int(enemy_id)] = new_enemy

        dict(sorted(self.id_to_enemy_dictionary.items()))


class MapManager:
    def __init__(self):
        self.id_to_map_dict = {}
        self.reload_all_maps_from_db()

    def reload_all_maps_from_db(self):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM maps")
        rows = cursor.fetchall()

        self.id_to_map_dict = {}

        for row in rows:
            new_map = Map(row)
            new_map.get_enemies_to_map_from_db()
            new_map.get_loot_to_map_from_db()
            self.id_to_map_dict[new_map.ID] = new_map

    def delete_map(self, map_id):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        sql_query = "DELETE FROM maps WHERE map_id = ?"
        cursor.execute(sql_query, (map_id,))

        connection.commit()

        self.reload_all_maps_from_db()


class Map:
    def __init__(self, values):
        self.ID = values[0]
        self.image_name = values[1]

        self.map_name = values[2]

        self.grid_interval = int(values[3])
        self.enemy_list = []
        self.loot_list = []
        self.money_loot = int(values[4])

    def get_enemies_to_map_from_db(self):
        self.enemy_list = []
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()
        sql_query = "SELECT * FROM map_enemies WHERE map_id = ?"
        cursor.execute(sql_query, (self.ID,))
        print(cursor.fetchall())
        for row in cursor.fetchall():
            creature = copy.copy(em_shared.id_to_enemy_dictionary[int(row[1])])
            creature.Temp_ID = row[2]
            creature.Temp_CharaName = row[3]
            creature.Temp_HP_Max = row[4]
            print(creature.Temp_CharaName)
            self.enemy_list.append(creature)

    def get_loot_to_map_from_db(self):
        self.loot_list = []
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()
        sql_query = "SELECT * FROM map_loot WHERE map_id = ?"
        cursor.execute(sql_query, (self.ID,))
        for row in cursor.fetchall():
            self.loot_list.append(row[1])

    def set_enemy_list(self, new_list):
        self.enemy_list = new_list

    def save_to_db(self):
        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        # Step 1: Delete all inventory items for the given character ID
        delete_query = "DELETE FROM maps WHERE map_id = ?"
        cursor.execute(delete_query, (self.ID,))

        delete_query = "DELETE FROM map_enemies WHERE map_id = ?"
        cursor.execute(delete_query, (self.ID,))

        delete_query = "DELETE FROM map_loot WHERE map_id = ?"
        cursor.execute(delete_query, (self.ID,))

        insert_query = """
                        INSERT INTO maps (map_id, image_name, map_name, grid_interval, map_money_loot)
                        VALUES (?, ?, ?, ?, ?)
                        """

        cursor.execute(insert_query, (self.ID, self.image_name, self.map_name, self.grid_interval, self.money_loot))

        for enemy in self.enemy_list:
            insert_query = """
                                INSERT INTO map_enemies (map_id, creature_id, ind_id, ind_name, hp)
                                VALUES (?, ?, ?, ?, ?)
                                """
            cursor.execute(insert_query, (self.ID, enemy.ID, enemy.Temp_ID, enemy.Temp_CharaName,
                                          enemy.Temp_HP_Max))

        for loot in self.loot_list:
            insert_query = """
                                            INSERT INTO map_loot (map_id, item_id)
                                            VALUES (?, ?)
                                            """
            cursor.execute(insert_query, (self.ID, loot))

        connection.commit()


class JournalManager:
    """SQLite-backed shared campaign journal, newest changed topics first."""
    def __init__(self, db_path='assets.db'):
        self.db_path = db_path
        self.Topics = []
        self._lock = RLock()
        migration = Path(__file__).parent / 'migrations' / '002_journal.sql'
        with closing(sqlite3.connect(self.db_path)) as connection:
            connection.executescript(migration.read_text(encoding='utf-8'))
        self.get_all_journals_by_topic()

    @staticmethod
    def _now():
        return datetime.now(timezone.utc).isoformat(timespec='microseconds')

    def get_all_journals_by_topic(self):
        """Return topics by ChangeDate descending, with entries oldest first."""
        with self._lock, closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute('BEGIN')
                topics = [JournalTopic(*row) for row in connection.execute(
                    'SELECT ID, Name, CreationDate, ChangeDate FROM journalTopics '
                    'ORDER BY ChangeDate DESC, ID DESC')]
                by_id = {topic.ID: topic for topic in topics}
                for row in connection.execute(
                    'SELECT ID, Text, CreationDate, CharaID, journalTopicID FROM journalItems '
                    'ORDER BY CreationDate, ID'):
                    by_id[row[4]].Items.append(JournalItem(*row))
            self.Topics = topics
            return topics

    def create_journal_topic(self, name: str):
        if not isinstance(name, str) or not name.strip() or len(name.strip()) > 200:
            raise ValueError('Enter a topic name between 1 and 200 characters.')
        now = self._now()
        with self._lock, closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                cursor = connection.execute(
                    'INSERT INTO journalTopics (Name, CreationDate, ChangeDate) VALUES (?, ?, ?)',
                    (name.strip(), now, now))
                topic_id = cursor.lastrowid
            self.get_all_journals_by_topic()
        return topic_id

    def add_journal_item(self, text: str, journalTopicID: str, chara: Character = None):
        if not isinstance(text, str) or not text.strip() or len(text) > 20000:
            raise ValueError('Enter an entry between 1 and 20000 characters.')
        try:
            topic_id = int(journalTopicID)
        except (ValueError, TypeError):
            raise ValueError('Choose a valid journal topic.') from None
        chara_id = chara.ID if chara is not None else None
        with self._lock, closing(sqlite3.connect(self.db_path)) as connection:
            with connection:
                connection.execute('BEGIN IMMEDIATE')
                if not connection.execute('SELECT 1 FROM journalTopics WHERE ID=?', (topic_id,)).fetchone():
                    raise ValueError('Journal topic does not exist.')
                if chara_id is not None and not connection.execute(
                        'SELECT 1 FROM character WHERE id=?', (chara_id,)).fetchone():
                    raise ValueError('Character does not exist.')
                now = self._now()
                cursor = connection.execute(
                    'INSERT INTO journalItems (Text, CreationDate, CharaID, journalTopicID) '
                    'VALUES (?, ?, ?, ?)', (text.strip(), now, chara_id, topic_id))
                item_id = cursor.lastrowid
                connection.execute('UPDATE journalTopics SET ChangeDate=? WHERE ID=?', (now, topic_id))
            self.get_all_journals_by_topic()
        return item_id


cm_shared = CharacterManager()
em_shared = EnemyManagement()
mm_shared = MapManager()

jm_shared = JournalManager()
