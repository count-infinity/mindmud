# in mygame/evadventure/chargen.py

from typeclasses.characters import Character
from .rules import DEFAULT_STARTING_POINTS
from .rules import dice
from .rules import GURPSRuleset

from evennia import CmdSet, EvMenu
from evennia import create_object


_TEMP_SHEET = """
{name}
{race}/{character_class}

{description}

ST +{strength}
DX +{dexterity}
IQ +{intelligence}
HT +{health}

Level: {level}

Points: {points}

"""

class TemporaryCharacterSheet:

    def _random_ability(self):
        return min(dice.roll("1d6"), dice.roll("1d6"), dice.roll("1d6"))

    def __init__(self):        

        # name will likely be modified later
        self.name = "Default Name"
        self.description = "A random description for a n00b."
        self.points = DEFAULT_STARTING_POINTS

        self.modifiers=[]

        self.attributes={
            "strength": 10,
            "dexterity": 10,
            "health": 10,
            "intelligence": 10,
            "race": "Human",
            "character_class": "Fighter",
            "level": 1
        }

    def has_modifier(self, key):
        for mod in self.modifiers:
            if mod.key == key:
                return True
        
        return False
        
    def show_sheet(self):
        return _TEMP_SHEET.format(
            name=self.name,
            strength=self.attributes['strength'],
            dexterity=self.attributes['dexterity'],            
            intelligence=self.attributes['intelligence'],
            health=self.attributes['health'],
            description=self.description, 
            race = self.attributes['race'],
            character_class= self.attributes['character_class'],
            level=self.attributes['level'],
            points=self.points          
        )
    
    def apply(self, account):
        # create character object with given abilities

        
        new_character, _ = account.create_character(
            key=self.name,
            description = self.description,
            attributes=(
                ("name", self.name),                
                ("strength", self.attributes['strength']),
                ("dexterity", self.attributes['dexterity']),                
                ("intelligence", self.attributes['intelligence']),
                ("health", self.attributes['health']),
                ("race",self.attributes['race']),
                ("character_class",self.attributes['character_class']),
                ("level",self.attributes['level']),                
            ),
        )

        return new_character


def start_chargen(caller, session=None, opts={}):
    """
    This is a start point for spinning up the chargen from a command later.

    """

    menutree = {
        "node_chargen":node_chargen,
        "node_create_character":node_create_character
    }

    # this generates all random components of the character
    tmp_character = TemporaryCharacterSheet()
    tmp_character.name=opts["name"]
    tmp_character.description=opts["description"]

    print(f"Tmp character with desc {opts['description']}")

    EvMenu(
        caller,
        menutree,
        session=session,
        startnode="node_chargen",
        startnode_input=("", {"tmp_character": tmp_character}),
    )

def node_chargen(caller, raw_string, **kwargs):


    tmp_character = kwargs["tmp_character"]

    text = tmp_character.show_sheet()

    options = [        
        {
           "desc": "Create Character",
           "goto": ("node_create_character", kwargs)
        },
        {"key": "_default",
         "goto": (_set_attribute, kwargs)}
    ]    

    return text, options

def _set_attribute(caller, raw_string, **kwargs):
    attrname, value = raw_string.split()  # would need error handling here!
    if attrname in ("strength","str","st","iq","int","intelligence","dx","dex","dexterity","ht","health"):
        
        if attrname in ("strength","str","st"):
            attrname="strength"
        elif attrname in ("iq","int","intelligence"):
            attrname="intelligence"
        elif attrname in ("dx","dex","dexterity"):
            attrname="dexterity"
        elif attrname in ("ht"):
            attrname="health"

       
        tmp_sheet = kwargs["tmp_character"]        

        can_allocate, point_cost = GURPSRuleset.can_allocate(tmp_sheet,attrname,value)

        if not can_allocate:
            caller.msg(f"Setting {attrname} to {value} would cost too many points. ({point_cost})")
        else:
            caller.msg(f"You set {attrname} to {value}.")
            tmp_sheet.points += point_cost
            tmp_sheet.attributes[attrname]=int(value)
    else:
        caller.msg("That's not a valid input.")
    
    return False
    


def node_create_character(caller, raw_string, **kwargs):
    """
    End chargen and create the character. We will also puppet it.

    """
    tmp_character = kwargs["tmp_character"]
    tmp_character.apply(caller)

    text = "Character created!"

    return text, None