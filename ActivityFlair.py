from collections import defaultdict
import logging


# Activity flair main method
def make_activity_flair(username, sub):
    activity_settings = sub.sub_activity
    full_flair_text = []
    flair_perm = False
    css_perm = False

    # Loop through settings in order
    setting_count = 1
    while True:
        setting_name = "ACTIVITY TAG " + str(setting_count)
        setting_count += 1

        logging.debug("Checking " + setting_name)

        # Process main setting
        if setting_name in activity_settings:
            main_setting = activity_settings[setting_name]
            combine_subs = main_setting.getboolean("combine subs")
            sub_list = make_sub_list(main_setting, sub, username)

            # Prepare vars to store result info
            and_result = True
            or_result = True
            setting_name_and = setting_name + " - AND"
            setting_name_or = setting_name + " - OR"

            # Handle combined subs
            if combine_subs:
                logging.debug("Processing combined subs...")
                sub_names_list = [item[0] for item in sub_list]
                main_data = check_activity(username, sub, sub_names_list, main_setting)
                main_result = main_data[0]
                main_value = main_data[1]

                # Check OR only
                if not main_result:
                    if setting_name_or in activity_settings:
                        or_result = check_sub_setting(activity_settings, setting_name_or, sub, username)

                # If main result is True check AND and OR
                else:
                    if setting_name_or in activity_settings:
                        or_result = check_sub_setting(activity_settings, setting_name_or, sub, username)
                    elif setting_name_and in activity_settings:
                        and_result = check_sub_setting(activity_settings, setting_name_and, sub, username)

                logging.debug("Main result: " + str(main_result) +
                              "\n\tOR result: " + str(or_result) +
                              "\n\tAND result: " + str(and_result))

                # Process results
                if main_result and and_result and or_result:
                    pre_text = main_setting["pre text"]
                    post_text = main_setting["post text"]
                    display_value = main_setting.getboolean("display value")

                    # Concatenate flair text
                    flair_text = ""
                    flair_text += pre_text + " " if pre_text else ""
                    flair_text += str(main_value) + " " if display_value else ""
                    flair_text += post_text + " " if post_text else ""

                    if flair_text != "":
                        # Trim trailing whitespace
                        logging.debug("Flair text: " + flair_text)
                        full_flair_text.append(flair_text[:len(flair_text) - 1])

                    # Check if there is a valid permission
                    permission = main_setting["permissions"].lower()
                    if permission == "custom flair":
                        flair_perm = True
                        logging.debug("Flair perm = True")
                    elif permission == "custom css":
                        css_perm = True
                        logging.debug("CSS perm = True")

            # Handle individual subs
            else:
                logging.debug("Processing individual subs...")
                # Store data on results that meet criteria so that sort and sub cap can be implemented later
                flair_data = {}

                # Turn sub_list into a dict {abbrev: [sub1, sub2,...]}
                abbrev_dict = defaultdict(list)
                for data in sub_list:
                    name = data[0]
                    abbrev = data[1]
                    abbrev_dict[abbrev].append(name)

                # Process subs combined by abbrev
                for data in abbrev_dict.items():
                    abbrev = data[0]
                    combined_sub_list = data[1]

                    main_data = check_activity(username, sub, combined_sub_list, main_setting)
                    main_result = main_data[0]
                    main_value = main_data[1]

                    # If main result is False check OR only
                    if not main_result:
                        if setting_name_or in activity_settings:
                            or_result = check_sub_setting(activity_settings, setting_name_or, sub, username)

                    # If main result is True check AND and OR
                    else:
                        if setting_name_or in activity_settings:
                            or_result = check_sub_setting(activity_settings, setting_name_or, sub, username)
                        elif setting_name_and in activity_settings:
                            and_result = check_sub_setting(activity_settings, setting_name_and, sub, username)

                    #logging.debug("Main result: " + str(main_result) +
                    #              "\n\tOR result: " + str(or_result) +
                    #              "\n\tAND result: " + str(and_result))

                    # Process results
                    if main_result and and_result and or_result:
                        flair_data[abbrev] = main_value

                # Add data to lists unless they are None
                processed_data = process_flair_data(main_setting, flair_data)
                if len(processed_data) != 3:
                    logging.critical("process_flair_data didn't return all data")
                if processed_data[0]:
                    full_flair_text.append(processed_data[0])
                    logging.debug("Flair text: " + str(processed_data[0]))
                # Check if either perm returned True
                if processed_data[1]:
                    flair_perm = True
                    logging.debug("Flair perm = True")
                elif processed_data[2]:
                    css_perm = True
                    logging.debug("CSS perm = True")

        # No more settings activity tags to discover
        else:
            break
            
    logging.debug("Final results:" +
                  "\n\tFull text: " + str(full_flair_text) +
                  "\n\tFlair perm: " + str(flair_perm) +
                  "\n\tCSS perm: " + str(css_perm))
    
    return [full_flair_text, flair_perm, css_perm]


# Process combined sub flair data
def process_flair_data(setting, flair_data):
    # If no subreddits meet criteria then no flair text or permissions are added
    if len(flair_data) == 0:
        return [None, False, False]
    
    sort = setting["sort"]
    sub_cap = setting.getint("sub cap")
    pre_text = setting["pre text"]
    post_text = setting["post text"]
    display_value = setting.getboolean("display value")
    permission = setting["permissions"].lower()

    # Set default sort to most common
    reverse = True
    # If least common sort selected, list will not need to be reversed later
    if sort == "least common":
        reverse = False
    # If sub cap is not enabled, set it to 100 so it will not cut off any items
    if not sub_cap:
        sub_cap = 100

    # Sort flair_data by the key (user value)
    # I love python list/dict comprehension...I must learn more
    sorted_data = {abbrev: flair_data[abbrev] for abbrev in sorted(
                flair_data, key=flair_data.get, reverse=reverse)[:sub_cap]}

    # Concatenate flair text
    flair_text = ""
    for abbrev, value in sorted_data.items():
        flair_text += pre_text + " " if pre_text else ""
        flair_text += abbrev + " "
        flair_text += str(value) + " " if display_value else ""
        flair_text += post_text + " " if post_text else ""
        flair_text += ", "

    # Remove trailing " , "
    flair_text = flair_text[:len(flair_text) - 2]
    flair_text = flair_text.strip()
    if not flair_text:
        flair_text = None

    # Process updated permissions
    flair_perm, css_perm = False
    if permission == "custom flair":
        flair_perm = True
    elif permission == "custom css":
        css_perm = True

    return [flair_text, flair_perm, css_perm]


# Check result of secondary criteria
def check_sub_setting(activity_settings, setting_name, parent_sub, username):
    setting = activity_settings[setting_name]
    sub_list = make_sub_list(setting, parent_sub, username)
    data = check_activity(username, parent_sub, sub_list, setting)
    return data[0]


# Make a list of subreddit names and abbrevs based on section settings
def make_sub_list(setting, sub, username):
    sub_group_name = setting["target subs"]

    # Create a list of all subs with info in the database
    if sub_group_name == "ALL":
        sub_list = [[name, ""] for name in sub.db.get_all_subs(username)]

    # Create list with sub names from sub combine that match specified abbrev
    elif "-" in sub_group_name:
        # Get abbrev from string
        dash_index = sub_group_name.find("-")
        target_abbrev = sub_group_name[dash_index + 1:].strip()
        sub_group = sub.sub_groups[sub_group_name[:dash_index].strip()]
        sub_list = [[name, abbrev] for name, abbrev in sub_group.items() if abbrev == target_abbrev]

    # Create list with all sub names from sub combine
    else:
        sub_group = sub.sub_groups[sub_group_name]
        sub_list = [[name, abbrev] for name, abbrev in sub_group.items()]

    return sub_list


# Get user value from a specific sub (and subs that share the same abbreviation)
def check_activity(username, sub, sub_list, setting):
    target_value = setting.getint("target value")
    metric = setting["metric"].lower()
    comparison = setting["comparison"].lower()

    user_value = get_user_value(metric, sub_list, username, sub)
    activity_result = check_value(user_value, comparison, target_value)

    return [activity_result, user_value]


# Fetch the user_value from the database
def get_user_value(metric, sub_list, username, sub):
    user_value = 0

    # Get data from accnt_info table
    if metric in ("total comment karma", "total post karma"):
        user_value = sub.db.fetch_info_table(username, metric)
    elif metric == "total karma":
        user_value = sub.db.fetch_info_table(username, "total post karma") + \
                     sub.db.fetch_info_table(username, "total comment karma")

    # Get data from accnt_history table
    elif metric in ("comment karma", "post karma", "positive comments", "negative comments",
                    "positive posts", "negative posts", "positive QC", "negative QC"):
        user_value = sub.db.fetch_hist_table(username, sub_list, metric)
    elif metric == "net QC":
        user_value = sub.db.fetch_hist_table(username, sub_list, "positive QC") - \
                     sub.db.fetch_hist_table(username, sub_list, "negative QC")

    return user_value


# Check if the users value meets the requirements (target value and comparison)
def check_value(user_value, comparison, value):
    if comparison == ">":
        return user_value > value
    if comparison == "<":
        return user_value > value
    if comparison == ">=":
        return user_value >= value
    if comparison == "<=":
        return user_value <= value
