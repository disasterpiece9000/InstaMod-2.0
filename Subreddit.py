from datetime import datetime
from configparser import ConfigParser
from Database import Database


class Subreddit:
    # Load settings from wiki page
    def __init__(self, sub_name, r):
        self.r = r
        self.sub_name = sub_name
        self.sub = r.subreddit(sub_name)
        self.db = None
        self.start_interval = datetime.now()
        
        # Read config file from wiki page
        config = ConfigParser(allow_no_value=True)
        config.read(sub_name + "/config.ini")
        #config.read_string(self.sub.wiki["InstaModTest"].content_md)
        self.main_config = config["MAIN CONFIG"]
        self.flair_config = config["FLAIR"]
        self.qc_config = config["QUALITY COMMENTS"]
        self.progression_tiers = self.load_nested_config("PROGRESSION TIER", config)
        self.sub_activity = self.load_nested_config("SUB ACTIVITY", config)
        self.sub_groups = self.load_nested_config("SUB GROUP", config)
    
    def make_db(self):
        self.db = Database(self.sub_name)
    
    # Process config options with multiple tiers
    # Tiers increment in number and each tier can have one sub-tier (AND or OR)
    @staticmethod
    def load_nested_config(main_name, config):
        hold_config = {}
        tier_count = 1
        
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
