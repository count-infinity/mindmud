"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia.objects.objects import DefaultCharacter
from evennia.typeclasses.attributes import AttributeProperty
from evennia.utils.utils import lazy_property

from .objects import ObjectParent

from world.skills import SkillHandler


class Character(ObjectParent, DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_post_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """

    is_pc=True

    strength = AttributeProperty(10)
    dexterity = AttributeProperty(10)
    intelligence = AttributeProperty(10)
    health = AttributeProperty(10)
    level = 1
    hp = AttributeProperty(8)
    hp_max = AttributeProperty(8)
    xp = AttributeProperty(0)
    race = AttributeProperty("Default Race")
    character_class = AttributeProperty("Default Class")

    def get_stat(self, stat):
        if stat=='DX':
            return self.db.dexterity
        elif stat=='ST':
            return self.db.strength
        elif stat=='IQ':
            return self.db.intelligence
        elif stat=='HT':
            return self.db.health
        else:
            return self.attributes.get(stat)

    @lazy_property
    def skills(self):
       return SkillHandler(self)