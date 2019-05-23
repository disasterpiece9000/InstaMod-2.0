

# Get new flair for all enabled options
def update_flair(r, user, sub, prog_flair_enabled, new_accnt_flair_enabled, activity_flair_enabled):
    prog_flair = None
    new_accnt_flair = None
    activity_flair = None
    
    if prog_flair_enabled:
        prog_flair = make_prog_flair(user, sub)


# Get progression tier flair
def make_prog_flair(user, sub):
    prog_tiers = sub.progression_tiers
    flair_txt = ""
    
    # Loop through tiers in order
    tier_count = 1
    while True:
        tier_name = "PROGRESSION TIER " + str(tier_count)
        tier_count += 1
        
        if tier_name in prog_tiers:
            tier = prog_tiers[tier_name]
            main_result = user_in_tier(tier, user, sub)
  

# Check if the user belongs in the given tier
def user_in_tier(tier, user, sub):
    metric = tier["metric"]
    target_subs = tier["target subs"]
    comparison = tier["comparison"]
    value = tier["value"]
    flair_text = tier["flair text"]
    flair_css = tier["flair css"]
    permissions = tier["permissions"]
    
    user_value = get_user_value(metric, target_subs, user, sub)
    

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
