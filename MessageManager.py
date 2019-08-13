# TODO: Implement PM Messages and PM Commands section in config file

# TODO: Handle the appended "Re:" from PM replies

message_footer = ("\n\n-----\n\nThis is an automated message. "
                  "Please contact /u/shimmyjimmy97 with any questions, comments, or issues that you have.")


def process_pm(message, sub_list):
    message_subj = message.subject.split()
    # Return if the PM's subject does not contain the sub name and command
    if len(message_subj) != 2:
        message.reply("This message is not in the correct format and cannot be processed."
                      "Each PM command's subject must contain these parameters:\n\n"
                      "     !SubredditName !command" +
                      message_footer)
        message.mark_read()
        return
    
    # Get the subreddit the PM is in reference to
    sub_name = message_subj[0][1:].lower()
    command = message_subj[1]
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


# Handle custom flair requests
def flair_pm(message, target_sub):
    user = message.author
    username = str(user)
    message_lines = message.body.splitlines()
    user_in_db = target_sub.db.exists_in_db(username)
    flair_perm = target_sub.db.fetch_sub_info(username, "flair perm") == 1
    
    # Return if the user is not in the database yet or if they don't have proper permissions
    if not user_in_db or not flair_perm:
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
    message.mark_read()
    message.reply("Your flair has been set!\n\n"
                  "Flair Text: " + flair_txt + "\n\n"
                  "Flair CSS:" + flair_css +
                  message_footer)
