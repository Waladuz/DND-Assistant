CREATE TABLE IF NOT EXISTS mp_overrides (
    character_id INTEGER PRIMARY KEY REFERENCES character(id),
    level_1 INTEGER NOT NULL CHECK(level_1 >= 0),
    level_2 INTEGER NOT NULL CHECK(level_2 >= 0),
    level_3 INTEGER NOT NULL CHECK(level_3 >= 0),
    level_4 INTEGER NOT NULL CHECK(level_4 >= 0),
    level_5 INTEGER NOT NULL CHECK(level_5 >= 0),
    level_6 INTEGER NOT NULL CHECK(level_6 >= 0),
    level_7 INTEGER NOT NULL CHECK(level_7 >= 0),
    level_8 INTEGER NOT NULL CHECK(level_8 >= 0),
    level_9 INTEGER NOT NULL CHECK(level_9 >= 0)
);
