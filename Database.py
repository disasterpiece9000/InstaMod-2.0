import sqlite3


class Database:
    TABLE_ACCNT_INFO = "accnt_info"
    KEY1_USERNAME = "username"
    KEY1_DATE_CREATED = "date_created"
    KEY1_RATELIMIT_START = "ratelimit_start"
    KEY1_RATELIMIT_COUNT = "ratelimit_count"
    KEY1_POST_KARMA = "total_post_karma"
    KEY1_COMMENT_KARMA = "total_comment_karma"
    KEY1_FLAIR_TEXT = "flair_text"
    KEY1_LAST_SCRAPED = "last_scraped"
    CREATE_ACCNT_INFO = ("CREATE TABLE IF NOT EXISTS " + TABLE_ACCNT_INFO + " (" +
                         KEY1_USERNAME + " TEXT PRIMARY KEY, " + KEY1_DATE_CREATED + " INTEGER, " +
                         KEY1_RATELIMIT_START + " INTEGER, " + KEY1_RATELIMIT_COUNT + " INTEGER, " +
                         KEY1_POST_KARMA + " INTEGER, " + KEY1_COMMENT_KARMA + " INTEGER, " +
                         KEY1_FLAIR_TEXT + " TEXT, " + KEY1_LAST_SCRAPED + " INTEGER" +
                         ")")
    
    TABLE_ACCNT_HISTORY = "accnt_history"
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
    CREATE_ACCNT_HISTORY = ("CREATE TABLE IF NOT EXISTS " + TABLE_ACCNT_HISTORY + " (" +
                            KEY2_USERNAME + " TEXT, " + KEY2_SUB_NAME + " TEXT, " +
                            KEY2_POSITIVE_POSTS + " INTEGER, " + KEY2_NEGATIVE_POSTS + " INTEGER, " +
                            KEY2_POSITIVE_COMMENTS + " INTEGER, " + KEY2_NEGATIVE_COMMENTS + " INTEGER, " +
                            KEY2_POSITIVE_QC + " INTEGER, " + KEY2_NEGATIVE_QC + " INTEGER, " +
                            KEY2_POST_KARMA + " INTEGER, " + KEY2_COMMENT_KARMA + " INTEGER" +
                            ")")
    
    def __init__(self, sub_name):
        self.conn = sqlite3.connect(sub_name + "/master_databank.db", isolation_level=None)
        cur = self.conn.cursor()
        cur.execute(self.CREATE_ACCNT_INFO)
        cur.execute(self.CREATE_ACCNT_HISTORY)
        cur.close()
    
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
    
    def insert_info(self, username, created, ratelimit_start, ratelimit_count, total_post_karma,
                    total_comment_karma, flair_txt, last_scraped):
    
        if flair_txt is not None:
            print("Flair Text: " + flair_txt)
        else:
            print("Flair Text: n/a")
        print("Last Scraped: " + str(last_scraped) + "\n")
        
        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_ACCNT_INFO + "(" + self.KEY1_USERNAME + ", "
                      + self.KEY1_DATE_CREATED + ", " + self.KEY1_RATELIMIT_START + ", "
                      + self.KEY1_RATELIMIT_COUNT + ", " + self.KEY1_POST_KARMA + ", "
                      + self.KEY1_COMMENT_KARMA + ", " + self.KEY1_FLAIR_TEXT + ", "
                      + self.KEY1_LAST_SCRAPED + ") "
                      + "VALUES(?,?,?,?,?,?,?,?)")
        
        cur.execute(insert_str, (username, created, ratelimit_start, ratelimit_count, total_post_karma,
                    total_comment_karma, flair_txt, last_scraped))
        cur.close()
        print("Done inserting into accnt_info\n")
        
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
        print("Done updating accnt_info\n")
        
    def insert_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments, sub_pos_qc, sub_neg_qc,
                        sub_post_karma, sub_pos_posts, sub_neg_posts):
        
        cur = self.conn.cursor()
        insert_str = ("INSERT INTO " + self.TABLE_ACCNT_HISTORY + "("
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
        print("Done inserting into accnt_activity\n")
        
    def update_activity(self, username, sub_comment_karma, sub_pos_comments, sub_neg_comments, sub_pos_qc, sub_neg_qc,
                        sub_post_karma, sub_pos_posts, sub_neg_posts):
        
        cur = self.conn.cursor()
        update_str = ("UPDATE " + self.TABLE_ACCNT_HISTORY + " SET "
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
        print("Done updating accnt_activity\n")
        
    def get_last_scraped(self, username):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY1_LAST_SCRAPED + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY1_USERNAME + "=?")
        
        scrape_time = cur.execute(select_str, (username,)).fetchone()[0]
        cur.close()
        return scrape_time
    
    def get_total_comment_karma(self, username):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY1_COMMENT_KARMA + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")
        
        cur.execute(select_str, (username,))
        value = cur.fetchone()[0]
        cur.close()
        return value

    def get_total_post_karma(self, username):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY1_POST_KARMA + " FROM " + self.TABLE_ACCNT_INFO
                      + " WHERE " + self.KEY1_USERNAME + " = ?")
    
        cur.execute(select_str, (username,))
        value = cur.fetchone()[0]
        cur.close()
        return value
    
    def get_comment_karma(self, username, sub_list):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY2_COMMENT_KARMA + " FROM " + self.TABLE_ACCNT_HISTORY
                      + " WHERE " + self.KEY2_USERNAME + " = ? AND "
                      + self.KEY2_SUB_NAME + " = ?")
        
        value = 0
        for sub in sub_list:
            sub = sub.lower()
            cur.execute(select_str, (username, sub))
            data = cur.fetchone()
            if data is not None:
                value += data[0]
        print(str(value))
        return value
    
    def print_all_users(self, username, subname):
        cur = self.conn.cursor()
        select_str = ("SELECT " + self.KEY2_COMMENT_KARMA + " FROM " + self.TABLE_ACCNT_HISTORY
                      + " WHERE " + self.KEY2_USERNAME + " = ? AND "
                      + self.KEY2_SUB_NAME + " = ?")
        
        for row in cur.execute(select_str, (username, subname)):
            print(row)
        cur.close()
