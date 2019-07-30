import sqlite3


# TODO: Fix all method calls that are broken by these changes lol


class Database:
    # Subreddit Info Table
    TABLE_SUB_INFO = "sub_info"
    KEY1_USERNAME = "username"
    KEY1_RATELIMIT_START = "ratelimit_start"
    KEY1_RATELIMIT_COUNT = "ratelimit_count"
    KEY1_FLAIR_TEXT = "flair_text"
    KEY1_LAST_UPDATED = "last_updated"
    KEY1_PERMISSIONS = "permissions"
    CREATE_SUB_INFO = ("CREATE TABLE IF NOT EXISTS " + TABLE_SUB_INFO + " (" +
                       KEY1_USERNAME + " TEXT PRIMARY KEY, " + KEY1_RATELIMIT_START + " INTEGER, " +
                       KEY1_RATELIMIT_COUNT + " INTEGER, " + KEY1_FLAIR_TEXT + " TEXT, " +
                       KEY1_LAST_UPDATED + " INTEGER, " + KEY1_PERMISSIONS + " TEXT" +
                       ")")
    
    # Subreddit Activity Table
    TABLE_SUB_ACTIVITY = "sub_activity"
    KEY2_USERNAME = "username"
    KEY2_SUB_NAME = "sub_name"
    KEY2_POSITIVE_POSTS = "positive_posts"
    KEY2_NEGATIVE_POSTS = "negative_posts"
    KEY2_POSITIVE_COMMENTS = "positive_comments"
    KEY2_NEGATIVE_COMMENTS = "negative_comments"
    KEY2_POSITIVE_QC = "positive_qc"
    KEY2_NEGATIVE_QC = "negative_qc"
    KEY2_POST_KARMA = "post_karma"
    KEY2_COMMENT_KARMA = "comment_karma"
    CREATE_SUB_ACTIVITY = ("CREATE TABLE IF NOT EXISTS " + TABLE_SUB_ACTIVITY + " (" +
                           KEY2_USERNAME + " TEXT, " + KEY2_SUB_NAME + " TEXT, " +
                           KEY2_POSITIVE_POSTS + " INTEGER, " + KEY2_NEGATIVE_POSTS + " INTEGER, " +
                           KEY2_POSITIVE_COMMENTS + " INTEGER, " + KEY2_NEGATIVE_COMMENTS + " INTEGER, " +
                           KEY2_POSITIVE_QC + " INTEGER, " + KEY2_NEGATIVE_QC + " INTEGER, " +
                           KEY2_POST_KARMA + " INTEGER, " + KEY2_COMMENT_KARMA + " INTEGER" +
                           ")")
    
    # Account Information Table
    TABLE_ACCNT_INFO = "accnt_info"
    KEY3_USERNAME = "username"
    KEY3_DATE_CREATED = "date_created"
    KEY3_POST_KARMA = "total_post_karma"
    KEY3_COMMENT_KARMA = "total_comment_karma"
    KEY3_LAST_SCRAPED = "last_scraped"
    CREATE_ACCNT_INFO = ("CREATE TABLE IF NOT EXISTS " + TABLE_ACCNT_INFO + " (" +
                         KEY3_USERNAME + " TEXT, " + KEY3_DATE_CREATED + " INTEGER, " +
                         KEY3_POST_KARMA + " INTEGER, " + KEY3_COMMENT_KARMA + " INTEGER, " +
                         KEY3_LAST_SCRAPED + " INTEGER" +
                         ")")
    
    #
    
    # Create tables if needed
    def __init__(self, folder_name):
        # Connect to all tables
        self.sub_info_conn = sqlite3.connect(folder_name + "/sub_databank.db", isolation_level=None,
                                             check_same_thread=False)
        sub_info_cur = self.sub_info_conn.cursor()
        self.sub_activity = sqlite3.connect("master_databank.db", isolation_level=None, check_same_thread=False)
        sub_activity_cur = self.sub_activity.cursor()
        self.accnt_info = sqlite3.connect("master_databank.db", isolation_level=None, check_same_thread=False)
        accnt_info_cur = self.accnt_info.cursor()
        
        # Create tables if necessary
        sub_info_cur.execute(self.CREATE_SUB_INFO)
        sub_activity_cur.execute(self.CREATE_SUB_ACTIVITY)
        accnt_info_cur.execute(self.CREATE_ACCNT_INFO)
        
        sub_info_cur.close()
        sub_activity_cur.close()
        accnt_info_cur.close()
    
    # Check if a user exists in the database
    def exists_in_db(self, username):
        cur = self.sub_activity.cursor()
        select_str = ("SELECT " + self.KEY1_USERNAME + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")
        
        cur.execute(select_str, (username,))
        data = cur.fetchone()
        if data:
            return True
        else:
            return False
    
    # Insert user data into Sub Info table
    def insert_sub_info(self, username, ratelimit_start, ratelimit_count, flair_txt, last_updated, permissions):
        
        cur = self.sub_info_conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_SUB_INFO + "(" + self.KEY1_USERNAME + ", "
                      + self.KEY1_RATELIMIT_START + ", " + self.KEY1_RATELIMIT_COUNT + ", "
                      + self.KEY1_FLAIR_TEXT + ", " + self.KEY1_LAST_UPDATED + ", "
                      + self.KEY1_PERMISSIONS + ") "
                      + "VALUES(?,?,?,?,?,?)")
        
        cur.execute(insert_str, (username, ratelimit_start, ratelimit_count, flair_txt, last_updated, permissions))
        cur.close()
    
    # Update existing user's data in Sub Info table
    def update_sub_info(self, username, ratelimit_start, ratelimit_count, flair_txt, last_updated):
        
        cur = self.sub_info_conn.cursor()
        update_str = ("UPDATE " + self.TABLE_SUB_INFO
                      + " SET " + self.KEY1_RATELIMIT_START + " = ?, " + self.KEY1_RATELIMIT_COUNT + " = ?, "
                      + self.KEY1_FLAIR_TEXT + " = ?, " + self.KEY1_LAST_UPDATED + " = ? "
                      + "WHERE " + self.KEY1_USERNAME + " = ?")
        
        cur.execute(update_str, (ratelimit_start, ratelimit_count, flair_txt, last_updated, username))
        cur.close()
    
    # Insert user data into Account History table
    def insert_sub_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments, sub_pos_qc,
                            sub_neg_qc, sub_post_karma, sub_pos_posts, sub_neg_posts):
        
        cur = self.sub_activity.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_SUB_ACTIVITY + "("
                      + self.KEY2_USERNAME + ", " + self.KEY2_SUB_NAME + ", "
                      + self.KEY2_POSITIVE_POSTS + ", " + self.KEY2_NEGATIVE_POSTS + ", "
                      + self.KEY2_POSITIVE_COMMENTS + ", " + self.KEY2_NEGATIVE_COMMENTS + ", "
                      + self.KEY2_POSITIVE_QC + ", " + self.KEY2_NEGATIVE_QC + ", "
                      + self.KEY2_POST_KARMA + ", " + self.KEY2_COMMENT_KARMA + ") "
                      + "VALUES(?,?,?,?,?,?,?,?,?,?)")
        
        # Union of all keys in both primary dictionaries
        all_subs = sub_comment_karma.keys() | sub_post_karma
        for sub in all_subs:
            cur.execute(insert_str, (username, sub, sub_pos_posts[sub], sub_neg_posts[sub],
                                     sub_pos_comments[sub], sub_neg_comments[sub],
                                     sub_pos_qc[sub], sub_neg_qc[sub],
                                     sub_post_karma[sub], sub_comment_karma[sub]))
        
        cur.close()
    
    # Update existing user's data in Account History table
    def update_sub_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments, sub_pos_qc,
                            sub_neg_qc, sub_post_karma, sub_pos_posts, sub_neg_posts):
        
        cur = self.sub_activity.cursor()
        update_str = ("UPDATE " + self.TABLE_SUB_ACTIVITY + " SET "
                      + self.KEY2_COMMENT_KARMA + " = " + self.KEY2_COMMENT_KARMA + "+ ?, "
                      + self.KEY2_POSITIVE_COMMENTS + " = " + self.KEY2_POSITIVE_COMMENTS + "+ ?, "
                      + self.KEY2_NEGATIVE_COMMENTS + " = " + self.KEY2_NEGATIVE_COMMENTS + "+ ?, "
                      + self.KEY2_POSITIVE_QC + " = " + self.KEY2_POSITIVE_QC + "+ ?, "
                      + self.KEY2_NEGATIVE_QC + " = " + self.KEY2_NEGATIVE_QC + "+ ?, "
                      + self.KEY2_POST_KARMA + " = " + self.KEY2_POST_KARMA + "+ ?, "
                      + self.KEY2_POSITIVE_POSTS + " = " + self.KEY2_POSITIVE_POSTS + "+ ?, "
                      + self.KEY2_NEGATIVE_POSTS + " = " + self.KEY2_NEGATIVE_POSTS + "+ ? "
                      + "WHERE " + self.KEY2_USERNAME + " = ?")
        
        # Union of all keys in both primary dictionaries
        all_subs = sub_comment_karma.keys() | sub_post_karma
        for sub in all_subs:
            cur.execute(update_str, (sub_comment_karma[sub], sub_pos_comments[sub], sub_neg_comments[sub],
                                     sub_pos_qc[sub], sub_neg_qc[sub], sub_post_karma[sub],
                                     sub_pos_posts[sub], sub_neg_posts[sub], username))
        
        cur.close()
        
    # Insert user data into Account Info table
    def insert_accnt_info(self, username, created, total_post_karma, total_comment_karma, last_scraped):
        cur = self.accnt_info.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_ACCNT_INFO + "("
                      + self.KEY3_USERNAME + ", " + self.KEY3_DATE_CREATED + ", "
                      + self.KEY3_POST_KARMA + ", " + self.KEY3_COMMENT_KARMA + ", "
                      + self.KEY3_LAST_SCRAPED + ") "
                      + "VALUES(?,?,?,?,?)")
        
        cur.execute(insert_str, (username, created, total_post_karma, total_comment_karma, last_scraped))
        cur.close()
        
    # Update user data in Account Info table
    def update_accnt_info(self, username, post_karma, comment_karma, last_scraped):
        cur = self.accnt_info.cursor()
        update_str = ("UPDATE " + self.TABLE_ACCNT_INFO + " SET "
                      + self.KEY3_POST_KARMA + " = ?, " + self.KEY3_COMMENT_KARMA + " = ?, "
                      + self.KEY3_LAST_SCRAPED + " = ? "
                      + "WHERE " + self.KEY3_USERNAME + " = ?")
        
        cur.execute(update_str, (post_karma, comment_karma, last_scraped, username))
    
    # Generic getter method for Account Info table
    def fetch_sub_info(self, username, key):
        select_key = self.find_key(key, self.TABLE_SUB_INFO)
        cur = self.sub_info_conn.cursor()
        select_str = ("SELECT " + select_key + " FROM " + self.TABLE_SUB_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")
        
        cur.execute(select_str, (username,))
        value = cur.fetchone()[0]
        cur.close()
        return value
    
    # Generic getter method for Account History table
    def fetch_sub_activity(self, username, sub_list, key):
        name_list = [data[0] for data in sub_list]
        select_key = self.find_key(key, self.TABLE_SUB_ACTIVITY)
        cur = self.sub_activity.cursor()
        
        # Sum only the specified rows (subreddits)
        select_str = ("SELECT " + select_key + " FROM " + self.TABLE_SUB_ACTIVITY
                      + " WHERE " + self.KEY2_USERNAME + " = ? AND "
                      + self.KEY2_SUB_NAME + " = ?")
        
        value = 0
        for name in name_list:
            cur.execute(select_str, (username, name))
            data = cur.fetchone()
            if data is not None:
                value += data[0]
        return value
    
    # Generic getter method for Account Info table
    def fetch_accnt_info(self, username, key):
        cur = self.accnt_info.cursor()
        select_key = self.find_key(key, self.TABLE_ACCNT_INFO)
        select_str = ("SELECT " + select_key + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY3_USERNAME + " = ?")
        
        cur.execute(select_str, (username,))
        value = cur.fetchone()[0]
        cur.close()
        return value
    
    # Get a list of all subreddits the user has a history in
    def get_all_subs(self, username):
        cur = self.sub_activity.cursor()
        select_str = ("SELECT " + self.KEY2_SUB_NAME + " FROM " + self.TABLE_SUB_ACTIVITY
                      + " WHERE " + self.KEY2_USERNAME + " = ?")
        cur.execute(select_str, (username,))
        rows = cur.fetchall()
        
        return [row[0] for row in rows]
    
    # Update a user's permissions
    def update_perm(self, username, permission):
        cur = self.sub_info_conn.cursor()
        update_str = ("UPDATE " + self.TABLE_SUB_INFO + " SET " + self.KEY1_PERMISSIONS
                      + " = ? WHERE " + self.KEY1_USERNAME + " = ?")
        
        cur.execute(update_str, (permission, username))
        cur.close()
    
    # Update a user's flair txt
    def update_flair(self, username, flair):
        cur = self.sub_info_conn.cursor()
        update_str = ("UPDATE " + self.TABLE_SUB_INFO + " SET " + self.KEY1_FLAIR_TEXT
                      + " = ? WHERE " + self.KEY1_USERNAME + " = ?")
        
        cur.execute(update_str, (flair, username))
        cur.close()
    
    # Turn string from INI file into a key
    def find_key(self, key, table):
        key = key.lower()
        if table == self.TABLE_SUB_INFO:
            if key == "ratelimit start":
                return self.KEY1_RATELIMIT_START
            elif key == "ratelimit count":
                return self.KEY1_RATELIMIT_COUNT
            elif key == "flair text":
                return self.KEY1_FLAIR_TEXT
            elif key == "last scraped":
                return self.KEY1_LAST_UPDATED
            elif key == "permissions":
                return self.KEY1_PERMISSIONS
        
        elif table == self.TABLE_SUB_ACTIVITY:
            if key == "sub name":
                return self.KEY2_SUB_NAME
            if key == "positive posts":
                return self.KEY2_POSITIVE_POSTS
            if key == "negative posts":
                return self.KEY2_NEGATIVE_POSTS
            if key == "positive comments":
                return self.KEY2_POSITIVE_COMMENTS
            if key == "negative comments":
                return self.KEY2_NEGATIVE_COMMENTS
            if key == "positive qc":
                return self.KEY2_POSITIVE_QC
            if key == "negative qc":
                return self.KEY2_NEGATIVE_QC
            if key == "post karma":
                return self.KEY2_POST_KARMA
            if key == "comment karma":
                return self.KEY2_COMMENT_KARMA
            
            elif table == self.TABLE_ACCNT_INFO:
                if key == "date created":
                    return self.KEY3_DATE_CREATED
                elif key == "total post karma":
                    return self.KEY3_POST_KARMA
                elif key == "total comment karma":
                    return self.KEY3_COMMENT_KARMA
                elif key == "last scraped":
                    return self.KEY3_LAST_SCRAPED
            
            else:
                print("Could not find a match for key in the given table"
                      "\nKey: " + key + "\tTable:" + table)
                return None
    
    # Test method pls ignore
    def print_all_users(self, username, sub_name):
        cur = self.sub_activity.cursor()
        select_str = ("SELECT " + self.KEY2_COMMENT_KARMA + " FROM " + self.TABLE_SUB_ACTIVITY
                      + " WHERE " + self.KEY2_USERNAME + " = ? AND "
                      + self.KEY2_SUB_NAME + " = ?")
        
        for row in cur.execute(select_str, (username, sub_name)):
            print(row)
        cur.close()
