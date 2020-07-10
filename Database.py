import logging
import sqlite3
from collections import Counter


class Database:
    # Subreddit Info Table
    TABLE_SUB_INFO = ""
    KEY1_USERNAME = "username"
    KEY1_RATELIMIT_START = "ratelimit_start"
    KEY1_RATELIMIT_COUNT = "ratelimit_count"
    KEY1_FLAIR_TEXT = "flair_text"
    KEY1_LAST_UPDATED = "last_updated"
    KEY1_FLAIR_PERM = "flair_perm"
    KEY1_CSS_PERM = "css_perm"
    KEY1_TEXT_PERM = "text_perm"
    KEY1_CUSTOM_FLAIR_USED = "custom_flair_used"
    KEY1_CUSTOM_TEXT_USED = "custom_text_used"
    KEY1_CUSTOM_CSS_USED = "custom_css_used"
    KEY1_NO_AUTO_FLAIR = "no_auto_flair"

    # Subreddit Activity Table
    TABLE_SUB_ACTIVITY = ""
    KEY2_USERNAME = "username"
    KEY2_SUB_NAME = "sub_name"
    KEY2_POSITIVE_QC = "positive_qc"
    KEY2_NEGATIVE_QC = "negative_qc"

    # Account Activity Table
    TABLE_ACCNT_ACTIVITY = "accnt_activity"
    KEY3_USERNAME = "username"
    KEY3_SUB_NAME = "sub_name"
    KEY3_POSITIVE_POSTS = "positive_posts"
    KEY3_NEGATIVE_POSTS = "negative_posts"
    KEY3_POSITIVE_COMMENTS = "positive_comments"
    KEY3_NEGATIVE_COMMENTS = "negative_comments"
    KEY3_POST_KARMA = "post_karma"
    KEY3_COMMENT_KARMA = "comment_karma"
    CREATE_SUB_ACTIVITY = ("CREATE TABLE IF NOT EXISTS " + TABLE_ACCNT_ACTIVITY + " (" +
                           KEY3_USERNAME + " TEXT, " + KEY3_SUB_NAME + " TEXT, " +
                           KEY3_POSITIVE_POSTS + " INTEGER, " + KEY3_NEGATIVE_POSTS + " INTEGER, " +
                           KEY3_POSITIVE_COMMENTS + " INTEGER, " + KEY3_NEGATIVE_COMMENTS + " INTEGER, " +
                           KEY3_POST_KARMA + " INTEGER, " + KEY3_COMMENT_KARMA + " INTEGER" +
                           ")")

    # Account Information Table
    TABLE_ACCNT_INFO = "accnt_info"
    KEY4_USERNAME = "username"
    KEY4_DATE_CREATED = "date_created"
    KEY4_POST_KARMA = "total_post_karma"
    KEY4_COMMENT_KARMA = "total_comment_karma"
    KEY4_LAST_SCRAPED = "last_scraped"
    CREATE_ACCNT_INFO = ("CREATE TABLE IF NOT EXISTS " + TABLE_ACCNT_INFO + " (" +
                         KEY4_USERNAME + " TEXT PRIMARY KEY, " + KEY4_DATE_CREATED + " INTEGER, " +
                         KEY4_POST_KARMA + " INTEGER, " + KEY4_COMMENT_KARMA + " INTEGER, " +
                         KEY4_LAST_SCRAPED + " INTEGER" +
                         ")")

    # Create tables if needed
    def __init__(self, sub_name):
        # Connect to all tables
        self.conn = sqlite3.connect("master_databank.db", isolation_level=None, check_same_thread=False)
        cur = self.conn.cursor()

        # Create shared tables if necessary
        cur.execute(self.CREATE_SUB_ACTIVITY)
        cur.execute(self.CREATE_ACCNT_INFO)

        # Create subreddit table if necessary
        self.TABLE_SUB_INFO = sub_name + "_info"
        cur.execute("CREATE TABLE IF NOT EXISTS " + self.TABLE_SUB_INFO + " (" +
                    self.KEY1_USERNAME + " TEXT PRIMARY KEY, " + self.KEY1_RATELIMIT_START + " INTEGER, " +
                    self.KEY1_RATELIMIT_COUNT + " INTEGER, " + self.KEY1_FLAIR_TEXT + " TEXT, " +
                    self.KEY1_LAST_UPDATED + " INTEGER, " + self.KEY1_FLAIR_PERM + " INTEGER, " +
                    self.KEY1_CSS_PERM + " INTEGER, " + self.KEY1_TEXT_PERM + "INTEGER, " +
                    self.KEY1_CUSTOM_FLAIR_USED + " INTEGER, " + self.KEY1_CUSTOM_TEXT_USED + " INTEGER, " +
                    self.KEY1_CUSTOM_CSS_USED + " INTEGER, " + self.KEY1_NO_AUTO_FLAIR + " INTEGER)")

        self.TABLE_SUB_ACTIVITY = sub_name + "_activity"
        cur.execute("CREATE TABLE IF NOT EXISTS " + self.TABLE_SUB_ACTIVITY + " (" +
                    self.KEY2_USERNAME + " TEXT, " + self.KEY2_SUB_NAME + " TEXT, " +
                    self.KEY2_POSITIVE_QC + " INTEGER, " + self.KEY2_NEGATIVE_QC + " INTEGER)")
        cur.close()

    # Check if a user exists in the account info table
    def exists_in_accnt_info(self, username):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY4_USERNAME + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY4_USERNAME + " = ?")

        cur.execute(select_str, (username,))
        data = cur.fetchone()
        if data:
            return True
        else:
            return False

    def exists_in_sub_info(self, username):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY1_USERNAME + " FROM " + self.TABLE_SUB_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")

        cur.execute(select_str, (username,))
        data = cur.fetchone()
        if data:
            return True
        else:
            return False

    # Insert user data into Sub Info table
    def insert_sub_info(self, username, ratelimit_start, ratelimit_count, flair_txt, last_updated):
        # Set default permissions to False
        # These values are updated at different stages
        flair_perm = 0
        css_perm = 0
        custom_flair_used = 0
        no_auto_flair = 0

        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_SUB_INFO + "(" + self.KEY1_USERNAME + ", "
                      + self.KEY1_RATELIMIT_START + ", " + self.KEY1_RATELIMIT_COUNT + ", "
                      + self.KEY1_FLAIR_TEXT + ", " + self.KEY1_LAST_UPDATED + ", "
                      + self.KEY1_FLAIR_PERM + ", " + self.KEY1_CSS_PERM + ", "
                      + self.KEY1_CUSTOM_FLAIR_USED + ", " + self.KEY1_NO_AUTO_FLAIR
                      + ") "
                      + "VALUES(?,?,?,?,?,?,?,?,?)")

        cur.execute(insert_str, (username, ratelimit_start, ratelimit_count, flair_txt,
                                 last_updated, flair_perm, css_perm, custom_flair_used, no_auto_flair))
        cur.close()

    # Update existing user's data in Sub Info table
    def update_row_sub_info(self, username, ratelimit_start, ratelimit_count, flair_txt, last_updated):
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_SUB_INFO
                      + " SET " + self.KEY1_RATELIMIT_START + " = ?, " + self.KEY1_RATELIMIT_COUNT + " = ?, "
                      + self.KEY1_FLAIR_TEXT + " = ?, " + self.KEY1_LAST_UPDATED + " = ? "
                      + "WHERE " + self.KEY1_USERNAME + " = ?")

        cur.execute(update_str, (ratelimit_start, ratelimit_count, flair_txt, last_updated, username))
        cur.close()

    def insert_sub_activity(self, username, all_pos_qc, all_neg_qc):
        cur = self.conn.cursor()
        insert_str_end = (" ("
                          + self.KEY2_USERNAME + ", " + self.KEY2_SUB_NAME + ", "
                          + self.KEY2_POSITIVE_QC + ", " + self.KEY2_NEGATIVE_QC + ") "
                          + "VALUES(?,?,?,?)")

        # Insert QC for all subreddits in database
        for target_sub in all_pos_qc:
            target_sub_pos = all_pos_qc[target_sub]
            target_sub_neg = all_neg_qc[target_sub]
            target_sub_table = target_sub + "_activity"
            insert_str = "INSERT INTO " + target_sub_table + insert_str_end

            # Loop through all subreddits with new QC values
            all_subs = target_sub_pos.keys() | target_sub_neg.keys()
            # Put data from dictionaries into a list of tuples
            insert_data_sub = [(username, sub, target_sub_pos[sub], target_sub_neg[sub])
                               for sub in all_subs]
            cur.executemany(insert_str, insert_data_sub)

        cur.close()

    def insert_accnt_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments,
                              sub_post_karma, sub_pos_posts, sub_neg_posts):
        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_ACCNT_ACTIVITY + "("
                      + self.KEY3_USERNAME + ", " + self.KEY3_SUB_NAME + ", "
                      + self.KEY3_POSITIVE_POSTS + ", " + self.KEY3_NEGATIVE_POSTS + ", "
                      + self.KEY3_POSITIVE_COMMENTS + ", " + self.KEY3_NEGATIVE_COMMENTS + ", "
                      + self.KEY3_POST_KARMA + ", " + self.KEY3_COMMENT_KARMA + ") "
                      + "VALUES(?,?,?,?,?,?,?,?)")

        # Union of all keys in both primary dictionaries
        all_subs = sub_comment_karma.keys() | sub_post_karma.keys()
        # Put data from dictionaries into a list of tuples
        insert_data_accnt = [(username, sub, sub_pos_posts[sub], sub_neg_posts[sub], sub_pos_comments[sub],
                              sub_neg_comments[sub], sub_post_karma[sub], sub_comment_karma[sub])
                             for sub in all_subs]

        cur.executemany(insert_str, insert_data_accnt)

    def update_sub_activity(self, username, all_pos_qc, all_neg_qc):
        cur = self.conn.cursor()
        update_str = ("UPDATE ? SET "
                      + self.KEY2_POSITIVE_QC + " = " + self.KEY2_POSITIVE_QC + "+ ?, "
                      + self.KEY2_NEGATIVE_QC + " = " + self.KEY2_NEGATIVE_QC + "+ ? "
                      + "WHERE " + self.KEY3_USERNAME + " = ? "
                      + "AND " + self.KEY3_SUB_NAME + " = ?")

        # Update QC for all subreddits in database
        for target_sub in all_pos_qc:
            target_sub_pos = all_pos_qc[target_sub]
            target_sub_neg = all_neg_qc[target_sub]
            target_sub_table = target_sub + "_activity"

            # Union of all keys in both dictionaries
            all_subs = target_sub_pos.keys() | target_sub_neg.keys()

            # Loop through all subreddits with new QC values
            for sub in all_subs:
                # Attempt to update row
                row_updated = cur.execute(update_str, (target_sub_table, target_sub_pos[sub],
                                                       target_sub_neg[sub], username, sub)
                                          ).rowcount == 1

                # Insert row if update failed
                if not row_updated:
                    insert_pos_qc = {target_sub: Counter({sub: target_sub_pos[sub]})}
                    insert_neg_qc = {target_sub: Counter({sub: target_sub_neg[sub]})}
                    self.insert_sub_activity(username, insert_pos_qc, insert_neg_qc)

        cur.close()

    def update_accnt_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments,
                              sub_post_karma, sub_pos_posts, sub_neg_posts):
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_ACCNT_ACTIVITY + " SET "
                      + self.KEY3_COMMENT_KARMA + " = " + self.KEY3_COMMENT_KARMA + " + ?, "
                      + self.KEY3_POSITIVE_COMMENTS + " = " + self.KEY3_POSITIVE_COMMENTS + " + ?, "
                      + self.KEY3_NEGATIVE_COMMENTS + " = " + self.KEY3_NEGATIVE_COMMENTS + " + ?, "
                      + self.KEY3_POST_KARMA + " = " + self.KEY3_POST_KARMA + " + ?, "
                      + self.KEY3_POSITIVE_POSTS + " = " + self.KEY3_POSITIVE_POSTS + " + ?, "
                      + self.KEY3_NEGATIVE_POSTS + " = " + self.KEY3_NEGATIVE_POSTS + " + ? "
                      + "WHERE " + self.KEY3_USERNAME + " = ? "
                      + "AND " + self.KEY3_SUB_NAME + " = ?")

        # Union of all keys in both primary dictionaries
        all_subs = sub_comment_karma.keys() | sub_post_karma.keys()

        for sub in all_subs:
            # Attempt to update row
            row_updated = cur.execute(update_str, (sub_comment_karma[sub], sub_pos_comments[sub],
                                                   sub_neg_comments[sub], sub_post_karma[sub],
                                                   sub_pos_posts[sub], sub_neg_posts[sub], username, sub)
                                      ).rowcount == 1

            # Insert row if update failed
            if not row_updated:
                # Make a dict of data for this subreddit only to pass to insert method
                insert_data = [{sub: item[sub]} for item in [sub_comment_karma, sub_pos_comments, sub_neg_comments,
                                                             sub_post_karma, sub_pos_posts, sub_neg_posts]]
                self.insert_accnt_activity(username, insert_data[0], insert_data[1], insert_data[2],
                                           insert_data[3], insert_data[4], insert_data[5])

        cur.close()

    # Insert user data into Account Info table
    def insert_accnt_info(self, username, created, total_post_karma, total_comment_karma, last_scraped):
        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_ACCNT_INFO + "("
                      + self.KEY4_USERNAME + ", " + self.KEY4_DATE_CREATED + ", "
                      + self.KEY4_POST_KARMA + ", " + self.KEY4_COMMENT_KARMA + ", "
                      + self.KEY4_LAST_SCRAPED + ") "
                      + "VALUES(?,?,?,?,?)")

        cur.execute(insert_str, (username, created, total_post_karma, total_comment_karma, last_scraped))
        cur.close()

    # Update user data in Account Info table
    def update_accnt_info(self, username, post_karma, comment_karma, last_scraped):
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_ACCNT_INFO + " SET "
                      + self.KEY4_POST_KARMA + " = ?, " + self.KEY4_COMMENT_KARMA + " = ?, "
                      + self.KEY4_LAST_SCRAPED + " = ? "
                      + "WHERE " + self.KEY4_USERNAME + " = ?")

        cur.execute(update_str, (post_karma, comment_karma, last_scraped, username))
        cur.close()

    # Drop all user data
    def partial_drop_user(self, username):
        cur = self.conn.cursor()

        # Get list of all tables
        select_str = ("SELECT name FROM sqlite_master "
                      "WHERE type='table';")

        cur.execute(select_str)
        tables = cur.fetchall()

        # Delete user data in each activity table
        delete_str_start = "DELETE FROM "
        delete_str_end = " WHERE username = ?"
        for table_name in tables:
            if not table_name[0].endswith("_info") or table_name[0] == "accnt_info":
                delete_str = delete_str_start + table_name[0] + delete_str_end
                cur.execute(delete_str, (username,))

    # Generic getter method for Account Info table
    def fetch_sub_info(self, username, key):
        select_key = self.find_key(key, self.TABLE_SUB_INFO)
        cur = self.conn.cursor()
        select_str = ("SELECT " + select_key + " FROM " + self.TABLE_SUB_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")

        cur.execute(select_str, (username,))
        data = cur.fetchone()
        value = data[0] if data is not None else None
        cur.close()
        return value

    # Generic getter method for Account History table
    def fetch_sub_activity(self, username, sub_list, key):
        key = key.lower()
        cur = self.conn.cursor()
        sub_list_str = "'" + "', '".join(sub_list) + "'"

        if "qc" in key:
            select_key = self.find_key(key, self.TABLE_SUB_ACTIVITY)
            from_table = self.TABLE_SUB_ACTIVITY
            where_key1 = self.KEY2_USERNAME
            where_key2 = self.KEY2_SUB_NAME
        else:
            select_key = self.find_key(key, self.TABLE_ACCNT_ACTIVITY)
            from_table = self.TABLE_ACCNT_ACTIVITY
            where_key1 = self.KEY3_USERNAME
            where_key2 = self.KEY3_SUB_NAME

        # Sum only the specified rows (subreddits)
        select_str = ("SELECT SUM(" + select_key + ") FROM " + from_table
                      + " WHERE " + where_key1 + " = ? AND "
                      + where_key2 + " IN (" + sub_list_str + ")")

        cur.execute(select_str, (username,))
        data = cur.fetchone()
        if data is not None:
            return data[0]
        else:
            return 0

    def fetch_sub_activity_perc(self, username, sub_list, key):
        cur = self.conn.cursor()

        total_select_str = "SELECT COUNT(" + self.KEY1_USERNAME + ") " \
                                                                  "FROM " + self.TABLE_SUB_INFO
        cur.execute(total_select_str)
        total_num = cur.fetchone()[0]

        if key == "net qc":
            user_select_str = "SELECT top_rank FROM (" + \
                              "SELECT ui." + self.KEY2_USERNAME + ", RANK() OVER(ORDER BY summed DESC) AS 'top_rank' " \
                              "FROM (" \
                                "SELECT SUM(" + self.KEY2_POSITIVE_QC + ") - SUM(" + self.KEY2_NEGATIVE_QC + ") " \
                                "AS 'summed', " + self.KEY2_USERNAME + " " \
                                "FROM " + self.TABLE_SUB_ACTIVITY + " " \
                                "WHERE " + self.KEY2_SUB_NAME + " IN ('" + "', '".join(sub_list) + "')" \
                                "GROUP BY " + self.KEY2_USERNAME + ") ui " \
                              "JOIN " + self.TABLE_SUB_INFO + " sub " \
                              "ON sub." + self.KEY1_USERNAME + " = ui." + self.KEY2_USERNAME + ") uo " \
                              "WHERE " + self.KEY2_USERNAME + " = ?"
        else:
            if "qc" in key:
                select_key1 = self.KEY2_USERNAME
                select_key2 = self.find_key(key, self.TABLE_SUB_ACTIVITY)
                select_key3 = self.KEY2_USERNAME
                from_table = self.TABLE_SUB_ACTIVITY
                where_key1 = self.KEY2_SUB_NAME
                group_key = self.KEY2_USERNAME
                on_key = self.KEY2_USERNAME
                where_key2 = self.KEY2_USERNAME

            else:
                select_key1 = self.KEY3_USERNAME
                select_key2 = self.find_key(key, self.TABLE_SUB_ACTIVITY)
                select_key3 = self.KEY3_USERNAME
                from_table = self.TABLE_ACCNT_ACTIVITY
                where_key1 = self.KEY3_SUB_NAME
                group_key = self.KEY3_USERNAME
                on_key = self.KEY3_USERNAME
                where_key2 = self.KEY3_USERNAME

            user_select_str = "SELECT top_rank FROM (" + \
                              "SELECT ui." + select_key1 + ", RANK() OVER(ORDER BY summed DESC) AS 'top_rank' " \
                              "FROM (" \
                                "SELECT SUM(" + select_key2 + ") AS 'summed', " + select_key3 + " " \
                                "FROM " + from_table + " " \
                                "WHERE " + where_key1 + " IN ('" + "', '".join(sub_list) + "')" \
                                "GROUP BY " + group_key + ") ui " \
                              "JOIN " + self.TABLE_SUB_INFO + " sub " \
                              "ON sub." + self.KEY1_USERNAME + " = ui." + on_key + ") uo " \
                              "WHERE " + where_key2 + " = ?"

        cur.execute(user_select_str, (username,))
        try:
            user_pos = cur.fetchone()[0]
        except TypeError:
            logging.debug("User has no rows in sub_activity: " + username)
            user_pos = total_num

        return user_pos, total_num

    # Generic getter method for Account Info table
    def fetch_accnt_info(self, username, key):
        cur = self.conn.cursor()
        select_key = self.find_key(key, self.TABLE_ACCNT_INFO)
        select_str = ("SELECT " + select_key + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY4_USERNAME + " = ?")

        cur.execute(select_str, (username,))
        value = cur.fetchone()[0]
        cur.close()
        return value

    # Generic updater method for sub info table
    def update_key_sub_info(self, username, key, value):
        cur = self.conn.cursor()
        update_key = self.find_key(key, self.TABLE_SUB_INFO)

        update_str = ("UPDATE " + self.TABLE_SUB_INFO + " SET " + update_key + " = ? "
                      + " WHERE " + self.KEY1_USERNAME + " = ?")
        cur.execute(update_str, (value, username))
        cur.close()

    def wipe_sub_info(self):
        cur = self.conn.cursor()
        delete_str = "DELETE FROM " + self.TABLE_SUB_INFO
        cur.execute(delete_str)
        cur.close()

    # Turn string from INI file into a key
    def find_key(self, key, table):
        key = key.lower()
        if table == self.TABLE_SUB_INFO:
            if key == "ratelimit start":
                return self.KEY1_RATELIMIT_START
            if key == "ratelimit count":
                return self.KEY1_RATELIMIT_COUNT
            if key == "flair text":
                return self.KEY1_FLAIR_TEXT
            if key == "last updated":
                return self.KEY1_LAST_UPDATED
            if key == "flair perm":
                return self.KEY1_FLAIR_PERM
            if key == "css perm":
                return self.KEY1_CSS_PERM
            if key == "text perm":
                return self.KEY1_TEXT_PERM
            if key == "custom flair used":
                return self.KEY1_CUSTOM_FLAIR_USED
            if key == "custom text used":
                return self.KEY1_CUSTOM_TEXT_USED
            if key == "custom css used":
                return self.KEY1_CUSTOM_CSS_USED
            if key == "no auto flair":
                return self.KEY1_NO_AUTO_FLAIR

        elif table == self.TABLE_SUB_ACTIVITY:
            if key == "sub name":
                return self.KEY2_SUB_NAME
            if key == "positive qc":
                return self.KEY2_POSITIVE_QC
            if key == "negative qc":
                return self.KEY2_NEGATIVE_QC

        elif table == self.TABLE_ACCNT_ACTIVITY:
            if key == "sub name":
                return self.KEY3_SUB_NAME
            if key == "positive posts":
                return self.KEY3_POSITIVE_POSTS
            if key == "negative posts":
                return self.KEY3_NEGATIVE_POSTS
            if key == "positive comments":
                return self.KEY3_POSITIVE_COMMENTS
            if key == "negative comments":
                return self.KEY3_NEGATIVE_COMMENTS
            if key == "post karma":
                return self.KEY3_POST_KARMA
            if key == "comment karma":
                return self.KEY3_COMMENT_KARMA

        elif table == self.TABLE_ACCNT_INFO:
            if key == "date created":
                return self.KEY4_DATE_CREATED
            if key == "total post karma":
                return self.KEY4_POST_KARMA
            if key == "total comment karma":
                return self.KEY4_COMMENT_KARMA
            if key == "last scraped":
                return self.KEY4_LAST_SCRAPED

        else:
            logging.critical("Could not find a match for key in the given table"
                             "\nKey: " + key + "\tTable:" + table)
            return None
