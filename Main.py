import praw
from queue import Queue
import threading
import os
import time

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
# Footer for automated PMs
message_footer = ("\n\n-----\n\nThis is an automated message. "
                  "Please contact /u/shimmyjimmy97 with any questions, comments, or issues that you have.")


def read_pms():
    for message in r.inbox.messages():
        if not message.was_comment:
            MessageManager.process_pm(message, sub_list)


# Create all subreddit objects and return multisub for comment stream
def get_multisub():
    # Get all folder names (subreddit names)
    folder_names = [name for name in os.listdir(".")
                    if name.startswith("r-") and os.path.isdir(name)]
    
    # Create subreddit objects and multisub
    multisub_str = ""
    for folder_name in folder_names:
        sub_name = folder_name[2:]
        sub_list.append(Subreddit(folder_name, r))
        multisub_str += sub_name + "+"
        
    return r.subreddit(multisub_str[:-1])
        

def flair_users():
    while not flair_queue.empty():
        flair_data = flair_queue.get()
        flair_queue.task_done()
        
        username = flair_data[0]
        flair_txt = flair_data[1]
        flair_css = flair_data[2]

        print("Flair results..."
              + "\n\tUser: " + username
              + "\n\tFlair: " + flair_txt
              + "\n\tCSS: " + flair_css + "\n")
        

def notify_permission_change():
    while not perm_queue.empty():
        perm_data = perm_queue.get()
        perm_queue.task_done()
        
        username = perm_data[0]
        new_perm = perm_data[1]
        target_sub = perm_data[2]
        
        # Get PM subject text from subreddit settings
        subject = None
        body = None
        
        # Notify user of flair perm via PM
        if new_perm == "flair perm":
            auto_perm_msg = "Your contributions to /r/" + target_sub.name + " have granted you access to custom flair "\
                            "options. You will continue to receive automatic flair until you apply a custom flair. " \
                            "In order to apply your desired flair, please click on [this preformatted link.](" \
                            "https://www.reddit.com/message/compose?to=InstaMod&subject=!CryptoMarkets%20!flair&" \
                            "message=REPLACE%20THIS%20WITH%20DESIRED%20FLAIR%20TEXT%0A%0AREPLACE%20THIS%20WITH%20" \
                            "DESIRED%20FLAIR%20ICON%20OR%20DELETE%20FOR%20NONE)" \
                            "\n\n**Note:** This link will not work on mobile and it can be used to change your flair" \
                            " as many times as you want.\n\n"

            # Concatenate message body with custom text from subreddit settings
            body = auto_perm_msg + target_sub.pm_messages["custom flair body"] + message_footer
            subject = target_sub.pm_messages["custom flair subj"]
        
        # Notify user of css perm via PM
        elif new_perm == "css perm":
            auto_perm_msg = "Your contributions to /r/" + target_sub.name + " have granted you access to custom flair "\
                            "icons. Your flair will still be updated automatically. " \
                            "In order to apply your desired flair icon, please click on [this preformatted link.](" \
                            "https://www.reddit.com/message/compose?to=InstaMod&subject=!CryptoMarkets%20!flair&" \
                            "message=REPLACE%20THIS%20WITH%20DESIRED%20FLAIR%20TEXT%0A%0AREPLACE%20THIS%20WITH%20" \
                            "DESIRED%20FLAIR%20ICON%20OR%20DELETE%20FOR%20NONE)" \
                            "\n\n**Note:** This link will not work on mobile and it can be used to change your flair" \
                            " icon as many times as you want.\n\n"
            
            body = auto_perm_msg + target_sub.pm_messages["custom css body"] + message_footer
            subject = target_sub.pm_messages["custom css subj"]
            
        print("Permissions updated:\n"
              "\tUser: " + username +
              "\tType: " + new_perm +
              "\tSub: " + target_sub.name +
              "\t Message Subj: " + subject +
              "\t Message Body: " + body)


# Main Method
all_subs = get_multisub()
# Child thread for processing comments
process_thread = threading.Thread(target=ProcessComment.fetch_queue,
                                  args=(comment_queue, flair_queue, perm_queue, sub_list))
process_thread.setDaemon(True)
process_thread.start()

while True:
    try:
        for comment in all_subs.stream.comments(pause_after=1, skip_existing=False):
            if comment is None:
                flair_users()
                notify_permission_change()
                #read_pms()
                continue
            comment_queue.put(comment)
    except Exception as e:
        print("Error: " + str(e) + "\nSleeping for 1 min")
        time.sleep(60)
