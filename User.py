import logging
import time
from configparser import RawConfigParser
from Database import Database

import prawcore


class User:
    def __init__(self, username, sub):
        self.db = sub.db
        user_data = sub.db.load_user_data(username, sub.name)
        self.user_info = user_data[0]

        # Account & Subreddit Activity
        self.user_activity = user_data[1]
        # Subreddit Info
        self.username = self.user_info[self.db.KEY1_USERNAME]
        self.ratelimit_start = self.user_info[self.db.KEY1_RATELIMIT_START]
        self.ratelimit_count = self.user_info[self.db.KEY1_RATELIMIT_COUNT]
        self.flair_text = self.user_info[self.db.KEY1_FLAIR_TEXT]
        self.last_updated = self.user_info[self.db.KEY1_LAST_UPDATED]
        self.flair_perm = self.user_info[self.db.KEY1_FLAIR_PERM]
        self.css_perm = self.user_info[self.db.KEY1_CSS_PERM]
        self.text_perm = self.user_info[self.db.KEY1_TEXT_PERM]
        self.custom_flair_used = self.user_info[self.db.KEY1_CUSTOM_FLAIR_USED]
        self.custom_text_used = self.user_info[self.db.KEY1_CUSTOM_TEXT_USED]
        self.custom_css_used = self.user_info[self.db.KEY1_CUSTOM_CSS_USED]
        # Account Info
        self.date_created = self.user_info[self.db.KEY4_DATE_CREATED]
        self.total_post_karam = self.user_info[self.db.KEY4_POST_KARMA]
        self.total_comment_karma = self.user_info[self.db.KEY4_COMMENT_KARMA]
        self.last_scraped = self.user_info[self.db.KEY4_LAST_SCRAPED]

    def fetch_sub_activity(self, sub_list, key):
        activity_result = 0
        for sub in sub_list:
            try:
                activity_result += self.user_activity[sub][key]
            except KeyError:
                continue

        return activity_result

    # Turn string from INI file into a key
    def find_activity_key(self, key):
        key = key.lower()
        if key == "sub name":
            return self.db.KEY2_SUB_NAME
        if key == "positive qc":
            return self.db.KEY2_POSITIVE_QC
        if key == "negative qc":
            return self.db.KEY2_NEGATIVE_QC
        if key == "sub name":
            return self.db.KEY3_SUB_NAME
        if key == "positive posts":
            return self.db.KEY3_POSITIVE_POSTS
        if key == "negative posts":
            return self.db.KEY3_NEGATIVE_POSTS
        if key == "positive comments":
            return self.db.KEY3_POSITIVE_COMMENTS
        if key == "negative comments":
            return self.db.KEY3_NEGATIVE_COMMENTS
        if key == "post karma":
            return self.db.KEY3_POST_KARMA
        if key == "comment karma":
            return self.db.KEY3_COMMENT_KARMA

        else:
            logging.critical("Could not find a match for key in the given table"
                             "\nKey: " + key + "\tTable:" + table)
            return None
