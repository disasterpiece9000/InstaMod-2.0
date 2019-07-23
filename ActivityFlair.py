
class ActivityFlair:

    # Activity flair main method
    def make_activity_flair(self, user, sub):
        activity_options = sub.sub_activity
        flair_text = []
        permissions = []

        # Loop through options in order
        option_count = 1
        while True:
            option_name = "ACTIVITY TAG " + str(option_count)
            option_count += 1

            # Process main option
            if option_name in activity_options:
                main_option = activity_options[option_name]
                group_subs = main_option.getboolean("group subs")
                sub_list = self.make_sub_list(main_option, sub)

                # TODO: Handle "ALL" option
                # Prepare vars to store result info
                and_result = True
                or_result = True
                option_name_and = option_name + " - AND"
                option_name_or = option_name + " - OR"

                # Handle grouped subs
                if group_subs:
                    main_data = self.check_activity(user, sub, sub_list, main_option)
                    main_result = main_data[0]
                    main_value = main_data[1]

                    # If main result is False check OR only
                    if not main_result:
                        if option_name_or in activity_options:
                            or_result = self.check_sub_option(activity_options, option_name_or, sub, user)

                    # If main result is True check AND and OR
                    else:
                        if option_name_or in activity_options:
                            or_result = self.check_sub_option(activity_options, option_name_or, sub, user)
                        elif option_name_and in activity_options:
                            and_result = self.check_sub_option(activity_options, option_name_and, sub, user)

                    # Process results
                    if main_result and and_result and or_result:
                        # Append flair
                        pre_text = main_option["pre text"]
                        post_text = main_option["post text"]
                        display_value = main_option.getboolean("display value")

                        # Concat flair
                        full_text = pre_text + " "
                        if display_value:
                            full_text += " " + str(main_value)
                        full_text += post_text
                        flair_text.append(full_text)
                        # Add relevant permissions
                        new_permissions = main_option["permissions"]
                        if new_permissions != "None":
                            permissions.append(new_permissions)

                # Handle individual subs
                else:
                    for sub_name in sub_list:
                        main_data = self.check_activity(user, sub, [sub_name], main_option)
                        main_result = main_data[0]
                        main_value = main_data[1]

                        # If main result is False check OR only
                        if not main_result:
                            if option_name_or in activity_options:
                                or_result = self.check_sub_option(activity_options, option_name_or, sub, user)

                        # If main result is True check AND and OR
                        else:
                            if option_name_or in activity_options:
                                or_result = self.check_sub_option(activity_options, option_name_or, sub, user)
                            elif option_name_and in activity_options:
                                and_result = self.check_sub_option(activity_options, option_name_and, sub, user)

                                # Process results
                                if main_result and and_result and or_result:
                                    # Append flair
                                    pre_text = main_option["pre text"]
                                    post_text = main_option["post text"]
                                    display_value = main_option.getboolean("display value")

                                    # Concat flair
                                    full_text = pre_text + " "
                                    if display_value:
                                        full_text += " " + str(main_value)
                                    full_text += post_text
                                    flair_text.append(full_text)
                                    # Add relevant permissions
                                    new_permissions = main_option["permissions"]
                                    if new_permissions != "None":
                                        permissions.append(new_permissions)

            else:
                break
        return [flair_text, permissions]

    def check_sub_option(self, activity_options, option_name, sub, user):
        option = activity_options[option_name]
        sub_list = self.make_sub_list(option, sub)
        data = self.check_activity(user, sub, sub_list, option)
        return data[0]

    def make_sub_list(self, option, sub):
        sub_group_name = option["target_subs"]

        # Create list with sub names from sub group that match specified abbrev
        if "-" in sub_group_name:
            # Get abbrev from string
            dash_index = sub_group_name.find("-")
            target_abbrev = sub_group_name[dash_index + 1:].strip()
            sub_group = sub.sub_groups[sub_group_name[:dash_index].strip()]
            sub_list = [name for name, abbrev in sub_group.items() if abbrev == target_abbrev]

        # Create list with all sub names from sub group
        else:
            sub_list = list(sub.sub_groups[sub_group_name].keys())

        return sub_list

    # Get user value from a specific sub (and subs that share the same abbreviation)
    def check_activity(self, user, sub, sub_list, option):
        target_value = int(option["target value"])
        metric = option["metric"]
        comparison = option["comparison"]

        user_value = self.get_user_value(metric, sub_list, user, sub)
        activity_result = self.check_value(user_value, comparison, target_value)

        return [activity_result, user_value]

    # Fetch the user_value from the database
    def get_user_value(self, metric, sub_list, user, sub):
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
    def check_value(self, user_value, comparison, value):
        if comparison == ">":
            return user_value > value
        if comparison == "<":
            return user_value > value
        if comparison == ">=":
            return user_value >= value
        if comparison == "<=":
            return user_value <= value