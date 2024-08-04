"""
Server startstop hooks

This module contains functions called by Evennia at various
points during its startup, reload and shutdown sequence. It
allows for customizing the server operation as desired.

This module must contain at least these global functions:

at_server_init()
at_server_start()
at_server_stop()
at_server_reload_start()
at_server_reload_stop()
at_server_cold_start()
at_server_cold_stop()

"""
import csv
import ast
from evennia import logger
from evennia.prototypes.prototypes import create_prototype

from world.skills import skillService


def at_server_init():
    """
    This is called first as the server is starting up, regardless of how.
    """
    skillService.load_all_skills()
    load_weapon_prototypes()


def at_server_start():
    """
    This is called every time the server starts up, regardless of
    how it was shut down.
    """
    pass


def at_server_stop():
    """
    This is called just before the server is shut down, regardless
    of it is for a reload, reset or shutdown.
    """
    pass


def at_server_reload_start():
    """
    This is called only when server starts back up after a reload.
    """
    pass


def at_server_reload_stop():
    """
    This is called only time the server stops before a reload.
    """
    pass


def at_server_cold_start():
    """
    This is called only when the server starts "cold", i.e. after a
    shutdown or a reset.
    """
    pass


def at_server_cold_stop():
    """
    This is called only when the server goes down due to a shutdown or
    reset.
    """
    pass


def load_weapon_prototypes():
    with open('world/weapons_tables.csv', newline='', encoding='utf-8-sig') as csvfile:
        weaponreader = csv.DictReader(csvfile)
        
        weapon_list=[]
        for _weapon in weaponreader:
            weapon_list.append(_weapon['prototype_key'])
            logger.log_trace(f"Parsing weapons {_weapon['prototype_key']}")
            weapon_prototype = {
                    "prototype_key": _weapon["prototype_key"],
                    "key": _weapon['weapon'],
                    "tl": _weapon['tl'],
                    "damage": _weapon['damage'],
                    "reach": _weapon['reach'],
                    "parry": _weapon['parry'],
                    "cost": _weapon['cost'],
                    "weight": _weapon['weight'],
                    "st": _weapon['st'],
                    "notes": _weapon['notes'],
                    "skill": _weapon['skill'],
                    "weapon": _weapon['weapon'],
                    "default": ast.literal_eval(_weapon['default']),
                    "tags": ["weapon"],
                    "typeclass": "world.combat_base.MeleeWeapon",
            }
            
            create_prototype(weapon_prototype)
                        
        logger.log_info(f"Weapon Prototypes Loaded: {len(weapon_list)}")
        logger.log_trace(f"Weapon Prototypes Loaded: {weapon_list}")