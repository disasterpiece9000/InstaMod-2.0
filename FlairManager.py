import time
from ActivityFlair import make_activity_flair
from ProgFlair import make_prog_flair


# Get new flair for all enabled options
def update_flair(flair_queue, perm_queue, user, sub, prog_flair_enabled,
                 new_accnt_flair_enabled, activity_flair_enabled):
    username = str(user).lower()
    prog_flair = None
    new_accnt_flair = None
    activity_flair = None
    css = ""
    flair_perm = False
    css_perm = False
    
    # Progression Flair
    if prog_flair_enabled:
        prog_data = make_prog_flair(user, sub)
        prog_flair = prog_data[0]
        css = prog_data[1]
        if prog_data[2]:
            flair_perm = True
        elif prog_data[3]:
            css_perm = True
            
    # New Account Flair
    if new_accnt_flair_enabled:
        new_accnt_flair = make_new_accnt_flair(username, sub)
        
    # Activity Flair
    if activity_flair_enabled:
        activity_data = make_activity_flair(user, sub)
        activity_flair = activity_data[0]
        if activity_data[1]:
            flair_perm = True
        elif activity_data[2]:
            css_perm = True
        
    # Check if the user's flair has been changed
    new_flair_txt = concat_flair(prog_flair, new_accnt_flair, activity_flair)
    old_flair_txt = sub.db.fetch_sub_info(username, "flair text")
    if new_flair_txt != old_flair_txt:
        sub.db.update_key_sub_info(username, "flair text", new_flair_txt)
        flair_queue.put([username, new_flair_txt, css, sub])

    # Check if the user has earned any new permissions
    old_flair_perm = sub.db.fetch_sub_info(username, "flair perm")
    old_css_perm = sub.db.fetch_sub_info(username, "css perm")
    
    if flair_perm and not old_flair_perm:
        sub.db.update_key_sub_info(username, "flair perm", int(flair_perm))
        perm_queue.put([username, "flair perm", sub])
    if css_perm and not old_css_perm:
        sub.db.update_key_sub_info(username, "flair perm", int(css_perm))
        perm_queue.put([username, "css perm", sub])


# Main method for new account flair
def make_new_accnt_flair(username, sub):
    min_accnt_age = int(sub.flair_config["young account age"])
    user_created = sub.db.fetch_accnt_info(username, "date created")
    current_time = int(time.time())
    # Convert seconds to months
    month_diff = int((current_time - user_created) / 2629746)
    
    if month_diff <= min_accnt_age:
        return str(month_diff) + " months old"
    else:
        return None


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
