
SPECIES = set([sp.lower() for sp in ('Human,High Elf,Deep Elf,Deep Dwarf,Hill Orc,Halfling,Kobold,Spriggan,Ogre,Troll,Naga,'
        + 'Centaur,Merfolk,Minotaur,Tengu,Draconian,Gargoyle,Formicid,Vine Stalker,Demigod,Demonspawn,'
        + 'Mummy,Ghoul,Vampire,Felid,Octopode,'
        + 'Black Draconian,Purple Draconian,Green Draconian,Yellow Draconian,Red Draconian,'
        + 'Mottled Draconian,White Draconian,Grey Draconian,Pale Draconian,'
        # Legacy/in development (wtf is a Grotesk?)
        + 'Mountain Dwarf,Djinni,Lava Orc,Sludge Elf,Barachian,Kenku,Grotesk'
        ).split(',')])

BGS = set([bg.lower() for bg in ('Fighter,Gladiator,Monk,Hunter,Assassin,Artificer,Wanderer,Berserker,Abyssal Knight,'
        + 'Chaos Knight,Skald,Transmuter,Warper,Arcane Marksman,Enchanter,Wizard,Conjurer,'
        + 'Summoner,Necromancer,Fire Elementalist,Ice Elementalist,Air Elementalist,'
        + 'Earth Elementalist,Venom Mage,'
        # Legacy
        + 'Jester,Stalker,Priest,Healer,Paladin,Death Knight').split(',')])

# dithmengos is borderline, and ukayaw
# Actually, should probably add them back and filter them out from canonical frame
# used for most analyses, like I'm doing with djinnis, jesters, stalkers, etc.
GODS = set(('ashenzari,beogh,cheibriados,dithmenos,elyvilon,fedhas,gozag,hepliaklqana,jiyva,kikubaaqudgha,lugonu,makhleb,nemelex xobeh,okawaru,pakellas,qazlal,ru,sif muna,the shining one,trog,uskayaw,vehumet,xom,yredelemnul,zin').split(','))

def lookup_fancy_god_name(name):
    if name in GODS:
        return name
    if name == 'warmaster okawaru':
        return 'okawaru'
    if name == 'the xom-meister': # really?
        return 'xom'
    parts = name.split()
    if name[0] in GODS:
        return name[0]
    binomial = ' '.join(name[:2])
    if binomial in GODS:
        return binomial
    assert False, "Unrecognized fancy god name: {}".format(name)

# Skipping dungeon, hells, because they're probably not useful for the kind of
# analysis I'm planning to do with this information
BRANCHES = set(('temple,lair,shoals,snake,slime,orc,elf,vaults,swamp,spider'
    + ',depths,tomb,zot,crypt').split(','))

GROUPED_BGS = {
        'Warriors': 'fighter,gladiator,monk,hunter,assassin',
        'Zealots': 'berserker,abyssal knight,chaos knight',
        'Warrior-mages': 'skald,transmuter,warper,arcane marksman,enchanter',
        'Mages': 'wizard,conjurer,summoner,necromancer,fire elementalist' +
            ',ice elementalist,air elementalist,earth elementalist,venom mage',
}

for k,v in GROUPED_BGS.items():
    GROUPED_BGS[k] = v.split(',')


# TODO: Distinguish removed vs. never-made-it-into-a-release
REMOVED_SPECIES = set('mountain dwarf,sludge elf'.split())
LEGACY_SPECIES = set('mountain dwarf,djinni,lava orc,sludge elf,barachian,kenku,grotesk'.split(','))

LEGACY_BGS = set('jester,stalker,priest,healer,paladin,death knight'.split(','))

CANON_SPECIES = SPECIES - LEGACY_SPECIES
CANON_BGS = BGS - LEGACY_BGS

# Valid 'wheredied' places
CANON_WD = {'abyss', 'bailey', 'bazaar', 'cocytus', 'crypt', 'depths', 'desolation of salt',
        'dungeon', 'ecumenical temple', 'elven halls', 'gehenna', 
        'hall of blades', 'hive',
        'ice cave', 'iron city of dis', 'labyrinth',
        'lair of beasts', 'orcish mines', 'ossuary', 'pandemonium',
        'pits of slime', 'realm of zot', 'sewer', 'shoals', 'snake pit', 'spider nest',
        'swamp', 'tartarus', 'tomb', 'treasure trove', 'vaults', 'vestibule of hell',
        'volcano', "wizard's laboratory",  'ziggurat', 
        'other',
        #'hive', 'treasure trove', 'north pole',
}

# Valid 'howdied' explanations
CANON_HOWDIED = {'asphyxiated', 'cloud', 'drowned', 'miscast', 'monster', 
        'quit', 'rot', 'starved', 'statdeath', 'suicide',
}

WIZLABS = {"cigotuvi's fleshworks", "doroklohe's tomb", "wucad mu's monastery", 
"wizard's laboratory", "zonguldrok's shrine", "iskendrun's mystic tower",
}

# I'm going to ignore the corresponding vampire lines (you were thirsty, very thirsty, etc.)
HUNGER_LINES = ['you were not hungry.', 'you were completely stuffed.', 'you were hungry.', 
    'you were full.', 'you were very hungry.', 'you were near starving.', 'you were very full.',
    'you were starving.',]
HUNGER_LINES = {line: line[len('you were '):-1] for line in HUNGER_LINES}

RUNES = {
        'abyssal', 'barnacled', 'bone', 'dark', 'decaying', 'demonic', 'fiery',
        'glowing', 'golden', 'gossamer', 'icy', 'iron', 'magical', 'obsidian',
        'serpentine', 'silver', 'slimy',
}

COLUMN_TO_CATEGORIES = {
    'bg':           BGS,
    'species':      SPECIES,
    'god':          GODS,
    'first_conversion': GODS,
    'wheredied':    CANON_WD,
    'hunger':       HUNGER_LINES,
    'howdied':      CANON_HOWDIED,
}

