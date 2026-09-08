-- Additive and safe to run on an existing database or rerun at startup.
BEGIN IMMEDIATE;
CREATE TABLE IF NOT EXISTS journalTopics (
    ID INTEGER PRIMARY KEY,
    Name TEXT NOT NULL CHECK(length(trim(Name)) BETWEEN 1 AND 200),
    CreationDate TEXT NOT NULL,
    ChangeDate TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS journalItems (
    ID INTEGER PRIMARY KEY,
    Text TEXT NOT NULL CHECK(length(trim(Text)) BETWEEN 1 AND 20000),
    CreationDate TEXT NOT NULL,
    CharaID INTEGER REFERENCES character(id),
    journalTopicID INTEGER NOT NULL REFERENCES journalTopics(ID)
);
CREATE INDEX IF NOT EXISTS journalItems_topic_date ON journalItems(journalTopicID, CreationDate, ID);
CREATE INDEX IF NOT EXISTS journalTopics_changed ON journalTopics(ChangeDate DESC, ID DESC);
COMMIT;
