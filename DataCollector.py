from collections import Counter
from datetime import datetime
import time
import logging
from psaw import PushshiftAPI

# PushShift Instance
ps = PushshiftAPI()


def load_data(user_in_accnt_info, user_in_sub_info, update_flair, comment, sub):
    # General account info
    author = comment.author
    username = str(author).lower()
    created = author.created_utc
    total_post_karma = author.link_karma
    total_comment_karma = author.comment_karma
    flair_txt = next(sub.sub.flair(username))["flair_text"]
    last_scraped = int(time.time())
    
    # Temp values for postponed ratelimit feature
    ratelimit_count = 0
    ratelimit_start = int(time.time())
    
    if user_in_sub_info:
        # Flair will be updated now
        if update_flair:
            last_updated = int(time.time())
        # Flair is not expired yet - keep old "last updated" value
        else:
            last_updated = sub.db.fetch_sub_info(username, "last updated")
        
        sub.db.update_row_sub_info(username, ratelimit_start, ratelimit_count, flair_txt, last_updated)
    else:
        last_updated = last_scraped
        sub.db.insert_sub_info(username, ratelimit_start, ratelimit_count, flair_txt, last_updated)
    
    if user_in_accnt_info:
        # Get comments/posts that occurred after the last scrape
        after_time = sub.db.fetch_accnt_info(username, "last scraped")
        
        # Update database entries
        sub.db.update_accnt_info(username, total_post_karma, total_comment_karma, last_scraped)
    else:
        # Get all available comments/posts (up to 1,000 each)
        after_time = int(datetime(2000, 1, 1).timestamp())
        # Insert data into accnt_info table
        sub.db.insert_accnt_info(username, created, total_post_karma, total_comment_karma, last_scraped)
    
    # Account Activity Table
    # Comments
    
    # Sleep for 1 sec to avoid ratelimit
    #time.sleep(2)
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
        # Check that all data was returned
        data = comment[len(comment) - 1]
        post_data_valid = False
        try:
            if None not in [data["id"], data["score"], data["subreddit"], data["body"]]:
                post_data_valid = True
        except KeyError:
            logging.debug("PSAW didn't return some parameters in post_results: " + str(data))
            continue
            
        if not post_data_valid:
            continue
            
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
        if sub.qc_config["positive word count"] != "":
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
        if sub.qc_config["negative score"] != "":
            neg_qc_score = score <= int(sub.qc_config["negative score"])
        else:
            neg_qc_score = True
        
        # Negative QC: Word Count
        if sub.qc_config["negative word count"] != "":
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
    
    # Sleep for 1 sec to avoid ratelimit
    #time.sleep(2)
    # Posts
    post_results = ps.search_submissions(author=author,
                                         after=after_time,
                                         filter=["id", "score", "subreddit"],
                                         limit=1000)
    sub_post_karma = Counter()
    sub_pos_posts = Counter()
    sub_neg_posts = Counter()
    
    for post in post_results:
        # Check that all data was returned
        data = post[len(post) - 1]
        post_data_valid = False
        try:
            if None not in [data["subreddit"], data["score"], data["id"]]:
                post_data_valid = True
        except KeyError:
            logging.debug("PSAW didn't return some parameters in post_results: " + str(data))
            continue
            
        if not post_data_valid:
            continue
        
        score = data["score"]
        subreddit = data["subreddit"].lower()
        
        sub_post_karma[subreddit] += score
        if score > 0:
            sub_pos_posts[subreddit] += 1
        else:
            sub_neg_posts[subreddit] += 1
    
    if user_in_accnt_info:
        sub.db.update_sub_activity(username, sub_comment_karma, sub_pos_comments, sub_neg_comments,
                                   sub_pos_qc, sub_neg_qc, sub_post_karma, sub_pos_posts, sub_neg_posts)
    else:
        sub.db.insert_sub_activity(username, sub_comment_karma, sub_pos_comments, sub_neg_comments,
                                   sub_pos_qc, sub_neg_qc, sub_post_karma, sub_pos_posts, sub_neg_posts)
        
    # Check if user is now in all 3 tables
    accnt = sub.db.exists_in_accnt_info(username)
    sub = sub.db.exists_in_sub_info(username)
    

def count_words(body):
    body_list = body.split()
    return len(body_list)
