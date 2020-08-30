import logging


def make_prog_flair(user_data, sub):
    username = user_data.username
    prog_tiers = sub.progression_tiers

    # Loop through tiers in order
    tier_count = 1
    while True:
        tier_name = "PROGRESSION TIER " + str(tier_count)
        tier_count += 1

        if tier_name in prog_tiers:
            
            main_tier = prog_tiers[tier_name]
            main_result = user_in_tier(main_tier, user_data, sub)
            and_result = True
            or_result = True
            tier_name_and = tier_name + " - AND"
            tier_name_or = tier_name + " - OR"
            
            # Only check OR
            if not main_result:
                if tier_name_or in prog_tiers:
                    or_tier = prog_tiers[tier_name_or]
                    or_result = user_in_tier(or_tier, user_data, sub)
                    if or_result:
                        final_result = True
                    else:
                        final_result = False
                else:
                    final_result = False

            # Only check AND
            elif tier_name_and in prog_tiers:
                logging.debug("Checking AND")
                and_tier = prog_tiers[tier_name_and]
                and_result = user_in_tier(and_tier, user_data, sub)
                if and_result:
                    final_result = True
                else:
                    final_result = False

            else:
                final_result = True

            logging.debug("Main result: " + str(main_result) +
                          "\n\tOR result: " + str(or_result) +
                          "\n\tAND result: " + str(and_result) +
                          "\n\tFINAL result: " + str(final_result))

            # Check if user meets all the criteria (including and/or)
            if final_result:
                flair_text = main_tier["flair text"]
                flair_css = main_tier["flair css"]
                permissions = main_tier["permissions"].lower()

                if permissions == "":
                    permissions = None

                logging.debug("Flair text: " + flair_text +
                              "\n\tFlair css: " + flair_css +
                              "\n\tPermission: " + str(permissions))

                return [flair_text, flair_css, permissions]

        # Last tier was discovered
        else:
            logging.debug("No tiers found")
            return [None, None, False, False]


# Check if the user belongs in the given tier
def user_in_tier(tier, user_data, sub):
    username = user_data.username
    target_subs = tier["target subs"]
    # If an abbreviation is specified make a list of all subs with a matching abbreviation
    if "-" in target_subs:
        # Get abbreviation from string
        target_abbrev = target_subs[target_subs.find("-") + 1:].strip()
        # Check if multiple abbreviations are given
        if "," in target_abbrev:
            target_abbrev = target_abbrev.replace(" ", "").split(",")
        else:
            target_abbrev = [target_abbrev]

        # Get sub group name from string
        sub_group = sub.sub_groups[target_subs[:target_subs.find("-")].strip()]

        # Create a list of all subreddits with matching abbreviations
        sub_list = []
        for sub_name, abbrev in sub_group.items():
            if abbrev in target_abbrev:
                sub_list.append(sub_name)

    # Turn Sub Group into list if all subs option not selected
    elif target_subs == "ALL":
        sub_list = sub.db.get_all_subs(username)
    
    # Sub Group used
    elif "sub group" in target_subs.lower():
        sub_list = list(sub.sub_groups[target_subs].keys())
    
    # Single subreddit used
    else:
        sub_list = [target_subs]

    metric = tier["metric"].lower()
    comparison = tier["comparison"]

    # Parse the target value out of the metric
    if ">=" in comparison or "<=" in comparison:
        target_value = comparison[2:]
        comparison = comparison[:2]
    else:
        target_value = comparison[1:]
        comparison = comparison[:1]

    target_value = target_value.strip()

    if "percent" in target_value:
        user_value = get_user_perc(metric, sub_list, username, sub)
        target_value = int(target_value.split()[0])
    else:
        user_value = get_user_value(metric, sub_list, user_data, sub)
        target_value = int(target_value)

    return check_value(user_value, comparison, target_value)


# Handel % in progression tier
def get_user_perc(metric, sub_list, username, sub):
    user_pos, total = sub.db.fetch_sub_activity_perc(username, sub_list, metric)
    if total == 0:
        logging.warning("No rows found in sub_info. Cannot divide by 0")
        return 100
    return int((user_pos / total) * 100)


# Fetch the user_value from the database
def get_user_value(metric, sub_list, user_data, sub):
    user_value = 0

    # Get data from accnt_info table
    if metric in (sub.db.KEY4_POST_KARMA, sub.db.KEY4_COMMENT_KARMA):
        user_value = user_data.user_info[metric]

    elif metric == "total karma":
        user_value = user_data.total_post_karma + user_data.total_comment_karma

    # Get data from activity tables
    elif metric in (sub.db.SUB_ACTIVITY_KEY_LIST + sub.db.ACCNT_ACTIVITY_KEY_LIST):
        user_value = user_data.fetch_sub_activity(sub_list, metric)

    elif metric == "net qc":
        user_value = user_data.fetch_sub_activity(sub_list, sub.db.KEY2_POSITIVE_QC) - \
                     user_data.fetch_sub_activity(sub_list, sub.db.KEY2_NEGATIVE_QC)

    return user_value


# Check if the users value meets the requirements (target value and comparison)
def check_value(user_value, comparison, value):
    if comparison == ">":
        return user_value > value
    if comparison == "<":
        return user_value < value
    if comparison == ">=":
        return user_value >= value
    if comparison == "<=":
        return user_value <= value
