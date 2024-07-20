from evennia import DefaultScript, create_script

from typeclasses.objects import Object
from commands.command import Command
from .rules import GURPSRuleset
import prototypes

class CombatFailure(RuntimeError):
    pass


class GURPSCombatHandler(DefaultScript):
    @classmethod
    def get_or_create_combathandler(cls, obj, **kwargs):
        """
        Get or create a combathandler on `obj`.
    
        Args:
            obj (any): The Typeclassed entity to store this Script on. 
        Keyword Args:
            combathandler_key (str): Identifier for script. 'combathandler' by
                default.
            **kwargs: Extra arguments to the Script, if it is created.
    
        """
        if not obj:
            raise CombatFailure("Cannot start combat without a place to do it!")
    
        combathandler_key = kwargs.pop("key", "combathandler")
        combathandler = obj.ndb.combathandler
        if not combathandler or not combathandler.id:
            combathandler = obj.scripts.get(combathandler_key).first()
            if not combathandler:
                # have to create from scratch
                persistent = kwargs.pop("persistent", True)
                combathandler = create_script(
                    cls,
                    key=combathandler_key,
                    obj=obj,
                    persistent=persistent,
                    **kwargs,
                )
            obj.ndb.combathandler = combathandler
        return combathandler
    def get_combat_summary(self, combatant):
        pass
    def get_sides(self, combatant):
        pass
    def queue_action(self, combatant):
        pass



class Weapon(Object):   
        
    def get_display_desc(self, looker, **kwargs):
        """The main display"""
        return self.attributes.get("name")


class MeleeWeapon(Weapon):

    def at_object_creation(self):        
        self.attributes.add("tl",0)
        self.attributes.add("damage",{"swing": (0,'cut')})
        self.attributes.add("reach",1)
        self.attributes.add("parry",(0,'U'))
        self.attributes.add("cost",0)
        self.attributes.add("weight",0)
        self.attributes.add("st",0)

class CmdKill(Command):
    key="kill"
    aliases=["k","attack", "hit"]

    help_category="Combat"

    def parse(self):
        """
        Handle parsing of most supported combat syntaxes (except stunts).

        <action> [<target>|<item>]
        or
        <action> <item> [on] <target>

        Use 'on' to differentiate if names/items have spaces in the name.

        """
        self.args = args = self.args.strip()
        self.lhs, self.rhs = "", ""

        if not args:
            return

        if " on " in args:
            lhs, rhs = args.split(" on ", 1)
        else:
            lhs, *rhs = args.split(None, 1)
            rhs = " ".join(rhs)
        self.lhs, self.rhs = lhs.strip(), rhs.strip()

    def func(self):

        if not self.lhs:
            self.caller.msg(f"Attack what?")
            return None
        target = self.caller.search(self.lhs, quiet=True)                                    

        if not target:
            self.caller.msg(f"You can't see {self.lhs} to attack.")
            return None
        self.caller.msg(f"Combat started.{self.lhs}")
        GURPSRuleset.success_roll(12)
        

