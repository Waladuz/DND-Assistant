import gc
import os
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path
from character import Character


class MPOverrideTests(unittest.TestCase):
    def setUp(self):
        self.old_cwd = Path.cwd()
        self.temp = tempfile.TemporaryDirectory()
        shutil.copy2(self.old_cwd / 'assets.db', Path(self.temp.name) / 'assets.db')
        os.chdir(self.temp.name)
        self.chara = Character(1)
        self.chara.delete_mp_override()
        self.chara.set_magic_points()

    def tearDown(self):
        os.chdir(self.old_cwd)
        gc.collect()
        self.temp.cleanup()

    def test_override_persistence_limits_and_delete(self):
        defaults = self.chara.get_max_magic_points()
        values = [6, 5, 4, 3, 2, 1, 0, 0, 0]
        self.chara.create_mp_override(values)
        loaded = Character(1)
        self.assertEqual(loaded.get_mp_override(), values)
        self.assertEqual(list(loaded.Max_Magic_Points.values()), values)
        loaded.change_magic_points(1, -2)
        self.assertEqual(loaded.Magic_Points[1], 4)
        loaded.refresh_magic_point_limits()
        self.assertEqual(loaded.Magic_Points[1], 4)
        loaded.create_mp_override([1] * 9)
        self.assertEqual(loaded.Magic_Points[1], 1)
        loaded.change_magic_points(1, 100)
        self.assertEqual(loaded.Magic_Points[1], 1)
        loaded.change_magic_points(1, -100)
        self.assertEqual(loaded.Magic_Points[1], 0)
        loaded.delete_mp_override()
        self.assertIsNone(loaded.get_mp_override())
        self.assertEqual(loaded.get_max_magic_points(), defaults)
        self.assertEqual(loaded.Magic_Points[1], 0)
        loaded.set_magic_points()
        self.assertEqual(list(loaded.Magic_Points.values()), defaults)

    def test_validation_and_non_caster(self):
        for values in ([1], [-1] * 9, [1.5] * 9, [True] * 9):
            with self.assertRaises(ValueError): self.chara.create_mp_override(values)
        self.assertIsNone(self.chara.get_mp_override())
        self.chara.Base_Class = 'Non-caster'
        self.assertEqual(self.chara.get_max_magic_points(), [0] * 9)
        self.chara.create_mp_override([2] * 9)
        self.chara.set_magic_points()
        self.assertEqual(list(self.chara.Magic_Points.values()), [2] * 9)
        self.chara.change_magic_points(20, 1)
        self.chara.delete_mp_override()
        self.assertEqual(list(self.chara.Max_Magic_Points.values()), [0] * 9)
        self.assertIsNone(Character(2).get_mp_override())

    def test_website_uses_override(self):
        import app
        import DataManagers
        import queue
        DataManagers.cm_shared.Character_From_ID_Dictionary[1] = self.chara
        self.chara.create_mp_override([3] * 9)
        self.chara.set_magic_points()
        app.website.event_queue = queue.Queue()
        client = app.website.app.test_client()
        with client.session_transaction() as session:
            session['user'] = 'test'
            session['chara_id'] = 1
        response = client.post('/magic')
        self.assertEqual(response.status_code, 200)
        self.assertIn('🟢🟢🟢', response.get_data(as_text=True))
        response = client.post('/change_mp', json={'level': 1, 'amount': -1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.chara.Magic_Points[1], 2)
        self.assertIn('⚫', response.json['new_value'])


if __name__ == '__main__': unittest.main()
