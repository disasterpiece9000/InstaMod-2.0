

def update_flair(r, user, sub, prog_flair_enabled, new_accnt_flair_enabled, activity_flair_enabled):
    prog_flair = ""
    new_accnt_flair = ""
    activity_flair = ""
    
    if prog_flair_enabled:
        prog_flair = make_prog_flair(user, sub)
    
def make_prog_flair(user, sub):
    prog_tiers = sub.progression_tiers
    flair_txt = ""
    
    tier_count = 1
    while True:
        tier_name = "PROGRESSION TIER " + str(tier_count)
        tier_count += 1
        
        if tier_name in prog_tiers:
            tier = prog_tiers[tier_name]
            main_result = user_in_tier(tier, user, sub)
            
def user_in_tier(tier, user, sub):
    metric = tier["metric"]
    target_subs = tier["target subs"]
    comparison = tier["comparison"]
    value = tier["value"]
    flair_text = tier["flair text"]
    flair_css = tier["flair css"]
    permissions = tier["permissions"]
    
    user_value = get_user_value(metric, target_subs, user, sub)
    

def get_user_value(metric, target_subs, user, sub):
    print(metric)
    username = str(user)
    user_value = 0
    sub_list = []
    
    if target_subs is not "ALL":
        sub_list = list(sub.sub_groups[target_subs].keys())
    else:
        sub_list = "ALL"
    
    if metric == "total comment karma":
        user_value = sub.db.get_total_comment_karma(username)
    elif metric == "total post karma":
        user_value = sub.db.get_total_post_karma(username)
    elif metric == "total karma":
        user_value = sub.db.get_total_comment_karma(username) + sub.db.get_total_post_karma(username)
    elif metric == "comment karma":
        user_value = sub.db.get_comment_karma(username, sub_list)