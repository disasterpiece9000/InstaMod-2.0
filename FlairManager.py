import time

# Get new flair for all enabled options
def update_flair(r, user, sub, prog_flair_enabled, new_accnt_flair_enabled, activity_flair_enabled):
    prog_flair = None
    new_accnt_flair = None
    activity_flair = None
    css = None
    permissions = []
    
    # Progression Flair
    if prog_flair_enabled:
        prog_data = make_prog_flair(user, sub)
        prog_flair = prog_data[0]
        css = prog_data[1]
        if prog_data[2] is not None:
            permissions.append(prog_data[2])
            
    # New Account Flair
    if new_accnt_flair_enabled:
        new_accnt_flair = make_new_accnt_flair(user, sub)
        
    # Activity Flair
    if activity_flair_enabled:
        activity_data = make_activity_flair(user, sub)
        

def make_activity_flair(user, sub):
    activity_options = sub.sub_activity
    
    # Loop through options in order
    option_count = 1
    while True:
        option_name = "SUB ACTIVITY " + str(option_count)
        option_count += 1
        
        if option_name in activity_options:
            main_option = activity_options[option_name]
            sub_group = main_option["target subs"]
            main_metric = main_option["metric"]
            
            sub_list = list(sub.sub_groups[sub_group].keys())
            
            for target_sub in sub_list:
                main_result = check_activity(user, sub, target_sub, main_option)
                
                if not main_result:
                    continue
                
                and_result = True
                or_result = True
                
        

# Get progression tier flair
def make_prog_flair(user, sub):
    prog_tiers = sub.progression_tiers
    
    # Loop through tiers in order
    tier_count = 1
    while True:
        tier_name = "PROGRESSION TIER " + str(tier_count)
        tier_count += 1
        
        if tier_name in prog_tiers:
            main_tier = prog_tiers[tier_name]
            main_result = user_in_tier(main_tier, user, sub)
            
            if not main_result:
                continue
            
            and_result = True
            or_result = True
            
            # Check for AND/OR rules
            tier_name_and = tier_name + " - AND"
            tier_name_or = tier_name + " - OR"
            
            if tier_name_and in prog_tiers:
                and_tier = prog_tiers[tier_name_and]
                and_result = user_in_tier(and_tier, user, sub)
                
            elif tier_name_or in prog_tiers:
                or_tier = prog_tiers[tier_name_or]
                or_result = user_in_tier(or_tier, user, sub)
                
            # Check if user meets all the criteria (including and/or)
            if main_result and and_result and or_result:
                return [main_tier["flair text"], main_tier["flair css"], main_tier["permissions"]]
            
        # Last tier was discovered
        else:
            return [None, None, None]


def make_new_accnt_flair(user, sub):
    username = str(user)
    min_accnt_age = int(sub.flair_config["young account age"])
    user_created = sub.db.fetch_info_table(username, "date created")
    current_time = int(time.time())
    month_diff = int((current_time - user_created) / 2629746)
    
    if month_diff >= min_accnt_age:
        return str(month_diff) + " months old"
    else:
        return None


def check_activity(user, sub, target_sub, option):
    target_value = int(option["value"])
    metric = option["metric"]
    comparison = option["comparison"]
    user_value = get_user_value(metric, [target_sub], user, sub)
    
    return check_value(user_value, comparison, target_value)


# Check if the user belongs in the given tier
def user_in_tier(tier, user, sub):
    # Turn Sub Group into list if all subs option not selected
    target_subs = tier["target subs"]
    if target_subs != "ALL":
        sub_list = list(sub.sub_groups[target_subs].keys())
    else:
        sub_list = "ALL"
        
    metric = tier["metric"]
    comparison = tier["comparison"]
    value = int(tier["value"])
    user_value = get_user_value(metric, sub_list, user, sub)
    
    return check_value(user_value, comparison, value)
    

# Fetch the user_value from the database
def get_user_value(metric, sub_list, user, sub):
    username = str(user)
    user_value = 0
    
    # Get data from accnt_info table
    if metric in ("total comment karma", "total post karma"):
        user_value = sub.db.fetch_info_table(username, metric)
    elif metric == "total karma":
        user_value = sub.db.fetch_info_table(username, "total post karma") + \
                     sub.db.fetch_info_table(username, "total comment karma")
    
    # Get data from accnt_history table
    elif metric in ("comment karma", "post karma", "positive comments", "negative comments",
                    "positive posts", "negative posts", "positive QC", "negative QC"):
        user_value = sub.db.fetch_hist_table(username, sub_list, metric)
    elif metric == "net QC":
        user_value = sub.db.fetch_hist_table(username, sub_list, "positive QC") - \
                     sub.db.fetch_hist_table(username, sub_list, "negative QC")
        
    return user_value


def check_value(user_value, comparison, value):
    if comparison == ">":
        return user_value > value
    if comparison == "<":
        return user_value > value
    if comparison == ">=":
        return user_value >= value
    if comparison == "<=":
        return user_value <= value
