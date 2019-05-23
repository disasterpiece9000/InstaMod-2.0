

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
        permissions.append(prog_data[2])
        

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


# Check if the user belongs in the given tier
def user_in_tier(tier, user, sub):
    metric = tier["metric"]
    target_subs = tier["target subs"]
    comparison = tier["comparison"]
    value = tier["value"]
    user_value = get_user_value(metric, target_subs, user, sub)
    
    return check_value(user_value, comparison, value)
    

# Fetch the user_value from the database
def get_user_value(metric, target_subs, user, sub):
    print(metric)
    username = str(user)
    user_value = 0
    
    # Make list of subs from the specified group
    if target_subs is not "ALL":
        sub_list = list(sub.sub_groups[target_subs].keys())
    # Otherwise select data from all subreddits
    else:
        sub_list = "ALL"
    
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
