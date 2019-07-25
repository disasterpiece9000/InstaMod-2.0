import DataCollector
import FlairManager
import prawcore


# Get new comments as they are added to the queue by the producer thread
def fetch_queue(comment_queue, flair_queue, perm_queue, sub_list):
    # Loop continuously checking for new comments
    while True:
        comment = comment_queue.get()
        comment_queue.task_done()
        user = comment.author
        
        # Find sub that the comment was placed in
        target_sub = None
        comment_sub = str(comment.subreddit).lower()
        for sub in sub_list:
            if sub.name.lower() == comment_sub:
                target_sub = sub
                break
        if target_sub is None:
            print("Target sub not found"
                  "\nSubreddit: " + comment_sub)
            continue
            
        if skip_user(user, target_sub):
            continue
            
        # Process comment and check if flair needs to be updated
        print("Collecting data...")
        try:
            update_flair = DataCollector.get_data(comment, target_sub)
        except (prawcore.NotFound, prawcore.RequestException) as e:
            print("\nError in DataCollector: \n" + e + "\n")
            continue
        print("Done collecting data")
        
        # Read flair toggles from sub config
        prog_flair_enabled = target_sub.main_config.getboolean("progression tier")
        new_accnt_flair_enabled = target_sub.main_config.getboolean("young account tag")
        activity_flair_enabled = target_sub.main_config.getboolean("activity tag")
        
        # If user flair is expired and at least one toggle is enabled, update user flair
        if update_flair and (prog_flair_enabled
                             or new_accnt_flair_enabled
                             or activity_flair_enabled):
            print("Updating flair...")
            FlairManager.update_flair(flair_queue, perm_queue, comment.author, target_sub, prog_flair_enabled,
                                      new_accnt_flair_enabled, activity_flair_enabled)
        else:
            print("All flair settings disabled")


def skip_user(user, target_sub):
    username = str(user)
    if user not in target_sub.mods and username not in target_sub.flair_config["user whitelist"]:
        return False
    else:
        return True
