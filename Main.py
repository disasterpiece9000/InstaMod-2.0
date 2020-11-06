import logging
import os
import shutil
import sqlite3
import threading
import time
import traceback
from os import path
from queue import Queue

import praw
import prawcore
from praw.models import Message

import MessageManager
import ProcessComment
from Subreddit import Subreddit
from praw.exceptions import APIException

r = praw.Reddit("InstaMod")  # PRAW Instance
sub_list = []  # List of subreddits
comment_queue = Queue()  # Queue for users to be analyzed
flair_queue = Queue()  # Queue for users to be flaired
perm_queue = Queue()  # Queue for notifying users of new permissions
lock = threading.Lock()  # Lock for shared resources
last_config_check = int(time.time())  # Store times for re-checking sub config

logging.basicConfig(filename="info.log",
                    filemode="w",
                    level=logging.INFO)


# Check inbox
def read_pms():
    for item in r.inbox.unread():
        if isinstance(item, Message):
            logging.info("Found a PM")
            try:
                MessageManager.process_pm(item, sub_list, flair_queue, perm_queue, r)
            except (prawcore.ServerError, prawcore.RequestException, prawcore.ResponseException):
                logging.warning("PM Rate Limit Error: Stopping PM responses and resuming scraping"
                                "\nStacktrace: " + str(traceback.print_exc()))
                time.sleep(60)
                break
        else:
            logging.info("Found a comment, marking as read")
            item.mark_read()
    logging.debug("Done with PMs")


# Create all subreddit objects and return multisub for comment stream
def get_multisub():
    multisub_str = ""
    # Read subreddit names from master list
    master_list = open("subreddit_master_list.txt", "r", )
    for sub_name in master_list:
        sub_name = sub_name.replace("\n", "")
        sub_list.append(Subreddit(sub_name, r))
        multisub_str += sub_name + "+"

    # Remove trailing '+'
    return r.subreddit(multisub_str[:-1])


# Handel daily, weekly, and monthly backups of database
def check_backup():
    cur_time = int(time.time())
    db_path = path.realpath("master_databank.db")  # Get path to database
    main_path, main_file = path.split(db_path)
    backup_path = main_path + "/Backups/"  # Get path to backup folder from database path

    # Parse all files in the Backups dir
    for root, dirs, files in os.walk(backup_path):
        # If .keep is the only file, create initial backup
        if len(files) == 1:
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

            return  # Don't need to check backups if they were just created

        for filename in files:
            if filename == ".keep":
                continue

            file_data = filename.split("-")
            time_diff = cur_time - int(file_data[1][:-7])  # Parse last backup time from file name
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

            if None not in [old_path, new_path, db_path]:
                os.remove(old_path)  # Remove old file
                shutil.copy(db_path, new_path)  # Copy source file to backup folder and rename
                shutil.copystat(db_path, new_path)  # Copy permissions from source to destination


# Process flair queue
def flair_users():
    logging.debug("Flairing users...")
    while not flair_queue.empty():
        flair_data = flair_queue.get()
        flair_queue.task_done()

        username = flair_data[0]
        flair_txt = flair_data[1]
        flair_css = flair_data[2]
        target_sub = flair_data[3]

        # Check if custom text/css perms were used
        if target_sub.db.fetch_sub_info(username, "custom text used") == 1:
            flair_txt = target_sub.db.fetch_sub_info(username, "flair text")
        if target_sub.db.fetch_sub_info(username, "custom css used") == 1:
            flair_css = next(target_sub.sub.flair(username))["flair_css_class"]

        # Check if flair data is null and should not be assigned
        if (flair_css is None or flair_css == '') \
                and \
                (flair_txt is None or flair_txt == '') \
                and \
                bool(target_sub.flair_config["no empty flair"]):

            logging.info("Flair results"
                         + "\n\tUser: " + str(username)
                         + "\n\t Flair: Null flair not applied due to no blank flair config")
            continue

        # Remove all spaces in flair text if it's too long
        if len(flair_txt) > 64:
            flair_txt = flair_txt.replace(" ", "")

        target_sub.sub.flair.set(username, flair_txt, flair_css)

        logging.info("Flair results"
                     + "\n\tUser: " + str(username)
                     + "\n\tFlair: " + str(flair_txt)
                     + "\n\tCSS: " + str(flair_css)
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
            auto_perm_msg = "Your contributions to /r/" + str(target_sub.sub) + \
                            " have granted you access to custom flair options. You will continue to receive " \
                            "automatic flair until you apply a custom flair. In order to apply your desired " \
                            "flair, please click on [this pre-formatted link.](https://www.reddit.com/message/" \
                            "compose?to=InstaMod&subject=!" + str(target_sub.sub) + "%20!flair" \
                            "&message=Flair%20Text:%0AFlair%20CSS:)" \
                            "\n\n**Note:** This link will not work on mobile and can be used to change your flair" \
                            " as many times as you want.\n\n"

            # Concatenate message body with custom text from subreddit settings
            body = auto_perm_msg + target_sub.pm_messages["custom flair body"] + message_footer
            subject = target_sub.pm_messages["custom flair subj"]

        elif new_perm == "css perm":
            auto_perm_msg = "Your contributions to /r/" + str(target_sub.sub) + " have granted you access to custom " \
                            "flair styling options. Your flair text will still be updated automatically. " \
                            "In order to apply your desired flair styling, please click on [this pre-formatted link.]" \
                            "(https://www.reddit.com/message/compose?to=InstaMod&subject=!" + str(target_sub.sub) + \
                            "%20!css&message=Flair%20CSS:)" \
                            "\n\n**Note:** This link will not work on mobile and can be used to change your flair" \
                            " styling as many times as you want.\n\n"

            body = auto_perm_msg + target_sub.pm_messages["custom css body"] + message_footer
            subject = target_sub.pm_messages["custom css subj"]

        elif new_perm == "text perm":
            auto_perm_msg = "Your contributions to /r/" + str(target_sub.sub) + " have granted you access to custom " \
                            "flair text. You will continue to receive automatic flair until you apply a custom flair." \
                            " In order to apply your desired flair text, please click on [this pre-formatted link.](" \
                            "https://www.reddit.com/message/compose?to=InstaMod&subject=!" + str(target_sub.sub) + \
                            "%20!text&message=Flair%20Text:)" \
                            "\n\n**Note:** This link will not work on mobile and it can be used to change your flair" \
                            " text as many times as you want.\n\n"

            body = auto_perm_msg + target_sub.pm_messages["custom text body"] + message_footer
            subject = target_sub.pm_messages["custom text subj"]

        user = r.redditor(username)

        try:
            user.message(subject, body)
        except APIException:
            logging.warning("PM Permissions Error: Skipping PM for user"
                            "\nStacktrace: " + str(traceback.print_exc()))
        except (prawcore.ServerError, prawcore.RequestException, prawcore.ResponseException):
            logging.warning("PM Rate Limit Error: Stopping PM permission notifications and resuming scraping"
                            "\nStacktrace: " + str(traceback.print_exc()))
            time.sleep(60)
            break

        logging.info("Permissions updated:"
                     "\n\tUser: " + username +
                     "\n\tType: " + new_perm +
                     "\n\tSub: " + target_sub.name +
                     "\n\tMessage Subj: " + subject +
                     "\n\tMessage Body: " + body + "\n")
    logging.debug("Done updating permissions")


def run_idle_tasks(last_check):
    flair_users()  # Process flair_queue
    notify_permission_change()  # Process perm_queue
    read_pms()  # Check for PM commands
    check_backup()  # Create a backup of database file every day/week/month

    # Re-read each subreddit's config file each hour
    current_time = int(time.time())
    if current_time - last_check > 3600:
        for sub in sub_list:
            try:
                sub.read_config()
            except sqlite3.OperationalError:
                logging.warning("Unable to update subreddit's config, database is locked")

        last_check = current_time
    return last_check


# Get multisub so that all subreddits can be searched simultaneously
all_subs = get_multisub()
# Run idle tasks once before beginning main loop
sub_list[0].db.drop_inactive_users()  # Clean-up db
run_idle_tasks(last_config_check)

# Create thread for processing comments
process_thread = threading.Thread(target=ProcessComment.fetch_queue,
                                  args=(comment_queue, flair_queue, perm_queue, sub_list))
process_thread.setDaemon(False)
process_thread.start()

while True:
    try:
        # Grab any comments made in subreddits using InstaMod
        for comment in all_subs.stream.comments(pause_after=0, skip_existing=True):
            # If no new comments are found after 3 checks do other stuff
            if comment is None:
                logging.debug("No new comments found")
                last_config_check = run_idle_tasks(last_config_check)
                continue

            comment_queue.put(comment)
            logging.info("Comment added to queue from " + str(comment.author))
            logging.info("Queue size: " + str(comment_queue.qsize()))

    except (prawcore.ServerError, prawcore.RequestException, prawcore.ResponseException):
        logging.warning("Server Error: Sleeping for 1 min"
                        "\nStacktrace: " + str(traceback.print_exc()))
        time.sleep(60)
        continue
