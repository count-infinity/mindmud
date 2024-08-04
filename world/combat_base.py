from evennia import DefaultScript, create_script

from typeclasses.objects import Object
from commands.command import Command
from .rules import GURPSRuleset, dice
from world.skills import skillService

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

    def resolve_attack(source, target, weapon):
        GURPSCombatHandler.base_skill(source, weapon)

    def base_skill(source, weapon):

        weapon_skill = weapon.attributes.get('skill')
        if skill_to_use := source.skills.get(weapon_skill):
            skill_to_use = source.skills.adjusted_skills([(skill_to_use.skill_key,0)])[0]
        else:
            skill_to_use = GURPSCombatHandler.select_max_skill(source, weapon.db.default)  

        source.msg(f"Skill to use {skill_to_use}")      

        dice_roll, total=dice.roll("3d6")
        hit = True if total<=skill_to_use[1] else False
        
        source.msg(f"Attack with {weapon.db.weapon} using skill {skill_to_use[0]}, rolled {dice_roll} for {total}.  Hits: {hit}")

    def select_max_skill(source, skill_list):
        print(f"Default skill list {skill_list}")

        potential_skills=source.skills.skills_from(skill_list)
        adj_skills = source.skills.adjusted_skills(potential_skills)
        max_skill = max(adj_skills, key=lambda x: x[1])

        return max_skill

class Weapon(Object):   
        
    def get_display_desc(self, looker, **kwargs):
        """The main display"""
        return self.attributes.get("name")

class MeleeWeapon(Weapon):
    pass

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
        GURPSCombatHandler.resolve_attack(self.caller,target,self.caller.db.weapon)
        

