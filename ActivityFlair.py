# TODO: Consider making meta settings for each module
# Ex: pre/post text for each flair module type

# TODO: Change name for grouped, option, etc

from collections import defaultdict


# Activity flair main method
def make_activity_flair(user, sub):
    activity_options = sub.sub_activity
    full_flair_text = []
    full_permissions = []

    # Loop through options in order
    option_count = 1
    while True:
        option_name = "ACTIVITY TAG " + str(option_count)
        option_count += 1

        # Process main option
        if option_name in activity_options:
            main_option = activity_options[option_name]
            group_subs = main_option.getboolean("group subs")
            sub_list = make_sub_list(main_option, sub)

            # TODO: Handle "ALL" option
            # Prepare vars to store result info
            and_result = True
            or_result = True
            option_name_and = option_name + " - AND"
            option_name_or = option_name + " - OR"

            # Handle grouped subs
            if group_subs:
                sub_names_list = [item[0] for item in sub_list]
                main_data = check_activity(user, sub, sub_names_list, main_option)
                main_result = main_data[0]
                main_value = main_data[1]

                # If main result is False check OR only
                if not main_result:
                    if option_name_or in activity_options:
                        or_result = check_sub_option(activity_options, option_name_or, sub, user)

                # If main result is True check AND and OR
                else:
                    if option_name_or in activity_options:
                        or_result = check_sub_option(activity_options, option_name_or, sub, user)
                    elif option_name_and in activity_options:
                        and_result = check_sub_option(activity_options, option_name_and, sub, user)

                # Process results
                if main_result and and_result and or_result:
                    # TODO: Fix flair concatenation with split()
                    pre_text = main_option["pre text"]
                    post_text = main_option["post text"]
                    display_value = main_option.getboolean("display value")
                    flair_text = ""
                    flair_text += pre_text + " " if pre_text else ""
                    flair_text += str(main_value) + " " if display_value else ""
                    flair_text += post_text + " " if post_text else ""

                    if flair_text != "":
                        # Trim trailing whitespace
                        full_flair_text.append(flair_text[:len(flair_text) - 1])

                    # Check if there is a valid permission
                    permission = main_option["permissions"]
                    if permission in ["custom flair", "custom css"]:
                        full_permissions.append(permission)

            # Handle individual subs
            else:
                # Store data on results that meet criteria so that sort and sub cap can be implemented later
                flair_data = {}

                # Turn sub_list into a dict {abbrev: [sub1, sub2,...]}
                abbrev_dict = defaultdict(list)
                for data in sub_list:
                    name = data[0]
                    abbrev = data[1]
                    abbrev_dict[abbrev].append(name)

                # Process subs grouped by abbrev
                for data in abbrev_dict.items():
                    abbrev = data[0]
                    grouped_sub_list = data[1]

                    main_data = check_activity(user, sub, grouped_sub_list, main_option)
                    main_result = main_data[0]
                    main_value = main_data[1]

                    # If main result is False check OR only
                    if not main_result:
                        if option_name_or in activity_options:
                            or_result = check_sub_option(activity_options, option_name_or, sub, user)

                    # If main result is True check AND and OR
                    else:
                        if option_name_or in activity_options:
                            or_result = check_sub_option(activity_options, option_name_or, sub, user)
                        elif option_name_and in activity_options:
                            and_result = check_sub_option(activity_options, option_name_and, sub, user)

                            # Process results
                            if main_result and and_result and or_result:
                                flair_data[abbrev] = main_value

                processed_data = process_flair_data(main_option, flair_data)
                full_flair_text.append(processed_data[0])
                # Don't append None to permissions list
                if processed_data[1]:
                    full_permissions.append(processed_data[1])

        # No more options activity tags to discover
        else:
            break
    return [full_flair_text, full_permissions]


def process_flair_data(option, flair_data):
    sort = option["sort"]
    sub_cap = option.getint("sub cap")
    pre_text = option["pre text"]
    post_text = option["post text"]
    display_value = option.getboolean("display value")
    permission = option["permissions"]

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

    flair_text = ""
    for abbrev, value in sorted_data.items():
        flair_text += pre_text + " " if pre_text else ""
        flair_text += abbrev + " "
        flair_text += str(value) + " " if display_value else ""
        flair_text += post_text + " " if post_text else ""
        flair_text += ", "

    # Remove trailing " , "
    flair_text = flair_text[:len(flair_text) - 3]

    # Check if there is a valid permission
    if permission not in ["custom flair", "custom css"]:
        permission = None

    return [flair_text, permission]


# Check result of secondary criteria
def check_sub_option(activity_options, option_name, parent_sub, user):
    option = activity_options[option_name]
    sub_list = make_sub_list(option, parent_sub)
    data = check_activity(user, parent_sub, sub_list, option)
    return data[0]


# Make a list of subreddit names and abbrevs based on section settings
def make_sub_list(option, sub):
    sub_group_name = option["target_subs"]

    # Create list with sub names from sub group that match specified abbrev
    if "-" in sub_group_name:
        # Get abbrev from string
        dash_index = sub_group_name.find("-")
        target_abbrev = sub_group_name[dash_index + 1:].strip()
        sub_group = sub.sub_groups[sub_group_name[:dash_index].strip()]
        sub_list = [[name, abbrev] for name, abbrev in sub_group.items() if abbrev == target_abbrev]

    # Create list with all sub names from sub group
    else:
        sub_list = list(sub.sub_groups[sub_group_name].keys())

    return sub_list


# Get user value from a specific sub (and subs that share the same abbreviation)
def check_activity(user, sub, sub_list, option):
    target_value = int(option["target value"])
    metric = option["metric"]
    comparison = option["comparison"]

    user_value = get_user_value(metric, sub_list, user, sub)
    activity_result = check_value(user_value, comparison, target_value)

    return [activity_result, user_value]


# Fetch the user_value from the database
def get_user_value(metric, sub_list, user, sub):
    username = str(user)
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
