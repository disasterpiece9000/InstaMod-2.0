from datetime import datetime
from configparser import ConfigParser
from Database import Database


class Subreddit:
    # Load settings from wiki page
    def __init__(self, folder_name, r):
        self.r = r
        self.folder_name = folder_name
        self.name = folder_name[2:].lower()
        self.sub = r.subreddit(self.name)
        self.db = None
        self.start_interval = datetime.now()
        self.mods = self.sub.moderator()
        
        # Prepare to read settings from wiki page
        self.main_config = None
        self.flair_config = None
        self.qc_config = None
        self.pm_commands = None
        self.pm_messages = None
        self.progression_tiers = None
        self.sub_activity = None
        self.sub_groups = None
        self.read_config()
    
    # Check wiki page for settings
    def read_config(self):
        config = ConfigParser(allow_no_value=True)
        # config.read(self.folder_name + "/config.ini")
        config.read_string(self.sub.wiki["InstaModTest"].content_md)
        self.main_config = config["MAIN CONFIG"]
        self.flair_config = config["FLAIR"]
        self.qc_config = config["QUALITY COMMENTS"]
        self.pm_commands = config["PM Commands"]
        self.pm_messages = config["PM Messages"]
        # Process sections with secondary criteria
        self.progression_tiers = self.load_nested_config("PROGRESSION TIER", config)
        self.sub_activity = self.load_nested_config("ACTIVITY TAG", config)
        self.sub_groups = self.load_nested_config("SUB GROUP", config)
        # Setup the sub's database
        self.db = Database(self.folder_name)
    
    # Process config options with multiple tiers
    @staticmethod
    def load_nested_config(main_name, config):
        hold_config = {}
        tier_count = 1

        # Tiers increment in number and each tier can have one sub-tier (AND or OR)
        while True:
            tier_name = main_name + " " + str(tier_count)
            tier_count += 1
            
            if tier_name in config:
                hold_config[tier_name] = config[tier_name]
                
                # Check for either and/or rule
                tier_name_and = tier_name + " - AND"
                tier_name_or = tier_name + " - OR"
                
                if tier_name_and in config:
                    hold_config[tier_name_and] = config[tier_name_and]
                elif tier_name_or in config:
                    hold_config[tier_name_or] = config[tier_name_or]
            
            # Last tier was discovered
            else:
                break

        return hold_config
