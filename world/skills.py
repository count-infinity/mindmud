import csv
from evennia import logger
from collections import namedtuple

AcquiredSkill=namedtuple("AcquiredSkill", ['skill_key','controlling_attribute','adjustment'])

class SkillService:

    skills = None
    raw_skills = None

    def load_all_skills(self):
        self.raw_skills={}
        self.skills={}

        logger.info("Loading all skills.")
        
        with open('world/skill_tables.csv', newline='', encoding='utf-8-sig') as csvfile:
            skill_list = csv.DictReader(csvfile)
            for skill in skill_list:
                self.raw_skills[skill["key"]]=skill

        for skill, value in self.raw_skills.items():
            self.parse_skill(skill, value)

        logger.info(f"Loaded skills {len(self.skills)}")
        logger.trace(f"Loaded skills {self.skills}")
            
    def parse_skill(self, skill_key, value):
        if skill_key not in self.skills:

            skill=Skill(skill_key
                        ,value["controlling_attribute"]
                        ,value["prerequisites"]
                        ,value["difficulty"]
                        ,None
                        ,value["tags"])
            
           
            
            self.skills[skill_key]=skill
            
            parsed_list=self.parse_defaults(skill_key, value["defaults"])
            skill.defaults=parsed_list
            return skill
            


    '''
    Parse list of defaults in skill;adjustment string format
    i.e. parses "dx;-5,flail;-6" to [(dx,-5),(flail,-6)]
    '''
    def parse_defaults(self,skill_key,defaults):
        parsed_list=[]        
        if defaults != "None":
            default_list=defaults.split(",")
            for default_skill in default_list:
                dflt, adjust=default_skill.split(';')
                if dflt in self.skills or dflt in ('DX','IQ','HT','ST'):
                    parsed_list.append((dflt,int(adjust)))
                else:
                    if dflt in self.raw_skills:
                        self.parse_skill(dflt,self.raw_skills[dflt])
                        parsed_list.append((dflt,int(adjust)))
                    else:
                        raise ValueError(f"Default Skill not found {skill_key} - {dflt}")
        return parsed_list
    
    def getSkill(self, key):
        return self.skills[key]
    
skillService = SkillService()


class SkillHandler:
    def __init__(self, obj):
        self.obj = obj
        self.do_save = False
        self._load()

    def _load(self):
        self.storage = self.obj.attributes.get(
            "_skills", default=[], category="skills")
        self.storage = [AcquiredSkill(*x) for x in self.storage]

    def _save(self):
        self.obj.attributes.add(
            "_skills", self.storage, category="skills")
        self._load()  # important
        self.do_save = False

    def add(self, acquired_skill):
        self.storage.append(acquired_skill)
        self._save()

    def remove(self, skill_key):
        self.storage=[skill for skill in self.storage if skill.skill_key != skill_key]
        self._save()

    def get(self,skill_key):
        return next((x for x in self.storage if x.skill_key == skill_key), None)
    
    def has_skill(self,skill_key):
        if self.get(skill_key):
            return True
        if skill_key in ['DX','IQ','ST','HT']:
            return True
        return False
    
    def skills_from(self, skill_list):
        potential_skills=[]
        for skill in skill_list:
            skill_key, _ = skill
            has_skill=self.has_skill(skill_key)
            if has_skill:
                potential_skills.append(skill)
        return potential_skills
    
    def adjusted_skills(self, skill_list):
        adj_list=[]
        for skill in skill_list:
            skill_key,adjustment = skill
            if skill_key in ['DX','IQ','ST','HT']:
                skill_base=self.obj.get_stat(skill_key)
                total=skill_base+adjustment
                adj_list.append((skill_key,total))
            else:
                acquired_skill = self.get(skill_key)
                self.obj.msg(f"Acquired skill {acquired_skill}")
                skill_base=self.obj.get_stat(acquired_skill.controlling_attribute)
                adjusted_base=skill_base+acquired_skill.adjustment
                total = adjusted_base+skill[1]
                adj_list.append((skill_key,total))
        return adj_list

class Skill:
    def __init__(self,key,controlling_attribute,prerequisites,difficulty,defaults,tags, *args, **kwargs):
        self.key=key
        self.controlling_attribute=controlling_attribute
        self.prerequisites=prerequisites
        self.difficulty=difficulty
        self.defaults=defaults
        self.tags=tags

        for key, value in kwargs.items():
            setattr(self,key,value)    
            
    def __repr__(self):
        attrs=", ".join(f"{key}={value!r}" for key, value in self.__dict__.items())
        return f"{self.__class__.__name__}({attrs})"
    
    def __str__(self):
        return self.__repr__()

    