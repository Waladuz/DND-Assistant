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
    1: {
        "name": "Rage, Unarmored Defense",
        "description": "Rage grants bonus damage and resistance while raging. Unarmored Defense gives AC equal to 10 + Dex mod + Con mod when not wearing armor."
    },
    2: {
        "name": "Reckless Attack, Danger Sense",
        "description": "Reckless Attack allows attacking with advantage but gives enemies advantage on attacks against you. Danger Sense grants advantage on Dex saves against visible effects."
    },
    3: {
        "name": "Primal Path",
        "description": "Choose a Barbarian subclass (e.g., Berserker, Totem Warrior), granting unique abilities."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "Extra Attack, Fast Movement",
        "description": "Attack twice per turn instead of once. Your movement speed increases by 10 feet when not wearing heavy armor."
    },
    6: {
        "name": "Path Feature",
        "description": "Gain a new ability from your Primal Path subclass."
    },
    7: {
        "name": "Feral Instinct",
        "description": "Gain advantage on initiative rolls. If surprised, you can act normally if you enter rage first."
    },
    8: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "Brutal Critical (1 die)",
        "description": "When you crit, roll one extra weapon damage die for extra damage."
    },
    10: {
        "name": "Path Feature",
        "description": "Gain a new ability from your Primal Path subclass."
    },
    11: {
        "name": "Relentless Rage",
        "description": "If reduced to 0 HP while raging, make a DC 10 Con save to drop to 1 HP instead. The DC increases with each use."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "Brutal Critical (2 dice)",
        "description": "When you crit, roll two extra weapon damage dice for extra damage."
    },
    14: {
        "name": "Path Feature",
        "description": "Gain a new ability from your Primal Path subclass."
    },
    15: {
        "name": "Persistent Rage",
        "description": "Your rage now only ends if you fall unconscious or choose to end it."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "Brutal Critical (3 dice)",
        "description": "When you crit, roll three extra weapon damage dice for extra damage."
    },
    18: {
        "name": "Indomitable Might",
        "description": "If your Strength check roll is lower than your Strength score, you can use your Strength score instead."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Primal Champion",
        "description": "Your Strength and Constitution scores increase by 4 (max 24)."
    }
}

SKILLS_BARD_SKILLNAME = SKILLS_BARD = {
    1: {
        "name": "Spellcasting, Bardic Inspiration (d6)",
        "description": "You gain the ability to cast bard spells. Bardic Inspiration allows you to grant an ally a d6 that they can add to an ability check, attack roll, or saving throw."
    },
    2: {
        "name": "Jack of All Trades, Song of Rest (d6)",
        "description": "Jack of All Trades lets you add half your proficiency bonus to ability checks you're not proficient in. Song of Rest allows allies to regain extra hit points (d6) when they heal during a short rest."
    },
    3: {
        "name": "Bard College, Expertise",
        "description": "Choose a Bard College, gaining unique features. Expertise lets you double proficiency in two chosen skills."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "Bardic Inspiration (d8), Font of Inspiration",
        "description": "Bardic Inspiration die increases to d8. Font of Inspiration lets you regain all Bardic Inspiration uses after a short or long rest."
    },
    6: {
        "name": "Countercharm, Bard College Feature",
        "description": "Countercharm grants allies advantage on saving throws against being frightened or charmed while you perform."
    },
    7: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    8: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "Song of Rest (d8)",
        "description": "Song of Rest die increases to d8, granting additional healing during short rests."
    },
    10: {
        "name": "Bardic Inspiration (d10), Expertise, Magical Secrets",
        "description": "Bardic Inspiration die increases to d10. Gain two more Expertise skills. Magical Secrets allows you to learn two spells from any class."
    },
    11: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "Song of Rest (d10)",
        "description": "Song of Rest die increases to d10, granting additional healing during short rests."
    },
    14: {
        "name": "Magical Secrets, Bard College Feature",
        "description": "Learn two more spells from any class. Gain another feature from your Bard College."
    },
    15: {
        "name": "Bardic Inspiration (d12)",
        "description": "Bardic Inspiration die increases to d12."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "Song of Rest (d12)",
        "description": "Song of Rest die increases to d12, granting additional healing during short rests."
    },
    18: {
        "name": "Magical Secrets",
        "description": "Learn two more spells from any class."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Superior Inspiration",
        "description": "If you have no Bardic Inspiration dice when you roll initiative, you regain one."
    }
}


SKILLS_CLERIC_SKILLNAME = {
    1: {
        "name": "Spellcasting, Divine Domain",
        "description": "You gain the ability to cast cleric spells. Choose a Divine Domain, which grants unique features and spells."
    },
    2: {
        "name": "Channel Divinity (1/rest), Divine Domain Feature",
        "description": "Channel Divinity allows you to use divine power for special effects. Gain a feature from your Divine Domain."
    },
    3: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "Destroy Undead (CR 1/2)",
        "description": "When you use Turn Undead, undead of CR 1/2 or lower are instantly destroyed if they fail their save."
    },
    6: {
        "name": "Channel Divinity (2/rest), Divine Domain Feature",
        "description": "You can now use Channel Divinity twice per rest. Gain another feature from your Divine Domain."
    },
    7: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    8: {
        "name": "Ability Score Improvement, Destroy Undead (CR 1), Divine Domain Feature",
        "description": "Increase one ability score by 2, or two ability scores by 1. Turn Undead now destroys undead of CR 1 or lower. Gain a new feature from your Divine Domain."
    },
    9: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    10: {
        "name": "Divine Intervention",
        "description": "You can call upon your deity for aid. Roll percentile dice, and if you roll under your cleric level, the deity intervenes."
    },
    11: {
        "name": "Destroy Undead (CR 2)",
        "description": "Turn Undead now destroys undead of CR 2 or lower."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    14: {
        "name": "Destroy Undead (CR 3)",
        "description": "Turn Undead now destroys undead of CR 3 or lower."
    },
    15: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "Destroy Undead (CR 4), Divine Domain Feature",
        "description": "Turn Undead now destroys undead of CR 4 or lower. Gain a new feature from your Divine Domain."
    },
    18: {
        "name": "Channel Divinity (3/rest)",
        "description": "You can now use Channel Divinity three times per rest."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Divine Intervention Improvement",
        "description": "If you fail your Divine Intervention roll, you automatically succeed once per week."
    }
}

SKILLS_DRUID_SKILLNAME = {
    1: {
        "name": "Druidic, Spellcasting",
        "description": "You learn Druidic, the secret language of druids. You also gain the ability to cast druid spells."
    },
    2: {
        "name": "Wild Shape, Druid Circle",
        "description": "Wild Shape allows you to transform into a beast you’ve seen before. Choose a Druid Circle, which grants unique abilities."
    },
    3: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    4: {
        "name": "Wild Shape Improvement, Ability Score Improvement",
        "description": "You can now use Wild Shape twice per rest. Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    6: {
        "name": "Druid Circle Feature",
        "description": "Gain a new ability from your chosen Druid Circle."
    },
    7: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    8: {
        "name": "Wild Shape Improvement, Ability Score Improvement",
        "description": "Your Wild Shape improves, allowing stronger transformations. Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    10: {
        "name": "Druid Circle Feature",
        "description": "Gain a new ability from your chosen Druid Circle."
    },
    11: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    14: {
        "name": "Druid Circle Feature",
        "description": "Gain a new ability from your chosen Druid Circle."
    },
    15: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    18: {
        "name": "Timeless Body, Beast Spells",
        "description": "Timeless Body makes you age much slower. Beast Spells allow you to cast druid spells while in Wild Shape."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Archdruid",
        "description": "You can use Wild Shape an unlimited number of times. You also ignore verbal, somatic, and material components of spells without cost."
    }
}

SKILLS_FIGHTER_SKILLNAME = {
    1: {
        "name": "Fighting Style, Second Wind",
        "description": "Choose a Fighting Style that enhances combat abilities (e.g., Archery, Defense, Great Weapon Fighting). Second Wind allows you to regain 1d10 + fighter level hit points as a bonus action once per short or long rest."
    },
    2: {
        "name": "Action Surge (one use)",
        "description": "You can take one additional action on your turn. This ability can be used once per short or long rest."
    },
    3: {
        "name": "Martial Archetype",
        "description": "Choose a Martial Archetype (e.g., Champion, Battle Master, Eldritch Knight), gaining unique features."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "Extra Attack",
        "description": "You can attack twice when you take the Attack action."
    },
    6: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    7: {
        "name": "Martial Archetype Feature",
        "description": "Gain a new ability from your chosen Martial Archetype."
    },
    8: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "Indomitable (one use)",
        "description": "You can reroll a failed saving throw. This ability can be used once per long rest."
    },
    10: {
        "name": "Martial Archetype Feature",
        "description": "Gain a new ability from your chosen Martial Archetype."
    },
    11: {
        "name": "Extra Attack (2)",
        "description": "You can attack three times when you take the Attack action."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "Indomitable (two uses)",
        "description": "You can now use Indomitable twice per long rest."
    },
    14: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    15: {
        "name": "Martial Archetype Feature",
        "description": "Gain a new ability from your chosen Martial Archetype."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "Action Surge (two uses), Indomitable (three uses)",
        "description": "You can now use Action Surge twice per short or long rest. You can now use Indomitable three times per long rest."
    },
    18: {
        "name": "Martial Archetype Feature",
        "description": "Gain a new ability from your chosen Martial Archetype."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Extra Attack (3)",
        "description": "You can attack four times when you take the Attack action."
    }
}

SKILLS_MONK_SKILLNAME = {
    1: {
        "name": "Unarmored Defense, Martial Arts",
        "description": "Unarmored Defense grants AC equal to 10 + Dexterity mod + Wisdom mod when not wearing armor. Martial Arts allows you to use Dexterity instead of Strength for unarmed strikes and monk weapons, use a d4 for unarmed strike damage, and make an unarmed strike as a bonus action."
    },
    2: {
        "name": "Ki, Unarmored Movement",
        "description": "Ki grants you special abilities like Flurry of Blows, Patient Defense, and Step of the Wind. Unarmored Movement increases your speed when not wearing armor."
    },
    3: {
        "name": "Monastic Tradition, Deflect Missiles",
        "description": "Choose a Monastic Tradition (e.g., Way of the Open Hand, Shadow, or Four Elements). Deflect Missiles lets you reduce the damage from a ranged attack and potentially catch and throw the projectile."
    },
    4: {
        "name": "Ability Score Improvement, Slow Fall",
        "description": "Increase one ability score by 2, or two ability scores by 1. Slow Fall lets you reduce falling damage by five times your monk level."
    },
    5: {
        "name": "Extra Attack, Stunning Strike",
        "description": "You can attack twice when you take the Attack action. Stunning Strike lets you spend 1 ki point to attempt to stun an opponent until the end of your next turn."
    },
    6: {
        "name": "Ki-Empowered Strikes, Monastic Tradition Feature",
        "description": "Your unarmed strikes count as magical for overcoming resistance and immunity to nonmagical attacks. Gain a new feature from your Monastic Tradition."
    },
    7: {
        "name": "Evasion, Stillness of Mind",
        "description": "Evasion allows you to take no damage on a successful Dexterity saving throw and half damage on a failure. Stillness of Mind lets you end the charmed or frightened condition as an action."
    },
    8: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "Unarmored Movement Improvement",
        "description": "You can now move along vertical surfaces and across liquids without falling during your turn."
    },
    10: {
        "name": "Purity of Body",
        "description": "You are immune to disease and poison."
    },
    11: {
        "name": "Monastic Tradition Feature",
        "description": "Gain a new ability from your Monastic Tradition."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "Tongue of the Sun and Moon",
        "description": "You can understand and be understood by any creature that knows a language."
    },
    14: {
        "name": "Diamond Soul",
        "description": "You gain proficiency in all saving throws, and can spend 1 ki point to reroll a failed save."
    },
    15: {
        "name": "Timeless Body",
        "description": "You no longer suffer the effects of aging and cannot be aged magically."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "Monastic Tradition Feature",
        "description": "Gain a new ability from your Monastic Tradition."
    },
    18: {
        "name": "Empty Body",
        "description": "You can spend 4 ki points to become invisible for 1 minute and resistant to all damage except force damage."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Perfect Self",
        "description": "If you start combat with no ki points, you regain 4 ki points."
    }
}

SKILLS_PALADIN_SKILLNAME = {
    1: {
        "name": "Divine Sense, Lay on Hands",
        "description": "Divine Sense allows you to detect celestials, fiends, and undead within 60 feet. Lay on Hands lets you heal a total number of hit points equal to your Paladin level × 5."
    },
    2: {
        "name": "Fighting Style, Spellcasting, Divine Smite",
        "description": "Choose a Fighting Style that enhances your combat abilities. Gain the ability to cast paladin spells. Divine Smite allows you to expend spell slots to deal radiant damage when you hit with a melee weapon."
    },
    3: {
        "name": "Divine Health, Sacred Oath",
        "description": "Divine Health makes you immune to disease. Sacred Oath grants unique abilities based on your chosen Oath."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "Extra Attack",
        "description": "You can attack twice when you take the Attack action."
    },
    6: {
        "name": "Aura of Protection",
        "description": "You and allies within 10 feet gain a bonus to saving throws equal to your Charisma modifier."
    },
    7: {
        "name": "Sacred Oath Feature",
        "description": "Gain a new ability from your chosen Sacred Oath."
    },
    8: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    10: {
        "name": "Aura of Courage",
        "description": "You and allies within 10 feet cannot be frightened while you are conscious."
    },
    11: {
        "name": "Improved Divine Smite",
        "description": "Your melee weapon attacks automatically deal an extra 1d8 radiant damage."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    14: {
        "name": "Cleansing Touch",
        "description": "You can use an action to end one spell affecting yourself or another creature. Usable a number of times equal to your Charisma modifier per long rest."
    },
    15: {
        "name": "Sacred Oath Feature",
        "description": "Gain a new ability from your chosen Sacred Oath."
    },
16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    18: {
        "name": "Aura Improvements",
        "description": "Your Aura of Protection and Aura of Courage now extend to 30 feet."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Sacred Oath Feature",
        "description": "Gain the final ability from your chosen Sacred Oath."
    }
}

SKILLS_RANGER_SKILLNAME = {
    1: {
        "name": "Favored Enemy, Natural Explorer",
        "description": "Favored Enemy grants bonuses when tracking and recalling information about a chosen enemy type. Natural Explorer enhances travel and survival abilities in a chosen terrain."
    },
    2: {
        "name": "Fighting Style, Spellcasting",
        "description": "Choose a Fighting Style that enhances combat abilities. Gain the ability to cast ranger spells."
    },
    3: {
        "name": "Ranger Archetype, Primeval Awareness",
        "description": "Choose a Ranger Archetype, gaining unique abilities. Primeval Awareness lets you sense the presence of specific creatures within 1 mile by expending a spell slot."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "Extra Attack",
        "description": "You can attack twice when you take the Attack action."
    },
    6: {
        "name": "Favored Enemy and Natural Explorer Improvements",
        "description": "Choose an additional favored enemy and favored terrain, gaining the benefits of those features again."
    },
    7: {
        "name": "Ranger Archetype Feature",
        "description": "Gain a new ability from your chosen Ranger Archetype."
    },
    8: {
        "name": "Ability Score Improvement, Land’s Stride",
        "description": "Increase one ability score by 2, or two ability scores by 1. Land’s Stride allows you to move through nonmagical difficult terrain without extra movement and resist magical effects that slow movement."
    },
    9: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    10: {
        "name": "Natural Explorer Improvement, Hide in Plain Sight",
        "description": "Choose another favored terrain. Hide in Plain Sight allows you to camouflage yourself when stationary, making it harder to be detected."
    },
    11: {
        "name": "Ranger Archetype Feature",
        "description": "Gain a new ability from your chosen Ranger Archetype."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    14: {
        "name": "Favored Enemy Improvement, Vanish",
        "description": "Choose another favored enemy. Vanish allows you to Hide as a bonus action and prevents enemies from tracking you unless by magical means."
    },
    15: {
        "name": "Ranger Archetype Feature",
        "description": "Gain a new ability from your chosen Ranger Archetype."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    18: {
        "name": "Feral Senses",
        "description": "You gain blindsight up to 30 feet, allowing you to sense invisible creatures near you."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Foe Slayer",
        "description": "Once per turn, you can add your Wisdom modifier to an attack roll or damage roll against a favored enemy."
    }
}

SKILLS_ROUGE_SKILLNAME = {
    1: {
        "name": "Expertise, Sneak Attack, Thieves’ Cant",
        "description": "Expertise lets you double proficiency in two skills. Sneak Attack grants bonus damage when attacking with advantage. Thieves’ Cant is a secret language known only to Rogues."
    },
    2: {
        "name": "Cunning Action",
        "description": "You can take the Dash, Disengage, or Hide action as a bonus action."
    },
    3: {
        "name": "Roguish Archetype",
        "description": "Choose a Roguish Archetype (e.g., Assassin, Thief, Arcane Trickster), granting new abilities."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "Uncanny Dodge",
        "description": "When an attacker you can see hits you, you can use your reaction to halve the damage."
    },
    6: {
        "name": "Expertise",
        "description": "Choose two more skills to gain double proficiency."
    },
    7: {
        "name": "Evasion",
        "description": "When making a Dexterity saving throw, you take no damage on a success and only half damage on a failure."
    },
    8: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "Roguish Archetype Feature",
        "description": "Gain a new feature from your Roguish Archetype."
    },
    10: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    11: {
        "name": "Reliable Talent",
        "description": "When you make an ability check with a proficient skill, you treat a d20 roll of 9 or lower as a 10."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "Roguish Archetype Feature",
        "description": "Gain a new feature from your Roguish Archetype."
    },
    14: {
        "name": "Blindsense",
        "description": "If you can hear, you are aware of hidden or invisible creatures within 10 feet."
    },
    15: {
        "name": "Slippery Mind",
        "description": "You gain proficiency in Wisdom saving throws."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "Roguish Archetype Feature",
        "description": "Gain a new feature from your Roguish Archetype."
    },
    18: {
        "name": "Elusive",
        "description": "No attack roll against you has advantage if you aren’t incapacitated."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Stroke of Luck",
        "description": "Once per short rest, you can treat a failed attack roll or ability check as a natural 20."
    }
}

SKILLS_SORCERER_SKILLNAME = {
    1: {
        "name": "Spellcasting, Sorcerous Origin",
        "description": "Gain the ability to cast sorcerer spells. Choose a Sorcerous Origin, which grants unique abilities and spells."
    },
    2: {
        "name": "Font of Magic",
        "description": "Gain Sorcery Points, which can be used to create spell slots or fuel Metamagic abilities."
    },
    3: {
        "name": "Metamagic",
        "description": "Choose two Metamagic options, allowing you to alter your spells in various ways, such as extending their range or making them harder to resist."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    6: {
        "name": "Sorcerous Origin Feature",
        "description": "Gain a new ability from your chosen Sorcerous Origin."
    },
    7: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    8: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    10: {
        "name": "Metamagic",
        "description": "Choose an additional Metamagic option."
    },
    11: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    14: {
        "name": "Sorcerous Origin Feature",
        "description": "Gain a new ability from your chosen Sorcerous Origin."
    },
    15: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "Metamagic",
        "description": "Choose an additional Metamagic option."
    },
    18: {
        "name": "Sorcerous Origin Feature",
        "description": "Gain a new ability from your chosen Sorcerous Origin."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Sorcerous Restoration",
        "description": "Regain 4 Sorcery Points when you finish a short rest."
    }
}

SKILLS_WARLOCK_SKILLNAME = {
    1: {
        "name": "Otherworldly Patron, Pact Magic",
        "description": "Choose an Otherworldly Patron, which grants unique abilities. Gain access to Pact Magic, a form of spellcasting that relies on limited but powerful spell slots."
    },
    2: {
        "name": "Eldritch Invocations",
        "description": "Gain access to Eldritch Invocations, which provide magical enhancements, including passive effects and spellcasting options."
    },
    3: {
        "name": "Pact Boon",
        "description": "Choose a Pact Boon: Pact of the Chain (familiar), Pact of the Blade (magical weapon), or Pact of the Tome (additional spells)."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    6: {
        "name": "Otherworldly Patron Feature",
        "description": "Gain a new ability from your chosen Otherworldly Patron."
    },
    7: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    8: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    10: {
        "name": "Otherworldly Patron Feature",
        "description": "Gain a new ability from your chosen Otherworldly Patron."
    },
    11: {
        "name": "Mystic Arcanum (6th level)",
        "description": "Gain a 6th-level spell that can be cast once per long rest without expending a spell slot."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "Mystic Arcanum (7th level)",
        "description": "Gain a 7th-level spell that can be cast once per long rest without expending a spell slot."
    },
    14: {
        "name": "Otherworldly Patron Feature",
        "description": "Gain a new ability from your chosen Otherworldly Patron."
    },
    15: {
        "name": "Mystic Arcanum (8th level)",
        "description": "Gain an 8th-level spell that can be cast once per long rest without expending a spell slot."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "Mystic Arcanum (9th level)",
        "description": "Gain a 9th-level spell that can be cast once per long rest without expending a spell slot."
    },
    18: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Eldritch Master",
        "description": "You can spend 1 minute entreating your patron to regain all expended Pact Magic spell slots."
    }
}

SKILLS_WIZARD_SKILLNAME = {
    1: {
        "name": "Spellcasting, Arcane Recovery",
        "description": "Gain the ability to cast wizard spells. Arcane Recovery allows you to regain expended spell slots (of combined levels up to half your wizard level) once per day after a short rest."
    },
    2: {
        "name": "Arcane Tradition",
        "description": "Choose an Arcane Tradition, which grants unique abilities and specializes your magical study (e.g., Evocation, Necromancy, Illusion)."
    },
    3: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    4: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    5: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    6: {
        "name": "Arcane Tradition Feature",
        "description": "Gain a new ability from your chosen Arcane Tradition."
    },
    7: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    8: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    9: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    10: {
        "name": "Arcane Tradition Feature",
        "description": "Gain a new ability from your chosen Arcane Tradition."
    },
    11: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    12: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    13: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    14: {
        "name": "Arcane Tradition Feature",
        "description": "Gain a new ability from your chosen Arcane Tradition."
    },
    15: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    16: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    17: {
        "name": "No new features",
        "description": "No additional features gained at this level."
    },
    18: {
        "name": "Spell Mastery",
        "description": "Choose a 1st-level and a 2nd-level wizard spell. You can cast these spells at their lowest level without expending a spell slot."
    },
    19: {
        "name": "Ability Score Improvement",
        "description": "Increase one ability score by 2, or two ability scores by 1."
    },
    20: {
        "name": "Signature Spell",
        "description": "Choose two 3rd-level wizard spells. You can cast these spells at their lowest level without expending a spell slot, and you can cast them at higher levels by using spell slots."
    }
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
