import DataCollector
import FlairManager
import prawcore
import time


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

        # Check if the user data should be updated
        check_data = check_user(user, target_sub)
        skip = check_data[0]
        update = check_data[1]
        if skip:
            print("User was skipped: " + str(user))
            continue
            
        # Process comment and check if flair needs to be updated
        print("Collecting data...")
        try:
            DataCollector.load_data(update, comment, target_sub)
        except (prawcore.NotFound, prawcore.RequestException) as e:
            print("\nError in DataCollector: \n" + str(e) + "\n")
            continue
        print("Done collecting data")
        
        # Read flair toggles from sub config
        prog_flair_enabled = target_sub.main_config.getboolean("progression tier")
        new_accnt_flair_enabled = target_sub.main_config.getboolean("young account tag")
        activity_flair_enabled = target_sub.main_config.getboolean("activity tag")
        
        # If at least one flair toggle is enabled, update user flair
        if prog_flair_enabled or new_accnt_flair_enabled or activity_flair_enabled:
            print("Updating flair...")
            FlairManager.update_flair(flair_queue, perm_queue, comment.author, target_sub, prog_flair_enabled,
                                      new_accnt_flair_enabled, activity_flair_enabled)
        else:
            print("All flair settings disabled")


# Check if user should be skipped and if their data needs to be updated or inserted
def check_user(user, target_sub):
    # Turn comma delimited string into a list of whitelisted usernames
    whitelist = target_sub.flair_config["user whitelist"].replace(" ", "").split(",")
    username = str(user)
    skip = False
    update = False

    # Check if user is a mod or whitelisted
    if user in target_sub.mods or username in whitelist:
        skip = True
        update = False

    # Check if the user has previously had data scraped
    elif target_sub.db.exists_in_db(username):
        # Get user permissions
        permissions = target_sub.db.fetch_info_table(str(user), "permissions")
        if permissions == "custom flair":
            skip = True
            update = True

        # Check if user data is expired
        last_seen = target_sub.db.fetch_info_table(username, "last scraped")
        current_time = int(time.time())
        day_diff = int((current_time - last_seen) / 86400)
        if day_diff >= target_sub.flair_config.getint("flair expiration"):
            skip = False
            update = True
        else:
            skip = True
            update = True

    # All user data needs to be pulled
    else:
        skip = False
        update = False

    return [skip, update]
