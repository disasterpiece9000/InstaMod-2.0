import time


# Get new flair for all enabled options
def update_flair(flair_queue, perm_queue, user, sub, prog_flair_enabled,
                 new_accnt_flair_enabled, activity_flair_enabled):
    username = str(user)
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
        activity_flair = activity_data[0]
        permissions.append(activity_data[1])
        
    # Check if the user's flair has been changed
    new_flair_txt = concat_flair(prog_flair, new_accnt_flair, activity_flair)
    old_flair_txt = sub.db.fetch_info_table(username, "flair text")
    if new_flair_txt != old_flair_txt:
        sub.db.update_flair(username, new_flair_txt)
        flair_queue.put([username, new_flair_txt, css])

    # Check if the user has earned any new permissions
    old_permission = sub.db.fetch_info_table(username, "permissions")
    new_permission = None
    if len(permissions) > 0 and old_permission != "CUSTOM FLAIR":
        if "CUSTOM FLAIR" in permissions:
            new_permission = "CUSTOM FLAIR"
        elif "FLAIR CSS" in permissions:
            new_permission = "FLAIR CSS"
    
    if new_permission is not None and old_permission != new_permission:
        sub.db.update_perm(username, new_permission)
        perm_queue.put([username, new_permission])
     

# Activity flair main method
def make_activity_flair(user, sub):
    activity_options = sub.sub_activity
    flair_text = []
    permissions = []
    
    # Loop through options in order
    option_count = 1
    while True:
        option_name = "ACTIVITY TAG " + str(option_count)
        option_count += 1
        
        if option_name in activity_options:
            main_option = activity_options[option_name]
            sub_group_name = main_option["target subs"]
            group_subs = main_option.getboolean("group subs")

            # TODO: Rework method so that AND/OR is always checked
            if "-" in sub_group_name:
                # Get abbreviation from string
                dash_index = sub_group_name.find("-")
                target_abbrev = sub_group_name[dash_index + 1:].strip()
                sub_group = sub.sub_groups[sub_group_name[:dash_index].strip()]
                sub_list = [name for name, abbrev in sub_group.itema() if abbrev == target_abbrev]
                
            # Subs are treated as a group
            if group_subs:
                sub_group = sub.sub_groups[sub_group_name]
                sub_list = list(sub_group.keys())
                # Get cumulative user value
                user_value = get_user_value(main_option["metric"], sub_list, user, sub)
                target_value = main_option.getint("target value")
                comparison = main_option["comparison"]
                
                if not check_value(user_value, comparison, target_value):
                    continue

                # TODO: Rework method so that AND/OR is always checked
                
                # Append flair
                pre_text = main_option["pre text"]
                post_text = main_option["post text"]
                display_value = main_option.getboolean("display value")
                full_text = pre_text + " " + post_text
                
                if display_value:
                    full_text += " " + str(user_value)

                flair_text.append(full_text)
                new_permissions = main_option["permissions"]
                if new_permissions != "":
                    permissions.append(new_permissions)
            
            # Subs are treated as individuals
            else:
                sub_group = sub.sub_groups[sub_group_name]
                abbrev_list = list(set(sub_group.values()))
                for abbrev in abbrev_list:
                    main_data = check_activity(user, sub, abbrev, main_option, sub_group)
                    main_result = main_data[0]
                    main_value = main_data[1]
                    
                    # If the first result is False then move to next tag
                    if not main_result:
                        continue
                    
                    # Check for AND/OR rules
                    and_result = True
                    or_result = True
                    option_name_and = option_name + " - AND"
                    option_name_or = option_name + " - OR"
                    
                    if option_name_and in activity_options:
                        and_option = activity_options[option_name_and]
                        and_data = check_activity(user, sub, abbrev, and_option, sub_group)[0]
                        and_result = and_data[0]
                        and_value = and_data[1]
                        
                    elif option_name_or in activity_options:
                        or_option = activity_options[option_name_or]
                        or_data = check_activity(user, sub, abbrev, or_option, sub_group)[0]
                        or_result = or_data[0]
                        or_value = or_data[1]
                        
                    if main_result and and_result and or_result:
                        # Append flair
                        pre_text = main_option["pre text"]
                        post_text = main_option["post text"]
                        display_value = main_option.getboolean("display value")
                        
                        full_text = pre_text + " " + abbrev + " " + post_text
                        if display_value:
                            full_text += " " + str(main_value)
                        flair_text.append(full_text)
                        
                        new_permissions = main_option["permissions"]
                        if new_permissions != "None":
                            permissions.append(new_permissions)
        # Last tag discovered
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


# Main method for new account flair
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


# Get user value from a specific sub (and subs that share the same abbreviation)
def check_activity(user, sub, target_abbrev, option, sub_group):
    target_value = int(option["target value"])
    metric = option["metric"]
    comparison = option["comparison"]
    
    # Get subreddits that have the same abbreviation
    sub_list = []
    for sub_name, abbrev in sub_group.items():
        if abbrev == target_abbrev:
            sub_list.append(sub_name)
            
    user_value = get_user_value(metric, sub_list, user, sub)
    activity_result = check_value(user_value, comparison, target_value)
    
    return [activity_result, user_value]


# Check if the user belongs in the given tier
def user_in_tier(tier, user, sub):
    target_subs = tier["target subs"]
    # If an abbreviation is specified make a list of all subs with a matching abbreviation
    if "-" in target_subs:
        # Get abbreviation from string
        target_abbrev = target_subs[target_subs.find("-") + 1:].strip()
        sub_group = sub.sub_groups[target_subs[:target_subs.find("-")].strip()]
        sub_list = []
        for sub_name, abbrev in sub_group.items():
            if abbrev == target_abbrev:
                sub_list.append(sub_name)
                
    # Turn Sub Group into list if all subs option not selected
    elif target_subs != "ALL":
        sub_list = list(sub.sub_groups[target_subs].keys())
        
    else:
        sub_list = "ALL"
        
    metric = tier["metric"]
    comparison = tier["comparison"]
    value = int(tier["target value"])
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


# Concatenate flair text into a single formatted string
def concat_flair(prog_flair, new_accnt_flair, activity_flair):
    flair_txt = ""
    if prog_flair is not None:
        flair_txt += prog_flair
    if new_accnt_flair is not None:
        if flair_txt == "":
            flair_txt += new_accnt_flair
        else:
            flair_txt += " | " + new_accnt_flair
    
    if activity_flair is not None and len(activity_flair) > 0:
        if flair_txt != "":
            flair_txt += " | "
        for hold_flair in activity_flair:
            flair_txt += hold_flair + " "
    
    return flair_txt


# Check if the users value meets the requirements (target value and comparison)
def check_value(user_value, comparison, value):
    if comparison == ">":
        return user_value > value
    if comparison == "<":
        return user_value > value
    if comparison == ">=":
        return user_value >= value
    if comparison == "<=":
        return user_value <= value
