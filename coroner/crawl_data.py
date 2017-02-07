# Current as of 0.19
CURRENT_SPECIES = set([sp.lower() for sp in 
    ('Human,High Elf,Deep Elf,Deep Dwarf,Hill Orc,Halfling,Kobold,Spriggan,Ogre,Troll,Naga,'
        + 'Centaur,Merfolk,Minotaur,Tengu,Draconian,Gargoyle,Formicid,Vine Stalker,Demigod,Demonspawn,'
        + 'Mummy,Ghoul,Vampire,Felid,Octopode,'
        + 'Black Draconian,Purple Draconian,Green Draconian,Yellow Draconian,Red Draconian,'
        + 'Mottled Draconian,White Draconian,Grey Draconian,Pale Draconian,'
).split(',')])
        
# Species that were removed between 0.10 and 0.19
LEGACY_SPECIES = {'mountain dwarf' , 'sludge elf'}
# Species that never made it into a release.
WEIRD_SPECIES = {'djinni', 'lava orc', 'barachian', 'grotesk'}
# Worth noting 'kenku' (old name for tengu) is not in any of these, but it gets 
# remapped when parsing
CANON_SPECIES = set.union(CURRENT_SPECIES, LEGACY_SPECIES)



CURRENT_BGS = set([bg.lower() for bg in ('Fighter,Gladiator,Monk,Hunter,Assassin,Artificer,Wanderer,Berserker,Abyssal Knight,'
        + 'Chaos Knight,Skald,Transmuter,Warper,Arcane Marksman,Enchanter,Wizard,Conjurer,'
        + 'Summoner,Necromancer,Fire Elementalist,Ice Elementalist,Air Elementalist,'
        + 'Earth Elementalist,Venom Mage,').split(',')])

LEGACY_BGS = {'stalker', 'priest', 'healer', 'death knight'}
# According to the wiki, paladins were removed in 0.8.0
WEIRD_BGS = {'jester', 'paladin'}
CANON_BGS = set.union(CURRENT_BGS, LEGACY_BGS)

GROUPED_BGS = {
        'Warriors': 'fighter,gladiator,monk,hunter,assassin',
        'Zealots': 'berserker,abyssal knight,chaos knight',
        'Warrior-mages': 'skald,transmuter,warper,arcane marksman,enchanter',
        'Mages': 'wizard,conjurer,summoner,necromancer,fire elementalist' +
            ',ice elementalist,air elementalist,earth elementalist,venom mage',
}
for k,v in GROUPED_BGS.items():
    GROUPED_BGS[k] = v.split(',')



GODS = set(('ashenzari,beogh,cheibriados,dithmenos,elyvilon,fedhas,gozag,hepliaklqana,jiyva,kikubaaqudgha,lugonu,makhleb,nemelex xobeh,okawaru,pakellas,qazlal,ru,sif muna,the shining one,trog,uskayaw,vehumet,xom,yredelemnul,zin').split(','))

RENAMED_GODS = {'dithmengos': 'dithmenos', 'ukayaw': 'uskayaw'}

def lookup_fancy_god_name(name):
    if name in GODS:
        return name
    if name in RENAMED_GODS:
        return RENAMED_GODS[name]
    if name == 'warmaster okawaru':
        return 'okawaru'
    if name.startswith('the xom-meister'): # really?
        return 'xom'
    parts = name.split()
    if parts[0] in GODS:
        return parts[0]
    if parts[0] in RENAMED_GODS:
        return RENAMED_GODS[parts[0]]
    binomial = ' '.join(parts[:2])
    if binomial in GODS:
        return binomial
    assert False, "Unrecognized fancy god name: {!r}".format(name)

# Skipping dungeon, hells, because they're probably not useful for the kind of
# analysis I'm planning to do with this information
BRANCHES = set(('temple,lair,shoals,snake,slime,orc,elf,vaults,swamp,spider'
    + ',depths,tomb,zot,crypt').split(','))


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

GROUPED_SKILLS = {
    'melee': {'fighting', 'short blades', 'long blades', 'axes', 'maces & flails',
              'polearms', 'staves', 'unarmed combat',},
    'ranged': {'bows', 'crossbows', 'slings', 'throwing'},
    'defense': {'armour', 'dodging', 'shields'},
    'magic': {'spellcasting', 'conjurations', 'hexes', 'charms', 'summonings',
                'necromancy', 'translocations', 'transmutations', 'fire magic',
                'ice magic', 'air magic', 'earth magic', 'poison magic'},
    'misc': {'invocations', 'evocations', 'stealth'},
}

CURRENT_SKILLS = set.union(*map(set, GROUPED_SKILLS.values()))

_MUTAGENIC_MONSTERS = {
    'an orb of fire', 'a neqoxec', 'a cacodemon', 'a shining eye'
}
_GOD_MUTATION_SOURCES = {
    "xom's mischief", "xom's grace", "jiyva's grace", "jiyva's power",
    "the severe capriciousness of xom", "ru sacrifice",
}

# This doesn't cover all possibilities, but it should encompass most of them
MUTATION_SOURCES = set.union({
    'mutagenic meat', 'potion of mutation', 'demonic ancestry',
    'potion of cure mutation',
    'wand of polymorph other',
    'species',
    'other',
}, _MUTAGENIC_MONSTERS, _GOD_MUTATION_SOURCES)



def canonical_mutation_source(src):
    if src in MUTATION_SOURCES:
        return src
    if src == 'demonic ancestry':
        return 'species'
    tokens = src.split()
    if (len(tokens) > 1 
            and tokens[-1] == 'growth' 
            and ' '.join(tokens[:-1]) in CANON_SPECIES):
        return 'species'
    return 'other'

