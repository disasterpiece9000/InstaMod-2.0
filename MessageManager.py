import logging
import traceback
import configparser

import prawcore
from praw import exceptions
from psaw import PushshiftAPI

import DataCollector
import FlairManager
import ProcessComment

praw_config = configparser.ConfigParser()
praw_config.read("praw.ini")
message_footer = ("\n\n-----\n\nThis is an automated message. Please contact /u/" + praw_config["Bot Info"]["bot_owner"]
                  + "  with any questions, comments, or issues that you have.")


# Main method for responding to PM commands
def process_pm(message, sub_list, flair_queue, perm_queue, r):
    author = message.author
    author_name = str(author)
    message_subj = message.subject.lower()

    # Trim "Re:" from PM reply
    if message_subj.startswith("re:"):
        message_subj = message_subj[3:]
    message_subj = message_subj.split()

    # Return if the PM's subject does not contain the sub name and command
    if len(message_subj) != 2:
        message.reply("This message's subject is not in the correct format and cannot be processed. "
                      "Each PM command's subject must contain these parameters:\n\n"
                      "     !SubredditName !Command" + message_footer)
        message.mark_read()
        logging.info("PM Format Error: Message subject didn't have 2 parameters")
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
        logging.info("PM Format Error: Target subreddit does not exist")
        return

    if command == "!flair":
        flair_pm(message, target_sub, r)

    if command == "!text":
        text_pm(message, target_sub, r)

    if command == "!css":
        css_pm(message, target_sub, r)

    elif command == "!noautoflair":
        if not check_if_mod(author_name, target_sub):
            message.reply("This PM command is restricted to moderators only" + message_footer)
            message.mark_read()
            logging.info("PM Privileges Error: User " + author_name + " tried to use !noautoflair "
                                                                      "but is not a moderator of " + target_sub.name)
            return

        target_user = get_user(message.body, r)
        if target_user is None:
            message.reply("The user " + message.body + " does not exist" + message_footer)
            message.mark_read()
            return
        remove_auto_flair(message, target_sub, r)

    elif command == "!giveflairperm":
        if not check_if_mod(author_name, target_sub):
            message.reply("This PM command is restricted to moderators only" + message_footer)
            message.mark_read()
            logging.info("PM Privileges Error: User " + author_name + " tried to use !giveflairperm "
                                                                      "but is not a moderator of " + target_sub.name)
            return

        target_user = get_user(message.body, r)
        if target_user is None:
            message.reply("The user " + message.body + " does not exist" + message_footer)
            message.mark_read()
            return

        give_flair_perm(message, target_sub, perm_queue, r)

    elif command == "!updatesettings":
        if not check_if_mod(author_name, target_sub):
            message.reply("This PM command is restricted to moderators only" + message_footer)
            message.mark_read()
            logging.info("PM Privileges Error: User " + author_name + " tried to use !updatesettings "
                         "but is not a moderator of " + target_sub.name)
            return

        target_sub.read_config()
        message.reply("The settings have been updated" + message_footer)
        message.mark_read()

    elif command == "!updatethem":
        if not check_if_mod(author_name, target_sub):
            message.reply("This PM command is restricted to moderators only" + message_footer)
            message.mark_read()
            logging.info("PM Privileges Error: User " + author_name + " tried to use !updatethem "
                                                                      "but is not a moderator of " + target_sub.name)
            return

        # Get user from username and verify that they exist
        target_user = get_user(message.body, r)
        if target_user is None:
            message.reply("The user " + message.body + " does not exist" + message_footer)
            message.mark_read()
            return

        update_user(target_user, target_sub, r, flair_queue, perm_queue, sub_list)
        message.reply("The user " + str(target_user) + " has had their data and flair queued for update."
                      + message_footer)
        message.mark_read()

    elif command == "!updateme":
        update_user(message.author, target_sub, r, flair_queue, perm_queue, sub_list)
        message.reply("Your data and flair have been queued for updating. "
                      "This process may not be instantaneous so please be patient." + message_footer)
        message.mark_read()

    elif command == "!wipe":
        if not check_if_mod(author, target_sub):
            message.reply("This PM command is restricted to moderators only" + message_footer)
            message.mark_read()
            logging.info("PM Privileges Error: User " + author_name + " tried to use !wipe "
                                                                      "but is not a moderator of " + target_sub.name)
            return

        target_sub.db.wipe_sub_info()
        message.mark_read()
        message.reply("The subreddit's data has been wiped" + message_footer)


# Check if the user is a mod in the target_sub
def check_if_mod(author_name, target_sub):
    logging.info("PM Info: Checking if " + author_name + " is a mod in " + target_sub.name)
    if author_name.lower() not in [str(mod).lower() for mod in target_sub.mods]:
        return False
    else:
        return True


# Check if the target user exists in the database
def user_in_db(username, target_sub):
    if not target_sub.db.exists_in_sub_info(username):
        logging.info("PM Warning: User " + username + " does not exist in the database and has been notified")
        return False
    else:
        return True


def get_user(username, r):
    user = r.redditor(username)
    try:
        user.created
    except prawcore.NotFound:
        logging.warning("PM Warning: User " + username + " does not exist")
        return None
    return user


# Handle !updatethem and !updateme
def update_user(target_user, target_sub, r, flair_queue, perm_queue, sub_list):
    # Check existing data
    check_data = ProcessComment.check_user(target_user, target_sub)
    update_flair = True
    user_in_accnt_info = check_data[2]  # Does the user's data need to be updated or inserted
    user_in_sub_info = check_data[3]

    # Collect new data
    try:
        # PushShift Instance
        ps = PushshiftAPI(r)
        DataCollector.load_data(user_in_accnt_info, user_in_sub_info, update_flair,
                                target_user, target_sub, sub_list, ps)
    except:
        logging.warning("PM: User " + str(target_user) + " was not able to have their data and flair updated"
                        "\nStacktrace: " + str(traceback.print_exc()))

    # Update flair with new data
    prog_flair_enabled = target_sub.main_config.getboolean("progression tier")
    new_accnt_flair_enabled = target_sub.main_config.getboolean("young account tag")
    activity_flair_enabled = target_sub.main_config.getboolean("activity tag")
    FlairManager.update_flair(flair_queue, perm_queue, target_user, target_sub,
                              prog_flair_enabled, new_accnt_flair_enabled, activity_flair_enabled)

    logging.debug("PM: User " + str(target_user) + " has had their data and flair updated")


# Handle custom flair text requests
def text_pm(message, target_sub, r):
    user = message.author
    username = str(user).lower()
    message_lines = message.body.splitlines()

    # Return if the user is not in the database
    in_db = user_in_db(username, target_sub)
    if not in_db:
        message.reply("This user cannot be modified because there is no record of their account. "
                      "To fix this, you can use the !updateme PM command and then try again."
                      "Here is a [pre-formatted link](https://www.reddit.com/message/compose?to=" +
                      str(r.user.me().name) + "&subject=!" + target_sub.name + "%20!updateme&message=) for that PM command\n\n"
                      + message_footer)
        message.mark_read()
        logging.info("PM Error: User " + username + " tried to update flair but doesn't exist in database")
        return

    # Return if the user doesn't have proper permissions
    text_perm = target_sub.db.fetch_sub_info(username, "text perm") == 1
    if not text_perm:
        message.reply("You have not met the requirements for custom flair text. You will be notified via a PM "
                      "from /u/" + str(r.user.me().name) + " once your account is eligible." + message_footer)
        message.mark_read()
        logging.info("PM Privileges Error: User " + username + " tried to update flair "
                     "but doesn't have custom flair permissions")
        return

    if not message_lines[0].lower().startswith("flair text:"):
        message.reply(
            "This PM is not in the correct format for flair assignment. Try using [this pre-formatted link]"
            "(https://www.reddit.com/message/compose?to=" + str(r.user.me().name) + "&subject=!" + target_sub.name +
            "%20!flair&message=Flair%20Text:)."
            + message_footer)
        message.mark_read()
        logging.info("PM Format Error: User " + username + " tried to update flair "
                                                           "but the message doesn't start with Flair Text:")
        return

    # Pull flair info
    flair_txt = message_lines[0][11:]
    flair_css = next(target_sub.sub.flair(username))["flair_css"]

    # Set the flair and notify the user
    try:
        target_sub.sub.flair.set(username, flair_txt, flair_css)
    except exceptions.APIException:
        # Catch invalid flairs
        message.reply("There was an error processing your message. Perhaps your flair text was too long or there was "
                      "an issue with Reddit's servers. Please check your formatting and try again in a few minutes."
                      + message_footer)
        message.mark_read()
        logging.info("PM Format Error: User " + username + " tried to update flair but it threw an APIException")
        return

    target_sub.db.update_key_sub_info(username, "custom text used", 1)
    message.reply("Your flair has been set!\n\n\n\n"
                  "Flair Text: " + flair_txt + "\n\n" +
                  message_footer)
    message.mark_read()
    logging.info("PM: User " + username + " had their flair updated successfully")


# Handle custom flair text requests
def css_pm(message, target_sub, r):
    user = message.author
    username = str(user).lower()
    message_lines = message.body.splitlines()

    # Return if the user is not in the database
    in_db = user_in_db(username, target_sub)
    if not in_db:
        message.reply("This user cannot be modified because there is no record of their account. "
                      "To fix this, you can use the !updateme PM command and then try again."
                      "Here is a [pre-formatted link](https://www.reddit.com/message/compose?to=" +
                      str(r.user.me().name) + "&subject=!" + target_sub.name + "%20!updateme&message=) for that PM command\n\n"
                      + message_footer)
        message.mark_read()
        logging.info("PM Error: User " + username + " tried to update flair but doesn't exist in database")
        return

    # Return if the user doesn't have proper permissions
    text_perm = target_sub.db.fetch_sub_info(username, "text perm") == 1
    if not text_perm:
        message.reply("You have not met the requirements for custom flair styling. You will be notified via a PM "
                      "from /u/" + str(r.user.me().name) + " once your account is eligible." + message_footer)
        message.mark_read()
        logging.info("PM Privileges Error: User " + username + " tried to update flair "
                     "but doesn't have custom flair permissions")
        return

    if not message_lines[0].lower().startswith("flair css:"):
        message.reply(
            "This PM is not in the correct format for flair assignment. Try using [this pre-formatted link]"
            "(https://www.reddit.com/message/compose?to=" + str(r.user.me().name) + "&subject=!" + target_sub.name +
            "%20!flair&message=Flair%20CSS:)."
            + message_footer)
        message.mark_read()
        logging.info("PM Format Error: User " + username + " tried to update flair "
                     "but the message doesn't start with Flair Text:")
        return

    # Pull flair info
    flair_css = message_lines[0][11:]
    flair_text = target_sub.db.fetch_sub_info(username, "flair text")

    # Set the flair and notify the user
    try:
        target_sub.sub.flair.set(username, flair_text, flair_css)
    except exceptions.APIException:
        # Catch invalid flairs
        message.reply("There was an error processing your message. Perhaps your flair text was too long or there was "
                      "an issue with Reddit's servers. Please check your formatting and try again in a few minutes."
                      + message_footer)
        message.mark_read()
        logging.info("PM Format Error: User " + username + " tried to update flair but it threw an APIException")
        return

    target_sub.db.update_key_sub_info(username, "custom css used", 1)
    message.reply("Your flair has been set!\n\n\n\n"
                  "Flair Text: " + flair_text + "\n\n" +
                  "Flair CSS: " + flair_css + "\n\n" +
                  message_footer)
    message.mark_read()
    logging.info("PM: User " + username + " had their flair updated successfully")


# Handle custom flair requests
def flair_pm(message, target_sub, r):
    user = message.author
    username = str(user).lower()
    message_lines = message.body.splitlines()

    # Return if the user is not in the database
    in_db = user_in_db(username, target_sub)
    if not in_db:
        message.reply("This user cannot be modified because they have no entry in the database. "
                      "To fix this, you can use the !updateme PM command and then try again."
                      "Here is a [pre-formatted link](https://www.reddit.com/message/compose?to=" +
                      str(r.user.me().name) + "&subject=!" + target_sub.name + "%20!updateme&message=) for that PM command\n\n"
                      + message_footer)
        message.mark_read()
        logging.info("PM Error: User " + username + " tried to update flair but doesn't exist in database")
        return

    # Return if the user doesn't have proper permissions
    flair_perm = target_sub.db.fetch_sub_info(username, "flair perm") == 1
    if not flair_perm:
        message.reply("You have not met the requirements for custom flair. You will be notified via a PM "
                      "from /u/" + str(r.user.me().name) + " once your account is eligible." + message_footer)
        message.mark_read()
        logging.info("PM Privileges Error: User " + username + " tried to update flair "
                                                               "but doesn't have custom flair permissions")
        return

    if not message_lines[0].lower().startswith("flair text:"):
        message.reply("This PM is not in the correct format for flair assignment. Try using [this pre-formatted link]"
                      "(https://www.reddit.com/message/compose?to=" + str(r.user.me().name) + "&subject=!" + target_sub.name +
                      "%20!flair&message=Flair%20Text:%0AFlair%20CSS:)."
                      + message_footer)
        message.mark_read()
        logging.info("PM Format Error: User " + username + " tried to update flair "
                     "but the message doesn't start with Flair Text:")
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
    try:
        target_sub.sub.flair.set(username, flair_txt, flair_css)
    except exceptions.APIException:
        # Catch invalid flairs
        message.reply("There was an error processing your message. Perhaps your flair text was too long, your "
                      "flair CSS is invalid or there was an issue with Reddit's servers. Please check your formatting "
                      "and try again in a few minutes." + message_footer)
        message.mark_read()
        logging.info("PM Format Error: User " + username + " tried to update flair but it threw an APIException")
        return

    target_sub.db.update_key_sub_info(username, "custom flair used", 1)
    message.reply("Your flair has been set on " + target_sub.name + "!\n\n\n\n"
                  "Flair Text: " + flair_txt + "\n\n"
                  "Flair CSS:" + flair_css +
                  message_footer)
    message.mark_read()
    logging.info("PM: User " + username + " had their flair updated successfully")


# Prevents a user from having flair assigned by InstaMod
def remove_auto_flair(message, target_sub, r):
    target_username = message.body.lower()
    # Return if the user doesn't exist in the database
    in_db = user_in_db(target_username, target_sub)
    if not in_db:
        message.reply("This user cannot be modified because they have no entry in the database. "
                      "To fix this, you can use the !updatethem PM command and then try again. "
                      "Here is a [pre-formatted link](https://www.reddit.com/message/compose?to=" + str(r.user.me().name) +
                      "&subject=!" + target_sub.name + "%20!updatethem&message=) for that PM command\n\n"
                      + message_footer)
        message.mark_read()
        logging.info("PM Error: User " + str(message.author) + " tried to revoke " + target_username + "'s "
                     "flair but that user doesn't exist in database")
        return

    target_sub.db.update_key_sub_info(target_username, "no auto flair", 1)
    message.reply("The user " + target_username + " will no longer receive flair from InstaMod. " +
                  "Their user data will continue to be updated." + message_footer)
    message.mark_read()
    logging.info("PM: User " + target_username +
                 " had their custom flair permissions revoked by " + str(message.author))


# Grant a user the ability to assign themselves custom flair
def give_flair_perm(message, target_sub, perm_queue, r):
    target_username = message.body.lower()
    # Return if the user doesn't exist in the database
    in_db = user_in_db(target_username, target_sub)
    if not in_db:
        message.reply("This user cannot be modified because they have no entry in the database. "
                      "To fix this, you can use the !updatethem PM command and then try again. "
                      "Here is a [pre-formatted link](https://www.reddit.com/message/compose?to=" + str(r.user.me().name) +
                      "&subject=!" + target_sub.name + "%20!updatethem&message=) for that PM command\n\n"
                      + message_footer)
        message.mark_read()
        logging.info("PM Error: User " + str(message.author) + " tried to grant " + target_username +
                     " custom flair permissions but that user doesn't exist in database")
        return

    target_sub.db.update_key_sub_info(target_username, "flair perm", 1)
    message.reply("The user " + target_username + " has been granted custom flair permissions and will be notified."
                  + message_footer)
    message.mark_read()
    perm_queue.put([target_username, "flair perm", target_sub])
    logging.info("PM: User " + target_username +
                 " was given custom flair permissions by " + str(message.author))
