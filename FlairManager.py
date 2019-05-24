import time


# Get new flair for all enabled options
def update_flair(r, user, sub, prog_flair_enabled, new_accnt_flair_enabled, activity_flair_enabled):
    prog_flair = None
    new_accnt_flair = None
    activity_flair = None
    css = ""
    permissions = []
    
    # Progression Flair
    if prog_flair_enabled:
        prog_data = make_prog_flair(user, sub)
        prog_flair = prog_data[0]
        css = prog_data[1]
        if prog_data[2] != "None":
            permissions.append(prog_data[2])
            
    # New Account Flair
    if new_accnt_flair_enabled:
        new_accnt_flair = make_new_accnt_flair(user, sub)
        
    # Activity Flair
    if activity_flair_enabled:
        activity_data = make_activity_flair(user, sub)
        activity_flair_list = activity_data[0]
        permissions.append(activity_data[1])
        
    full_flair_txt = concat_flair(prog_flair, new_accnt_flair, activity_flair)
    print("User: " + str(user)
          + "\nFlair: " + full_flair_txt
          + "\nCSS: " + css)
        

def make_activity_flair(user, sub):
    activity_options = sub.sub_activity
    flair_text = []
    permissions = []
    
    # Loop through options in order
    option_count = 1
    while True:
        option_name = "SUB ACTIVITY " + str(option_count)
        option_count += 1
        
        if option_name in activity_options:
            main_option = activity_options[option_name]
            sub_group_name = main_option["target subs"]
            sub_group = sub.sub_groups[sub_group_name]
            sub_list = list(sub_group.keys())
            
            for target_sub in sub_list:
                main_data = check_activity(user, sub, target_sub, main_option, sub_group)
                main_result = main_data[0]
                user_value = main_data[1]
                
                if not main_result:
                    continue
                
                # Check for AND/OR rules
                and_result = True
                or_result = True
                option_name_and = option_name + " - AND"
                option_name_or = option_name + " - OR"
                
                if option_name_and in activity_options:
                    and_option = activity_options[option_name_and]
                    and_result = check_activity(user, sub, target_sub, and_option, sub_group)[0]
                    
                elif option_name_or in activity_options:
                    or_option = activity_options[option_name_or]
                    or_result = check_activity(user, sub, target_sub, or_option, sub_group)[0]
                    
                if main_result and and_result and or_result:
                    pre_text = main_option["pre text"]
                    post_text = main_option["post text"]
                    sub_abbrev = sub_group[target_sub]
                    display_value = main_option.getboolean("display value")
                    
                    full_text = ""
                    if pre_text != "None":
                        full_text += pre_text + " "
                    full_text += sub_abbrev
                    if post_text != "None":
                        full_text += " " + post_text
                    if display_value:
                        full_text += " " + str(user_value)
                        
                    flair_text.append(full_text)
                    new_permissions = main_option["permissions"]
                    if new_permissions != "None":
                        permissions.append(new_permissions)
                    
        else:
            break
            
    return [flair_text, permissions]
                        

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
            
            # Check for AND/OR rules
            and_result = True
            or_result = True
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
    
    if month_diff <= min_accnt_age:
        return str(month_diff) + " months old"
    else:
        return None


def check_activity(user, sub, target_sub, option, sub_group):
    target_value = int(option["value"])
    metric = option["metric"]
    comparison = option["comparison"]
    
    sub_list = []
    target_abbrev = sub_group[target_sub]
    for sub_name, abbrev in sub_group.items():
        if abbrev == target_abbrev:
            sub_list.append(sub_name)
            
    user_value = get_user_value(metric, sub_list, user, sub)
    activity_result = check_value(user_value, comparison, target_value)
    
    return [activity_result, user_value]


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


def concat_flair(prog_flair, new_accnt_flair, activity_flair):
    flair_txt = ""
    for flair in [prog_flair, new_accnt_flair, activity_flair]:
        if flair is not None:
            if flair_txt == "":
                flair_txt += flair
            else:
                flair_txt += " | " + flair
    return flair_txt


def check_value(user_value, comparison, value):
    if comparison == ">":
        return user_value > value
    if comparison == "<":
        return user_value > value
    if comparison == ">=":
        return user_value >= value
    if comparison == "<=":
        return user_value <= value
    

