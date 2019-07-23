import time
from ActivityFlair import ActivityFlair as af
from ProgFlair import ProgFlair as pf


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
        prog_data = pf.make_prog_flair(user, sub)
        prog_flair = prog_data[0]
        css = prog_data[1]
        if prog_data[2] != "None":
            permissions.append(prog_data[2])
            
    # New Account Flair
    if new_accnt_flair_enabled:
        new_accnt_flair = make_new_accnt_flair(user, sub)
        
    # Activity Flair
    if activity_flair_enabled:
        activity_data = af.make_activity_flair(user, sub)
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



