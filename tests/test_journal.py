"""Run with python -m unittest discover -s tests -p test_journal.py."""
import os
import gc
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path


class JournalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.root = Path(__file__).resolve().parents[1]
        cls.old_cwd = Path.cwd()
        cls.temp = tempfile.TemporaryDirectory()
        shutil.copy2(cls.root / 'assets.db', Path(cls.temp.name) / 'assets.db')
        os.chdir(cls.temp.name)
        import app
        import DataManagers
        cls.web = app.website.app
        cls.web.config['TESTING'] = True
        cls.managers = DataManagers

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.old_cwd)
        gc.collect()
        cls.temp.cleanup()

    def setUp(self):
        self.db = str(Path(self.temp.name) / 'journal-test.db')
        with sqlite3.connect(self.db) as c:
            c.execute('CREATE TABLE IF NOT EXISTS character (id INTEGER PRIMARY KEY)')
            c.execute('INSERT OR IGNORE INTO character VALUES (1)')
            if c.execute("SELECT 1 FROM sqlite_master WHERE name='journalItems'").fetchone():
                c.execute('DELETE FROM journalItems')
                c.execute('DELETE FROM journalTopics')
        self.jm = self.managers.JournalManager(self.db)
        self.managers.jm_shared = self.jm
        self.client = self.web.test_client()
        with self.client.session_transaction() as s:
            s['user'] = 'test'
            s['chara_id'] = 1
        self.client.get('/journal')
        with self.client.session_transaction() as s:
            self.token = s['journal_token']

    def post(self, **data):
        return self.client.post('/journal', data={'token': self.token, **data})

    def test_manager_persistence_order_and_validation(self):
        first = self.jm.create_journal_topic('First')
        second = self.jm.create_journal_topic('Second')
        created = self.jm.Topics[-1].CreationDate
        self.jm.add_journal_item('Older topic updated', str(first), None)
        topics = self.managers.JournalManager(self.db).get_all_journals_by_topic()
        self.assertEqual([t.ID for t in topics], [first, second])
        self.assertEqual(topics[0].CreationDate, created)
        self.assertGreater(topics[0].ChangeDate, created)
        self.assertIsNone(topics[0].Items[0].CharaID)
        for text, topic in [('', first), ('x', 999), ('x', 'bad'), ('x' * 20001, first)]:
            with self.assertRaises(ValueError):
                self.jm.add_journal_item(text, topic)
        with self.assertRaises(ValueError):
            self.jm.create_journal_topic('   ')
        self.assertEqual(len(self.jm.get_all_journals_by_topic()[0].Items), 1)

    def test_web_create_expand_escape_and_attribution(self):
        self.assertEqual(self.post(action='topic', name='<script>topic</script>').status_code, 303)
        topic = self.jm.Topics[0].ID
        response = self.post(action='entry', topic_id=topic, text='<script>alert(1)</script>\nNext line', attribute='yes')
        self.assertEqual(response.status_code, 303)
        html = self.client.get(response.location).get_data(as_text=True)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
        self.assertNotIn('<script>alert(1)</script>', html)
        self.assertIn('<details open>', html)
        self.assertEqual(self.jm.Topics[0].Items[0].CharaID, 1)
        self.assertEqual(self.post(action='entry', topic_id=topic, text='No author').status_code, 303)
        self.assertIsNone(self.jm.Topics[0].Items[1].CharaID)
        self.assertEqual(self.client.get('/character').status_code, 200)

    def test_authentication_token_and_invalid_forms(self):
        anonymous = self.web.test_client()
        self.assertEqual(anonymous.get('/journal').status_code, 302)
        self.assertEqual(anonymous.post('/journal', data={'action': 'topic', 'name': 'No'}).status_code, 302)
        self.assertEqual(self.client.post('/journal', data={'action': 'topic', 'name': 'No'}).status_code, 400)
        self.assertEqual(self.post(action='topic', name=' ').status_code, 400)
        self.assertEqual(self.post(action='entry', topic_id='999', text='Missing').status_code, 400)
        self.assertEqual(self.post(action='unknown').status_code, 400)
        self.assertEqual(self.jm.get_all_journals_by_topic(), [])


if __name__ == '__main__':
    unittest.main()
