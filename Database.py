import sqlite3


class Database:
    # Account Info Table
    TABLE_ACCNT_INFO = "accnt_info"
    KEY1_USERNAME = "username"
    KEY1_DATE_CREATED = "date_created"
    KEY1_RATELIMIT_START = "ratelimit_start"
    KEY1_RATELIMIT_COUNT = "ratelimit_count"
    KEY1_POST_KARMA = "total_post_karma"
    KEY1_COMMENT_KARMA = "total_comment_karma"
    KEY1_FLAIR_TEXT = "flair_text"
    KEY1_LAST_SCRAPED = "last_scraped"
    KEY1_PERMISSIONS = "permissions"
    CREATE_ACCNT_INFO = ("CREATE TABLE IF NOT EXISTS " + TABLE_ACCNT_INFO + " (" +
                         KEY1_USERNAME + " TEXT PRIMARY KEY, " + KEY1_DATE_CREATED + " INTEGER, " +
                         KEY1_RATELIMIT_START + " INTEGER, " + KEY1_RATELIMIT_COUNT + " INTEGER, " +
                         KEY1_POST_KARMA + " INTEGER, " + KEY1_COMMENT_KARMA + " INTEGER, " +
                         KEY1_FLAIR_TEXT + " TEXT, " + KEY1_LAST_SCRAPED + " INTEGER, " +
                         KEY1_PERMISSIONS + " TEXT" +
                         ")")
    
    # Account Activity Table
    TABLE_ACCNT_ACTIVITY = "accnt_history"
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
    CREATE_ACCNT_HISTORY = ("CREATE TABLE IF NOT EXISTS " + TABLE_ACCNT_ACTIVITY + " (" +
                            KEY2_USERNAME + " TEXT, " + KEY2_SUB_NAME + " TEXT, " +
                            KEY2_POSITIVE_POSTS + " INTEGER, " + KEY2_NEGATIVE_POSTS + " INTEGER, " +
                            KEY2_POSITIVE_COMMENTS + " INTEGER, " + KEY2_NEGATIVE_COMMENTS + " INTEGER, " +
                            KEY2_POSITIVE_QC + " INTEGER, " + KEY2_NEGATIVE_QC + " INTEGER, " +
                            KEY2_POST_KARMA + " INTEGER, " + KEY2_COMMENT_KARMA + " INTEGER" +
                            ")")
    
    # Create tables if needed
    def __init__(self, folder_name):
        self.conn = sqlite3.connect(folder_name + "/master_databank.db", isolation_level=None)
        cur = self.conn.cursor()
        cur.execute(self.CREATE_ACCNT_INFO)
        cur.execute(self.CREATE_ACCNT_HISTORY)
        cur.close()
    
    # Check if a user exists in the database
    def exists_in_db(self, username):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY1_USERNAME + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")
        
        exists = False
        for _ in cur.execute(select_str, (username,)):
            exists = True
            break
        cur.close()
        return exists
    
    # Insert user data into Account Info table
    def insert_info(self, username, created, ratelimit_start, ratelimit_count, total_post_karma,
                    total_comment_karma, flair_txt, last_scraped, permissions):
        
        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_ACCNT_INFO + "(" + self.KEY1_USERNAME + ", "
                      + self.KEY1_DATE_CREATED + ", " + self.KEY1_RATELIMIT_START + ", "
                      + self.KEY1_RATELIMIT_COUNT + ", " + self.KEY1_POST_KARMA + ", "
                      + self.KEY1_COMMENT_KARMA + ", " + self.KEY1_FLAIR_TEXT + ", "
                      + self.KEY1_LAST_SCRAPED + ", " + self.KEY1_PERMISSIONS + ") "
                      + "VALUES(?,?,?,?,?,?,?,?,?)")
        
        cur.execute(insert_str, (username, created, ratelimit_start, ratelimit_count, total_post_karma,
                                 total_comment_karma, flair_txt, last_scraped, permissions))
        cur.close()
    
    # Update existing user's data in Account Info table
    def update_info(self, username, ratelimit_start, ratelimit_count, total_post_karma,
                    total_comment_karma, flair_txt, last_scraped):
        
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_ACCNT_INFO
                      + " SET " + self.KEY1_RATELIMIT_START + " = ?, " + self.KEY1_RATELIMIT_COUNT + " = ?, "
                      + self.KEY1_POST_KARMA + " = ?, " + self.KEY1_COMMENT_KARMA + " = ?, "
                      + self.KEY1_FLAIR_TEXT + " = ?, " + self.KEY1_LAST_SCRAPED + " = ? "
                      + "WHERE " + self.KEY1_USERNAME + " = ?")
        
        cur.execute(update_str, (ratelimit_start, ratelimit_count, total_post_karma,
                                 total_comment_karma, flair_txt, last_scraped, username))
        cur.close()

    # Insert user data into Account History table
    def insert_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments, sub_pos_qc, sub_neg_qc,
                        sub_post_karma, sub_pos_posts, sub_neg_posts):
        
        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_ACCNT_ACTIVITY + "("
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
    def update_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments, sub_pos_qc, sub_neg_qc,
                        sub_post_karma, sub_pos_posts, sub_neg_posts):
        
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_ACCNT_ACTIVITY + " SET "
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
    
    # Generic getter method for Account Info table
    def fetch_info_table(self, username, key):
        select_key = self.find_key(key, self.TABLE_ACCNT_INFO)
        cur = self.conn.cursor()
        select_str = ("SELECT " + select_key + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")
        
        cur.execute(select_str, (username,))
        value = cur.fetchone()[0]
        cur.close()
        return value
    
    # Generic getter method for Account History table
    def fetch_hist_table(self, username, sub_list, key):
        select_key = self.find_key(key, self.TABLE_ACCNT_ACTIVITY)
        cur = self.conn.cursor()
        
        # Sum all rows belonging to the user
        if sub_list == "ALL":
            select_str = ("SELECT SUM(" + select_key + ") FROM " + self.TABLE_ACCNT_ACTIVITY
                          + " WHERE " + self.KEY2_USERNAME + " = ?")

            cur.execute(select_str, (username,))
            data = cur.fetchone()
            if data is not None:
                return data[0]
            else:
                return None

        # Sum only the specified rows (subreddits)
        else:
            select_str = ("SELECT " + select_key + " FROM " + self.TABLE_ACCNT_ACTIVITY
                          + " WHERE " + self.KEY2_USERNAME + " = ? AND "
                          + self.KEY2_SUB_NAME + " = ?")
            
            value = 0
            for sub in sub_list:
                cur.execute(select_str, (username, sub))
                data = cur.fetchone()
                if data is not None:
                    value += data[0]
            return value
        
    # Update a user's permissions
    def update_perm(self, username, permission):
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_ACCNT_INFO + " SET " + self.KEY1_PERMISSIONS
                      + " = ? WHERE " + self.KEY1_USERNAME + " = ?")
        
        cur.execute(update_str, (permission, username))
        cur.close()
        
    # Update a user's flair txt
    def update_flair(self, username, flair):
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_ACCNT_INFO + " SET " + self.KEY1_FLAIR_TEXT
                      + " = ? WHERE " + self.KEY1_USERNAME + " = ?")
    
        cur.execute(update_str, (flair, username))
        cur.close()
    
    # Turn string from INI file into a key
    def find_key(self, key, table):
        key = key.lower()
        if table == self.TABLE_ACCNT_INFO:
            if key == "date created":
                return self.KEY1_DATE_CREATED
            elif key == "ratelimit start":
                return self.KEY1_RATELIMIT_START
            elif key == "ratelimit count":
                return self.KEY1_RATELIMIT_COUNT
            elif key == "total post karma":
                return self.KEY1_COMMENT_KARMA
            elif key == "total comment karma":
                return self.KEY1_POST_KARMA
            elif key == "flair text":
                return self.KEY1_FLAIR_TEXT
            elif key == "last scraped":
                return self.KEY1_LAST_SCRAPED
            elif key == "permissions":
                return self.KEY1_PERMISSIONS
        
        elif table == self.TABLE_ACCNT_ACTIVITY:
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
    
    # Test method pls ignore
    def print_all_users(self, username, subname):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY2_COMMENT_KARMA + " FROM " + self.TABLE_ACCNT_ACTIVITY
                      + " WHERE " + self.KEY2_USERNAME + " = ? AND "
                      + self.KEY2_SUB_NAME + " = ?")
        
        for row in cur.execute(select_str, (username, subname)):
            print(row)
        cur.close()
