import threading
import logging
import shutil
import os
import time
from os import path
import praw
from praw.models import Message
from queue import Queue
import prawcore

from Subreddit import Subreddit
import ProcessComment
import MessageManager

# PRAW Instance
r = praw.Reddit("InstaMod")
# List of subreddits
sub_list = []
# Queue for users to be analyzed
comment_queue = Queue()
# Queue for users to be flaired
flair_queue = Queue()
# Queue for notifying users of new permissions
perm_queue = Queue()
# Lock for shared resources
lock = threading.Lock()
# Logging
logging.basicConfig(filename="info.log", filemode="w", level=logging.INFO)
# Store times for re-checking sub config
last_config_check = int(time.time())


# Check inbox
def read_pms():
    logging.debug("Checking PMs...")
    for item in r.inbox.unread():
        if isinstance(item, Message):
            MessageManager.process_pm(item, sub_list, flair_queue, perm_queue, r)
    logging.debug("Done with PMs")


# Create all subreddit objects and return multisub for comment stream
def get_multisub():
    multisub_str = ""
    # Read subreddit names from master list
    master_list = open("subreddit_master_list.txt", "r", )
    for sub_name in master_list:
        sub_list.append(Subreddit(sub_name.strip(), r))
        multisub_str += sub_name + "+"
    
    # Remove trailing '+'
    return r.subreddit(multisub_str[:-1])


def check_backup():
    cur_time = int(time.time())
    db_path = path.realpath("master_databank.db")
    main_path, main_file = path.split(db_path)
    backup_path = main_path + "\\Backups\\"
    
    for root, dirs, files in os.walk("./Backups"):
        if len(files) == 0:
            # Initial daily backup
            first_daily_path = backup_path + "DAILY-" + str(cur_time) + ".db.bak"
            shutil.copy(db_path, first_daily_path)
            shutil.copystat(db_path, first_daily_path)
            # Initial weekly backup
            first_weekly_path = backup_path + "WEEKLY-" + str(cur_time) + ".db.bak"
            shutil.copy(db_path, first_weekly_path)
            shutil.copystat(db_path, first_weekly_path)
            # Initial monthly backup
            first_monthly_path = backup_path + "MONTHLY-" + str(cur_time) + ".db.bak"
            shutil.copy(db_path, first_monthly_path)
            shutil.copystat(db_path, first_monthly_path)
            return
            
        for filename in files:
            file_data = filename.split("-")
            time_diff = cur_time - int(file_data[1][:-7])
            old_path = None
            new_path = None
            
            if file_data[0] == "DAILY" and time_diff > 86400:
                old_path = backup_path + "DAILY-" + str(file_data[1])
                new_path = backup_path + "DAILY-" + str(cur_time) + ".db.bak"
            
            elif file_data[0] == "WEEKLY" and time_diff > 604800:
                old_path = backup_path + "WEEKLY-" + str(file_data[1])
                new_path = backup_path + "WEEKLY-" + str(cur_time) + ".db.bak"
                
            elif file_data[0] == "MONTHLY" and time_diff > 2592000:
                old_path = backup_path + "MONTHLY-" + str(file_data[1])
                new_path = backup_path + "MONTHLY-" + str(cur_time) + ".db.bak"

            os.remove(old_path)                 # Remove old file
            shutil.copy(db_path, new_path)      # Copy source file to backup folder and rename
            shutil.copystat(db_path, new_path)  # Copy permissions from source to destination


# Process flair queue
def flair_users():
    logging.debug("Flairing users...")
    while not flair_queue.empty():
        flair_data = flair_queue.get()
        flair_queue.task_done()
        
        username = flair_data[0]
        flair_txt = flair_data[1] if flair_data[1] else ""
        flair_css = flair_data[2] if flair_data[2] else ""
        target_sub = flair_data[3]
        
        # TODO: Figure out why target_sub.name returns None
        
        logging.info("Flair results"
                     + "\n\tUser: " + username
                     + "\n\tFlair: " + flair_txt
                     + "\n\tCSS: " + flair_css
                     + "\n\tSub: " + target_sub.name + "\n")
    logging.debug("Done flairing users")


# Process permission queue
def notify_permission_change():
    logging.debug("Updating permissions...")
    while not perm_queue.empty():
        perm_data = perm_queue.get()
        perm_queue.task_done()
        
        # Footer for automated PMs
        message_footer = ("\n\n-----\n\nThis is an automated message. "
                          "Please contact /u/shimmyjimmy97 with any questions, comments, or issues that you have.")
        
        username = perm_data[0]
        new_perm = perm_data[1]
        target_sub = perm_data[2]
        
        # Get PM subject text from subreddit settings
        subject = None
        body = None
        
        # Notify user of flair perm via PM
        if new_perm == "flair perm":
            auto_perm_msg = "Your contributions to /r/" + target_sub.name + \
                            " have granted you access to custom flair options. You will continue to receive " \
                            "automatic flair until you apply a custom flair. In order to apply your desired " \
                            "flair, please click on [this pre-formatted link.](https://www.reddit.com/message" \
                            "/compose?to=InstaMod&subject=!" + target_sub.name + "%20!flair&message=REPLACE" \
                            "%20THIS%20WITH%20DESIRED%20FLAIR%20TEXT%0A%0AREPLACE%20THIS%20WITH%20DESIRED" \
                            "%20FLAIR%20ICON%20OR%20DELETE%20FOR%20NONE)" \
                            "\n\n**Note:** This link will not work on mobile and it can be used to change your flair" \
                            " as many times as you want.\n\n"
            
            # Concatenate message body with custom text from subreddit settings
            body = auto_perm_msg + target_sub.pm_messages["custom flair body"] + message_footer
            subject = target_sub.pm_messages["custom flair subj"]
        
        elif new_perm == "css perm":
            auto_perm_msg = "Your contributions to /r/" + target_sub.name + " have granted you access to custom " \
                            "flair icons. Your flair will still be updated automatically. " \
                            "In order to apply your desired flair icon, please click on [this pre-formatted link.](" \
                            "https://www.reddit.com/message/compose?to=InstaMod&subject=!" + target_sub.name + \
                            "CryptoMarkets%20!flair&message=REPLACE%20THIS%20WITH%20DESIRED%20FLAIR%20TEXT" \
                            "%0A%0AREPLACE%20THIS%20WITH%20DESIRED%20FLAIR%20ICON%20OR%20DELETE%20FOR%20NONE)" \
                            "\n\n**Note:** This link will not work on mobile and it can be used to change your flair" \
                            " icon as many times as you want.\n\n"
            
            body = auto_perm_msg + target_sub.pm_messages["custom css body"] + message_footer
            subject = target_sub.pm_messages["custom css subj"]
        
        logging.info("Permissions updated:"
                     "\n\tUser: " + username +
                     "\n\tType: " + new_perm +
                     "\n\tSub: " + target_sub.name +
                     "\n\tMessage Subj: " + subject +
                     "\n\tMessage Body: " + body + "\n")
    logging.debug("Done updating permissions")


# Get multisub
all_subs = get_multisub()

# Create thread for processing comments
process_thread = threading.Thread(target=ProcessComment.fetch_queue,
                                  args=(comment_queue, flair_queue, perm_queue, sub_list, r))
process_thread.setDaemon(False)
process_thread.start()

while True:
    try:
        # Grab any comments made in subreddits using InstaMod
        for comment in all_subs.stream.comments(pause_after=3, skip_existing=False):
            # If no new comments are found after 3 checks do other stuff
            if comment is None:
                logging.debug("No new comments found")
                flair_users()
                notify_permission_change()
                read_pms()
                
                # Re-read each subreddit's config file each hour
                current_time = int(time.time())
                if current_time - last_config_check < 3600:
                    for sub in sub_list:
                        sub.read_config()
                    last_config_check = current_time
                    
                    # Create a backup of database file every day/week/month
                    check_backup()
                
                continue
            comment_queue.put(comment)
            logging.info("Comment added to queue from " + str(comment.author))
    except prawcore.ServerError:
        logging.warning("Server Error: Sleeping for 1 min")
        time.sleep(60)
        continue
