from collections import Counter
from datetime import datetime
import time
from psaw import PushshiftAPI

# PushShift Instance
ps = PushshiftAPI()


def get_data(comment, sub):
    user = comment.author
    username = str(user)
    update_flair = False
    user_in_db = sub.db.exists_in_db(username)
    
    # If user has not been seen before, pull all their data
    if not user_in_db:
        print("Getting all data for " + username + "...")
        load_data(False, comment, sub)
        update_flair = True
    # If user is expired, pull all data from after the last scrape
    elif is_expired(comment, sub):
        print("Updating data for " + username + "...")
        load_data(True, comment, sub)
        update_flair = True
    
    return update_flair


def load_data(update, comment, sub):
    # Account Info Table
    author = comment.author
    username = str(author)
    created = author.created_utc
    total_post_karma = author.link_karma
    total_comment_karma = author.comment_karma
    flair_txt = next(sub.sub.flair(username))["flair_text"]
    last_scraped = int(time.time())
    
    # Temp values
    ratelimit_count = 0
    ratelimit_start = int(time.time())
    
    if update:
        after_time = sub.db.get_last_scraped(username)
        sub.db.update_info(username, ratelimit_start, ratelimit_count, total_post_karma,
                           total_comment_karma, flair_txt, last_scraped)
    else:
        after_time = int(datetime(2000, 1, 1).timestamp())
        # Insert data into accnt_info table
        sub.db.insert_info(username, created, ratelimit_start, ratelimit_count, total_post_karma,
                           total_comment_karma, flair_txt, last_scraped)
    
    # Account Activity Table
    # Comments
    comment_results = ps.search_comments(author=author,
                                         after=after_time,
                                         filter=["id", "score", "subreddit", "body"],
                                         limit=1000)
    
    sub_comment_karma = Counter()
    sub_pos_comments = Counter()
    sub_neg_comments = Counter()
    sub_neg_qc = Counter()
    sub_pos_qc = Counter()
    
    for comment in comment_results:
        try:
            data = comment[6]
        except IndexError:
            print(comment)
            return
            
        score = data["score"]
        subreddit = data["subreddit"].lower()
        body = data["body"]
        
        sub_comment_karma[subreddit] += score
        if score > 0:
            sub_pos_comments[subreddit] += 1
        else:
            sub_neg_comments[subreddit] += 1
        
        # Quality Comments
        
        # Positive QC
        # Positive QC: Score
        if sub.qc_config["positive score"] != "None":
            pos_qc_score = score >= int(sub.qc_config["positive score"])
        else:
            pos_qc_score = True
        
        # Positive QC: Word Count
        if sub.qc_config["positive word count"] != "None":
            pos_qc_words = count_words(body) >= int(sub.qc_config["positive word count"])
        else:
            pos_qc_words = True
        
        # Positive QC: Result
        if sub.qc_config["positive criteria type"] == "AND":
            if pos_qc_words and pos_qc_score:
                sub_pos_qc[subreddit] += 1
        else:
            if pos_qc_words or pos_qc_score:
                sub_pos_qc[subreddit] += 1
        
        # Negative QC
        # Negative QC: Score
        if sub.qc_config["negative score"] != "None":
            neg_qc_score = score <= int(sub.qc_config["negative score"])
        else:
            neg_qc_score = True
        
        # Negative QC: Word Count
        if sub.qc_config["negative word count"] != "None":
            neg_qc_words = count_words(body) >= int(sub.qc_config["negative word count"])
        else:
            neg_qc_words = True
        
        # Negative QC: Result
        if sub.qc_config["negative criteria type"] == "AND":
            if neg_qc_words and neg_qc_score:
                sub_neg_qc[subreddit] += 1
        else:
            if neg_qc_words or neg_qc_score:
                sub_neg_qc[subreddit] += 1
    
    # Posts
    post_results = ps.search_submissions(author=author,
                                         after=after_time,
                                         filter=["id", "score", "subreddit"],
                                         limit=1000)
    sub_post_karma = Counter()
    sub_pos_posts = Counter()
    sub_neg_posts = Counter()
    
    for post in post_results:
        try:
            data = post[5]
        except IndexError:
            print(post)
            return
            
        score = data["score"]
        subreddit = data["subreddit"].lower()
        
        sub_post_karma[subreddit] += score
        if score > 0:
            sub_pos_posts[subreddit] += 1
        else:
            sub_neg_posts[subreddit] += 1
            
    if update:
        sub.db.update_activity(username, sub_comment_karma, sub_pos_comments, sub_neg_comments,
                               sub_pos_qc, sub_neg_qc, sub_post_karma, sub_pos_posts, sub_neg_posts)
    else:
        sub.db.insert_activity(username, sub_comment_karma, sub_pos_comments, sub_neg_comments,
                               sub_pos_qc, sub_neg_qc, sub_post_karma, sub_pos_posts, sub_neg_posts)


def is_expired(comment, target_sub):
    last_seen = target_sub.db.get_last_scraped(str(comment.author))
    current_time = int(time.time())
    day_diff = int((current_time - last_seen) / 86400)
    
    print("\nExpired Info:")
    print(str(last_seen))
    print(str(current_time))
    print(str(day_diff) + "\n")
    print(target_sub.flair_config["flair expiration"])
    
    if day_diff >= int(target_sub.flair_config["flair expiration"]):
        return True
    else:
        return False


def count_words(body):
    body_list = body.split()
    return len(body_list)

