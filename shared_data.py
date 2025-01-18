import sqlite3
from tkinter import ttk
from typing import List

#########
# Databank Reference Dictionaries
#########

DATABANK_BASE = {
    "ID": "id",
    "Name": "base_name",
    "Race": "base_race",
    "Class": "base_class",
    "Level": "base_lvl",
    "Exp": "base_exp",
    "Alignment": "base_allignment",
    "PlayerName": "player",
    "Max HP": "hp_max",
    "Initiative": "base_initiative",
    "Speed": "base_speed",
    "AC": "base_ac",
    "Money": "money"
}

DATABANK_ATTRIBUTES = {
    "Strength": "att_strength",
    "Dexterity": "att_dexterity",
    "Constitution": "att_constitution",
    "Intelligence": "att_intelligence",
    "Wisdom": "att_wisdom",
    "Charisma": "att_charisma"
}

DATABANK_SKILLS = {
    "Acrobatics": "sk_acrobatics",
    "AnimalHandling": "sk_animal",
    "Arcana": "sk_arcana",
    "Athletics": "sk_athletics",
    "Deception": "sk_deception",
    "History": "sk_history",
    "Insight": "sk_insight",
    "Intimidation": "sk_intimidation",
    "Investigation": "sk_investigation",
    "Medicine": "sk_medicine",
    "Nature": "sk_nature",
    "Perception": "sk_perception",
    "Performance": "sk_performance",
    "Persuasion": "sk_persuasion",
    "Religion": "sk_religion",
    "SleightOfHand": "sk_sleight",
    "Stealth": "sk_stealth",
    "Survival": "sk_survival"
}

SKILLS_BARBARIAN_SKILLNAME = {
    1: "Rage, Unarmored Defense",
    2: "Reckless Attack, Danger Sense",
    3: "Primal Path",
    4: "Ability Score Improvement",
    5: "Extra Attack, Fast Movement⁠",
    6: "Path feature",
    7: "Feral Instinct",
    8: "Ability Score Improvement",
    9: "Brutal Critical (1 die)",
    10: "Path feature",
    11: "Relentless⁠ Rage",
    12: "Ability Score Improvement",
    13: "Brutal Critical (2 dice)",
    14: "Path feature",
    15: "Persistent Rage",
    16: "Ability Score Improvement",
    17: "Brutal Critical (3 dice)",
    18: "Indomitable Might",
    19: "Ability Score Improvement",
    20: "Primal Champion⁠"
}

SKILLS_BARD_SKILLNAME = {
    1: "Spellcasting, Bardic Inspiration (d6)",
    2: "Jack of All Trades, Song of Rest (d6)",
    3: "Bard College, Expertise",
    4: "Ability Score Improvement",
    5: "Bardic Inspiration (d8), Font of Inspiration",
    6: "Countercharm, Bard College feature",
    7: "-",
    8: "Ability Score Improvement",
    9: "Song of Rest (d8)",
    10: "Bardic Inspiration (d10), Expertise, Magical Secrets",
    11: "-",
    12: "Ability Score Improvement",
    13: "Song of Rest (d10)",
    14: "Magical Secrets, Bard College feature",
    15: "Bardic Inspiration (d12)",
    16: "Ability Score Improvement",
    17: "Song of Rest (d12)",
    18: "Magical Secrets",
    19: "Ability Score Improvement",
    20: "Superior Inspiration"
}

SKILLS_CLERIC_SKILLNAME = {
    1: "Spellcasting, Divine Domain",
    2: "Channel Divinity (1/rest), Divine Domain feature",
    3: "-",
    4: "Ability Score Improvement",
    5: "Destroy Undead (CR 1/2)",
    6: "Channel Divinity (2/rest), Divine Domain feature",
    7: "-",
    8: "Ability Score Improvement, Destroy Undead (CR 1), Divine Domain feature",
    9: "-",
    10: "Divine Intervention",
    11: "Destroy Undead (CR 2)",
    12: "Ability Score Improvement",
    13: "-",
    14: "Destroy Undead (CR 3)",
    15: "-",
    16: "Ability Score Improvement",
    17: "Destroy Undead (CR 4), Divine Domain feature",
    18: "Channel Divinity (3/rest)",
    19: "Ability Score Improvement",
    20: "Divine Intervention improvement"
}

SKILLS_DRUID_SKILLNAME = {
    1: "Druidic, Spellcasting",
    2: "Wild Shape, Druid Circle",
    3: "-",
    4: "Wild Shape improvement, Ability Score Improvement",
    5: "-",
    6: "Druid Circle feature",
    7: "-",
    8: "Wild Shape improvement, Ability Score Improvement",
    9: "-",
    10: "Druid Circle feature",
    11: "-",
    12: "Ability Score Improvement",
    13: "-",
    14: "Druid Circle feature",
    15: "-",
    16: "Ability Score Improvement",
    17: "-",
    18: "Timeless Body, Beast Spells",
    19: "Ability Score Improvement",
    20: "Archdruid"
}

SKILLS_FIGHTER_SKILLNAME = {
    1: "Fighting Style, Second Wind",
    2: "Action Surge (one use)",
    3: "Martial Archetype",
    4: "Ability Score Improvement",
    5: "Extra Attack",
    6: "Ability Score Improvement",
    7: "Martial Archetype feature",
    8: "Ability Score Improvement",
    9: "Indomitable (one use)",
    10: "Martial Archetype feature",
    11: "Extra Attack (2)",
    12: "Ability Score Improvement",
    13: "Indomitable (two uses)",
    14: "Ability Score Improvement",
    15: "Martial Archetype feature",
    16: "Ability Score Improvement",
    17: "Action Surge (two uses), Indomitable (three uses)",
    18: "Martial Archetype feature",
    19: "Ability Score Improvement",
    20: "Extra Attack (3)"
}

SKILLS_MONK_SKILLNAME = {
    1: "Unarmored Defense, Martial Arts",
    2: "Ki, Unarmored Movement",
    3: "Monastic Tradition, Deflect Missiles",
    4: "Ability Score Improvement, Slow Fall",
    5: "Extra Attack, Stunning Strike",
    6: "Ki-Empowered Strikes, Monastic Tradition feature",
    7: "Evasion, Stillness of Mind",
    8: "Ability Score Improvement",
    9: "Unarmored Movement improvement",
    10: "Purity of Body",
    11: "Monastic Tradition feature",
    12: "Ability Score Improvement",
    13: "Tongue of the Sun and Moon",
    14: "Diamond Soul",
    15: "Timeless Body",
    16: "Ability Score Improvement",
    17: "Monastic Tradition feature",
    18: "Empty Body",
    19: "Ability Score Improvement",
    20: "Perfect Self"
}

SKILLS_PALADIN_SKILLNAME = {
    1: "Divine Sense, Lay on Hands",
    2: "Fighting Style, Spellcasting, Divine Smite",
    3: "Divine Health, Sacred Oath",
    4: "Ability Score Improvement",
    5: "Extra Attack",
    6: "Aura of Protection",
    7: "Sacred Oath feature",
    8: "Ability Score Improvement",
    9: "-",
    10: "Aura of Courage",
    11: "Improved Divine Smite",
    12: "Ability Score Improvement",
    13: "-",
    14: "Cleansing Touch",
    15: "Sacred Oath feature",
    16: "Ability Score Improvement",
    17: "-",
    18: "Aura improvements",
    19: "Ability Score Improvement",
    20: "Sacred Oath feature"
}

SKILLS_RANGER_SKILLNAME = {
    1: "Favored Enemy, Natural Explorer",
    2: "Fighting Style, Spellcasting",
    3: "Ranger Archetype, Primeval Awareness",
    4: "Ability Score Improvement",
    5: "Extra Attack",
    6: "Favored Enemy and Natural Explorer improvements",
    7: "Ranger Archetype feature",
    8: "Ability Score Improvement, Land’s Stride",
    9: "-",
    10: "Natural Explorer improvement, Hide in Plain Sight",
    11: "Ranger Archetype feature",
    12: "Ability Score Improvement",
    13: "-",
    14: "Favored Enemy improvement, Vanish",
    15: "Ranger Archetype feature",
    16: "Ability Score Improvement",
    17: "-",
    18: "Feral Senses",
    19: "Ability Score Improvement",
    20: "Foe Slayer"
}

SKILLS_ROUGE_SKILLNAME = {
    1: "Expertise, Sneak Attack, Thieves’ Cant",
    2: "Cunning Action",
    3: "Roguish Archetype",
    4: "Ability Score Improvement",
    5: "Uncanny Dodge",
    6: "Expertise",
    7: "Evasion",
    8: "Ability Score Improvement",
    9: "Roguish Archetype feature",
    10: "Ability Score Improvement",
    11: "Reliable Talent",
    12: "Ability Score Improvement",
    13: "Roguish Archetype feature",
    14: "Blindsense",
    15: "Slippery Mind",
    16: "Ability Score Improvement",
    17: "Roguish Archetype feature",
    18: "Elusive",
    19: "Ability Score Improvement",
    20: "Stroke of Luck"
}

SKILLS_SORCERER_SKILLNAME = {
    1: "Spellcasting, Sorcerous Origin",
    2: "Font of Magic",
    3: "Metamagic",
    4: "Ability Score Improvement",
    5: "-",
    6: "Sorcerous Origin feature",
    7: "-",
    8: "Ability Score Improvement",
    9: "-",
    10: "Metamagic",
    11: "-",
    12: "Ability Score Improvement",
    13: "-",
    14: "Sorcerous Origin feature",
    15: "-",
    16: "Ability Score Improvement",
    17: "Metamagic",
    18: "Sorcerous Origin feature",
    19: "Ability Score Improvement",
    20: "Sorcerous Restoration"
}

SKILLS_WARLOCK_SKILLNAME = {
    1: "Otherworldly Patron, Pact Magic",
    2: "Eldritch Invocations",
    3: "Pact Boon",
    4: "Ability Score Improvement",
    5: "-",
    6: "Otherworldly Patron feature",
    7: "-",
    8: "Ability Score Improvement",
    9: "-",
    10: "Otherworldly Patron feature",
    11: "Mystic Arcanum (6th level)",
    12: "Ability Score Improvement",
    13: "Mystic Arcanum (7th level)",
    14: "Otherworldly Patron feature",
    15: "Mystic Arcanum (8th level)",
    16: "Ability Score Improvement",
    17: "Mystic Arcanum (9th level)",
    18: "-",
    19: "Ability Score Improvement",
    20: "Eldritch Master"
}

SKILLS_WIZARD_SKILLNAME = {
    1: "Spellcasting, Arcane Recovery",
    2: "Arcane Tradition",
    3: "-",
    4: "Ability Score Improvement",
    5: "-",
    6: "Arcane Tradition feature",
    7: "-",
    8: "Ability Score Improvement",
    9: "-",
    10: "Arcane Tradition feature",
    11: "-",
    12: "Ability Score Improvement",
    13: "-",
    14: "Arcane Tradition feature",
    15: "-",
    16: "Ability Score Improvement",
    17: "-",
    18: "Spell Mastery",
    19: "Ability Score Improvement",
    20: "Signature Spell"
}

SKILLS_CLASS_TO_BONUSES = {
    "Barbarian": SKILLS_BARBARIAN_SKILLNAME,
    "Bard": SKILLS_BARD_SKILLNAME,
    "Cleric": SKILLS_CLERIC_SKILLNAME,
    "Druid": SKILLS_DRUID_SKILLNAME,
    "Fighter": SKILLS_FIGHTER_SKILLNAME,
    "Monk": SKILLS_MONK_SKILLNAME,
    "Paladin": SKILLS_PALADIN_SKILLNAME,
    "Ranger": SKILLS_RANGER_SKILLNAME,
    "Rogue": SKILLS_ROUGE_SKILLNAME,
    "Sorcerer": SKILLS_SORCERER_SKILLNAME,
    "Warlock": SKILLS_WARLOCK_SKILLNAME,
    "Wizard": SKILLS_WIZARD_SKILLNAME
}

MP_BARD = {
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
}

MP_CLERIC = {
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
}

MP_DRUID = {
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
}

MP_MONK = {
    1: [0, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    4: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    6: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    8: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    9: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    10: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    11: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    12: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    13: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    14: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    15: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    16: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    17: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    18: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    19: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    20: [4, 3, 3, 3, 2, 0, 0, 0, 0]
}

MP_PALADIN = {
    1: [0, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    4: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    6: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    8: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    9: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    10: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    11: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    12: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    13: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    14: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    15: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    16: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    17: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    18: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    19: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    20: [4, 3, 3, 3, 2, 0, 0, 0, 0]
}

MP_RANGER = {
    1: [0, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    4: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    6: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    8: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    9: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    10: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    11: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    12: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    13: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    14: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    15: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    16: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    17: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    18: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    19: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    20: [4, 3, 3, 3, 2, 0, 0, 0, 0]
}

MP_SORCERER = {
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
}

MP_WIZARD = {
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    6: [4, 3, 3, 0, 0, 0, 0, 0, 0],
    7: [4, 3, 3, 1, 0, 0, 0, 0, 0],
    8: [4, 3, 3, 2, 0, 0, 0, 0, 0],
    9: [4, 3, 3, 3, 1, 0, 0, 0, 0],
    10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
    11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
    13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
    15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
    17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
    18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
    19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
    20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
}

MP_BY_CLASS = {
    "Bard": MP_BARD,
    "Cleric": MP_CLERIC,
    "Druid": MP_DRUID,
    "Monk": MP_MONK,
    "Paladin": MP_PALADIN,
    "Ranger": MP_RANGER,
    "Sorcerer": MP_SORCERER,
    "Wizard": MP_WIZARD
}


def get_attribute_modifier(attribute):
    return (int(attribute) - 10) // 2


class MagicTable:
    def __init__(self):
        self.id_magic_dictionary = {}
        self.load_magic_info()

    def load_magic_info(self):
        self.id_magic_dictionary = {}

        connection = sqlite3.connect('assets.db')
        cursor = connection.cursor()

        query = "SELECT * FROM spells"
        cursor.execute(query)
        results = cursor.fetchall()  # Fetch one result
        connection.close()

        for i in results:
            self.id_magic_dictionary[i[0]] = Spell(i)


class Spell:
    def __init__(self, values):
        self.Magic_ID = values[0]
        self.Magic_Name = values[1]
        self.Magic_Level = int(values[2])
        self.Magic_School = values[3]

        self.Magic_Casting_Time = values[4]
        self.Magic_Duration = values[5]

        self.Magic_Range = values[6]
        self.Magic_Area = values[7]
        self.Magic_Attack = values[8]
        self.Magic_Save = values[9]
        self.Magic_Damage_Type = values[10]

        self.Magic_Ritual = values[11]
        self.Magic_Concentration = values[12]
        self.Magic_VSM = values[13]  # Useless
        self.Magic_Verbose = values[14]
        self.Magic_Somatic = values[15]
        self.Magic_Material = values[16]
        self.Magic_Material_Info = values[17]
        self.Magic_Detail = values[18]

    def get_saving_throw_type(self):
        if self.Magic_Save is None:
            return None

        first_three_letters = self.Magic_Save[:3]

        if first_three_letters == "WIS":
            return "Wisdom"
        if first_three_letters == "STR":
            return "Strength"
        if first_three_letters == "INT":
            return "Intelligence"
        if first_three_letters == "DEX":
            return "Dexterity"
        if first_three_letters == "CON":
            return "Constitution"
        if first_three_letters == "CHA":
            return "Charisma"

        return None

def ui_add_label_entry(labelframe: ttk.LabelFrame, label_name: str, row_pos: int, column_pos: int,
                       width: int) -> ttk.Entry:
    label = ttk.Label(labelframe, text=f"{label_name}")
    label.grid(row=row_pos, column=column_pos, padx=0, pady=0, sticky="nsew")
    entry_field = ttk.Entry(labelframe, width=width)
    entry_field.grid(row=row_pos, column=column_pos + 1, padx=0, pady=0, sticky="nsew")

    return entry_field

def ui_add_label_combobox(labelframe: ttk.LabelFrame, label_name: str, selection_list: List[str], row_pos: int,
                          column_pos: int, width: int) -> ttk.Combobox:
    label = ttk.Label(labelframe, text=f"{label_name}")
    label.grid(row=row_pos, column=column_pos, padx=0, pady=0, sticky="nsew")
    entry_field = ttk.Combobox(labelframe, width=width, values=selection_list, state="readonly")
    entry_field.grid(row=row_pos, column=column_pos + 1, padx=0, pady=0, sticky="nsew")

    return entry_field

def ui_add_label_checkbox(labelframe: ttk.LabelFrame, label_name: str, selection_list: List[str], row_pos: int,
                          column_pos: int, width: int) -> ttk.Checkbutton:
    label = ttk.Label(labelframe, text=f"{label_name}")
    label.grid(row=row_pos, column=column_pos, padx=0, pady=0, sticky="nsew")
    entry_field = ttk.Combobox(labelframe, width=width, values=selection_list, state="readonly")
    entry_field.grid(row=row_pos, column=column_pos + 1, padx=0, pady=0, sticky="nsew")

    return entry_field


magic_table = MagicTable()
