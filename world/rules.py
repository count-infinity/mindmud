from random import randint

DEFAULT_STARTING_POINTS = 125

class EvAdventureRollEngine:
    """
    This groups all dice rolls of EvAdventure. These could all have been normal functions, but we
    are group them in a class to make them easier to partially override and replace later.

    """

    def roll(self, roll_string, max_number=10):
        """
        NOTE: In evennia/contribs/rpg/dice/ is a more powerful dice roller with
        more features, such as modifiers, secret rolls etc. This is much simpler and only
        gets a simple sum of normal rpg-dice.

        Args:
            roll_string (str): A roll using standard rpg syntax, <number>d<diesize>, like
                1d6, 2d10 etc. Max die-size is 1000.
            max_number (int): The max number of dice to roll. Defaults to 10, which is usually
                more than enough.

        Returns:
            int: The rolled result - sum of all dice rolled.

        Raises:
            TypeError: If roll_string is not on the right format or otherwise doesn't validate.

        Notes:
            Since we may see user input to this function, we make sure to validate the inputs (we
            wouldn't bother much with that if it was just for developer use).

        """
        max_diesize = 1000
        roll_string = roll_string.lower()
        if "d" not in roll_string:
            raise TypeError(
                f"Dice roll '{roll_string}' was not recognized. Must be `<number>d<dicesize>`."
            )
        number, diesize = roll_string.split("d", 1)
        try:
            number = int(number)
            diesize = int(diesize)
        except Exception:
            raise TypeError(f"The number and dice-size of '{roll_string}' must be numerical.")
        if 0 < number > max_number:
            raise TypeError(f"Invalid number of dice rolled (must be between 1 and {max_number})")
        if 0 < diesize > max_diesize:
            raise TypeError(f"Invalid die-size used (must be between 1 and {max_diesize} sides)")

        # At this point we know we have valid input - roll and add dice together
        return sum(randint(1, diesize) for _ in range(number))

# access rolls e.g. with rules.dice.opposed_saving_throw(...)
dice = EvAdventureRollEngine()


class GURPSRuleset:
    ST_DEFAULT_POINTS_PER_LEVEL = 10
    DX_DEFAULT_POINTS_PER_LEVEL = 20
    IQ_DEFAULT_POINTS_PER_LEVEL = 20
    HT_DEFAULT_POINTS_PER_LEVEL = 10

    HP_DEFAULT_POINTS = 2
    WILL_DEFAULT_POINTS = 5
    PER_DEFAULT_POINTS = 5
    FP_DEFAULT_POINTS = 3
    BASIC_SPEED_DEFAULT_POINTS = 0.25
    BASIC_MOVE_DEFAULT_POINTS = 5

    WATER_MOVE_DEFAULT = 5


    def can_allocate(obj,attribute,amount):

        default_points_cost=0
        if attribute == "strength":
            default_points_cost=GURPSRuleset.ST_DEFAULT_POINTS_PER_LEVEL
        elif attribute == "dexterity":
            default_points_cost=GURPSRuleset.DX_DEFAULT_POINTS_PER_LEVEL
        elif attribute == "intelligence":
            default_points_cost=GURPSRuleset.IQ_DEFAULT_POINTS_PER_LEVEL
        elif attribute == "health":
            default_points_cost=GURPSRuleset.HT_DEFAULT_POINTS_PER_LEVEL


        current_value = obj.attributes[attribute]
        diff = current_value-int(amount)
        point_cost = diff*default_points_cost
        if obj.points+point_cost < 0:
            return False,point_cost                        
        return True,point_cost


class CharacterModifier:

    def BaseStrengthAllocation(amt):
        return CharacterModifier("BASE_STRENGTH_ALLOCATION","ST",0,amt)

    def __init__(self, key="",modifies="",point_cost=0, modify_by=0,prereqs=[], **kwargs):
        self.key=key
        self.modifies=modifies
        self.point_cost=point_cost
        self.modify_by=modify_by

        