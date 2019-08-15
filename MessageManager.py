# TODO: Implement PM Messages and PM Commands section in config file

# TODO: Handle the appended "Re:" from PM replies
import DataCollector

message_footer = ("\n\n-----\n\nThis is an automated message. "
                  "Please contact /u/shimmyjimmy97 with any questions, comments, or issues that you have.")


def process_pm(message, sub_list):
    author = message.author
    author_name = str(author)
    message_subj = message.subject.lower()
    
    # Trim "Re:" from PM reply
    if message_subj.startswith("re:"):
        message_subj = message_subj[3:]
    message_subj = message_subj.split()
    
    # Return if the PM's subject does not contain the sub name and command
    if len(message_subj) != 2:
        message.reply("This message's subject is not in the correct format and cannot be processed."
                      "Each PM command's subject must contain these parameters:\n\n"
                      "     !SubredditName !command" +
                      message_footer)
        message.mark_read()
        return
    
    # Get the subreddit the PM is in reference to
    sub_name = message_subj[0][1:].lower()
    command = message_subj[1].lower()
    target_sub = None
    for sub in sub_list:
        if sub.name == sub_name:
            target_sub = sub
            break
    
    # Return if the subreddit mentioned is not correct
    if target_sub is None:
        message.reply("The specified subreddit is not valid" + message_footer)
        message.mark_read()
        return
    
    if command == "!flair":
        flair_pm(message, target_sub)
    
    if command == "!noautoflair" and check_if_mod(author_name, target_sub, message):
        remove_auto_flair(message, target_sub)
        
    if command == "!giveflairperm" and check_if_mod(author_name, target_sub, message):
        give_flair_perm(message, target_sub)
        
    if command == "!updatesettings" and check_if_mod(author_name, target_sub, message):
        target_sub.read_config()
        
    # TODO: Consider adding a confirmation step to prevent accidental data loss
    if command == "!wipe" and check_if_mod(author, target_sub, message):
        target_sub.db.wipe_sub_info()


# Check if the user is a mod in the target_sub
def check_if_mod(author_name, target_sub, message):
    if author_name not in [str(mod).lower() for mod in target_sub.mods]:
        message.reply("This PM command is restricted to moderators only" + message_footer)
        message.mark_read()
        return False
    else:
        return True


# Check if the target user exists in the database
def user_in_db(username, target_sub, message):
    if not target_sub.db.exists_in_db(username):
        message.reply("This user has no entry in the database and cannot be modified. "
                      "To fix this, you can use the !updatethem PM command and then try again."
                      + message_footer)
        message.mark_read()
        return False
    else:
        return True


# Handle custom flair requests
def flair_pm(message, target_sub):
    user = message.author
    username = str(user)
    message_lines = message.body.splitlines()
    
    # Return if the user is not in the database
    in_db = user_in_db(username, target_sub, message)
    if not in_db:
        return

    # Return if the user doesn't have proper permissions
    flair_perm = target_sub.db.fetch_sub_info(username, "flair perm") == 1
    if not flair_perm:
        message.reply("You have not met the requirements for custom flair. You will be notified via a PM"
                      "from /u/InstaMod once your account is eligible." + message_footer)
        message.mark_read()
        return
    
    # Pull flair and css data from PM text
    flair_txt = message_lines[0][11:]
    if len(message_lines) == 2:
        flair_css = message_lines[1][10:]
    elif len(message_lines) == 3:
        flair_css = message_lines[2][10:]
    else:
        flair_css = ""
    
    # Set the flair and notify the user
    target_sub.sub.flair.set(username, flair_txt, flair_css)
    target_sub.db.update_key_sub_info(username, "custom flair used", 1)
    message.reply("Your flair has been set!\n\n"
                  "Flair Text: " + flair_txt + "\n\n"
                                               "Flair CSS:" + flair_css +
                  message_footer)
    message.mark_read()


# Prevents a user from having flair assigned by InstaMod
def remove_auto_flair(message, target_sub):
    target_username = message.body.lower()
    # Return if the user doesn't exist in the database
    in_db = user_in_db(target_username, target_sub, message)
    if not in_db:
        return
    
    target_sub.db.update_key_sub_info(target_username, "no auto flair", 1)
    message.reply("The user " + target_username + " will no longer receive flair from InstaMod. " +
                  "Their user data will continue to be updated." + message_footer)
    message.mark_read()


# Grant a user the ability to assign themselves custom flair
def give_flair_perm(message, target_sub):
    target_username = message.body.lower()
    # Return if the user doesn't exist in the database
    in_db = user_in_db(target_username, target_sub, message)
    if not in_db:
        return
    
    target_sub.db.update_key_sub_info(target_username, "flair perm", 1)
    message.reply("The user " + target_username + " has been granted custom flair permissions and will be notified."
                  + message_footer)
    message.mark_read()
