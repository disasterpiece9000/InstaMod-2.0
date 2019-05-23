import DataCollector
import FlairManager
import prawcore

# Get new comments as they are added to the queue by the producer thread
def fetch_queue(r, q, lock, sub_list):
    # Load databases
    for sub in sub_list:
        sub.make_db()
        
    # Loop continuously checking for new comments
    while True:
        comment = q.get()
        q.task_done()
        
        # Find sub that the comment was placed in
        target_sub = None
        comment_sub = str(comment.subreddit).lower()
        for sub in sub_list:
            if sub.sub_name.lower() == comment_sub:
                target_sub = sub
                break

        # Process comment and check if flair needs to be updated
        update_flair = False
        if target_sub is not None:
            try:
                update_flair = DataCollector.get_data(comment, target_sub)
            except (prawcore.NotFound, prawcore.RequestException):
                continue
        
        # Read flair toggles from sub config
        prog_flair_enabled = str2bool(target_sub.main_config["progression flair"])
        new_accnt_flair_enabled = str2bool(target_sub.main_config["young account tag"])
        activity_flair_enabled = str2bool(target_sub.main_config["sub activity"])
        
        # If user flair is expired and at least one toggle is enabled, update user flair
        if update_flair and (prog_flair_enabled
                             or new_accnt_flair_enabled
                             or activity_flair_enabled):
            
            FlairManager.update_flair(r, comment.author, target_sub, prog_flair_enabled,
                                      new_accnt_flair_enabled, activity_flair_enabled)


def str2bool(txt):
    return txt.lower() in ("yes", "true", "t", "1")
