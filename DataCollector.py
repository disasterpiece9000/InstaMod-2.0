import logging
import time
from collections import Counter
from datetime import datetime
from datetime import timedelta

from psaw import PushshiftAPI


def load_data(user_in_accnt_info, user_in_sub_info, update_flair, author, target_sub, sub_list, r):
    # PushShift Instance
    ps = PushshiftAPI(r)

    # General info
    username = str(author).lower()
    total_post_karma = author.link_karma
    total_comment_karma = author.comment_karma
    flair_txt = next(target_sub.sub.flair(username))["flair_text"]
    last_scraped = int(time.time())

    # Skip comments and posts that are not at least 1 week old
    before_time = int((datetime.today() - timedelta(days=7)).timestamp())

    # Temp values for postponed ratelimit feature
    ratelimit_count = 0
    ratelimit_start = int(time.time())

    # TODO: Figure out why/how this happens and catch it earlier on
    try:
        created = author.created_utc
    except AttributeError:
        logging.warning("The user " + username + " could not have their account info gathered")
        return

    # Get list of subreddits that the user does/doesn't exist in
    exists_in_sub = []
    not_exists_in_sub = []
    for sub in sub_list:
        if sub.db.exists_in_sub_info(username):
            exists_in_sub.append(sub.name)
        else:
            not_exists_in_sub.append(sub.name)

    # Check if user exists in all subreddits
    if user_in_accnt_info:
        if len(not_exists_in_sub) > 0:
            # Get all available comments/posts (up to 1,000 each)
            after_time = int(datetime(2000, 1, 1).timestamp())

            # Drop all user activity info to prepare for re-insert
            target_sub.db.partial_drop_user(username)

            # Re-insert accnt info
            target_sub.db.insert_accnt_info(username, created, total_post_karma, total_comment_karma, last_scraped)

            # Re-insert sub info for subs that do not have user
            user_in_sub_info = True
            for sub in sub_list:
                if not sub.db.exists_in_sub_info(username):
                    info_flair_txt = next(sub.sub.flair(username))["flair_text"]
                    sub.db.insert_sub_info(username, ratelimit_start, ratelimit_count, info_flair_txt, after_time)

        else:
            # Get comments/posts that occurred after the last scrape
            after_time = target_sub.db.fetch_accnt_info(username, "last scraped")

            # Update database entries
            target_sub.db.update_accnt_info(username, total_post_karma, total_comment_karma, last_scraped)
    else:
        # Get all available comments/posts (up to 1,000 each)
        after_time = int(datetime(2000, 1, 1).timestamp())
        # Insert data into accnt_info table
        target_sub.db.insert_accnt_info(username, created, total_post_karma, total_comment_karma, last_scraped)

    # Update target sub info data
    if user_in_sub_info:
        # Flair will be updated now
        if update_flair:
            last_updated = int(time.time())
        # Flair is not expired yet - keep old "last updated" value
        else:
            last_updated = target_sub.db.fetch_sub_info(username, "last updated")

        target_sub.db.update_row_sub_info(username, ratelimit_start, ratelimit_count, flair_txt, last_updated)
    # Insert user data in to target sub info
    else:
        last_updated = last_scraped
        target_sub.db.insert_sub_info(username, ratelimit_start, ratelimit_count, flair_txt, last_updated)

    # Comments

    comment_results = ps.search_comments(author=author,
                                         after=after_time,
                                         before=before_time,
                                         filter=["id", "score", "subreddit", "body", "is_submitter"], )

    # Account Activity Table
    sub_comment_karma = Counter()
    sub_pos_comments = Counter()
    sub_neg_comments = Counter()

    # Sub Activity Table
    all_neg_qc = {}
    all_pos_qc = {}

    # Create dict to store each subreddit's unique QC
    for sub in sub_list:
        all_neg_qc[sub.name] = Counter()
        all_pos_qc[sub.name] = Counter()

    for ps_comment in comment_results:

        score = ps_comment.score
        subreddit = str(ps_comment.subreddit).lower()
        body = ps_comment.body
        is_submitter = ps_comment.is_submitter

        sub_comment_karma[subreddit] += score
        if score > 0:
            sub_pos_comments[subreddit] += 1
        else:
            sub_neg_comments[subreddit] += 1

        # Quality Comments

        # Calculate each subreddit's unique QC value
        for qc_sub in sub_list:
            # Skip if author is OP
            if qc_sub.qc_config.getboolean("exclude when op") and is_submitter:
                continue

            # Positive QC
            # Positive QC: Score
            if qc_sub.qc_config["positive score"] != "None":
                pos_qc_score = score >= int(qc_sub.qc_config["positive score"])
            else:
                pos_qc_score = True

            # Positive QC: Word Count
            if qc_sub.qc_config["positive word count"] != "":
                pos_qc_words = count_words(body) >= int(qc_sub.qc_config["positive word count"])
            else:
                pos_qc_words = True

            # Positive QC: Result
            # AND criteria
            if qc_sub.qc_config["positive criteria type"] == "AND":
                if pos_qc_words and pos_qc_score:
                    all_pos_qc[qc_sub.name][subreddit] += 1

            # OR criteria
            else:
                if pos_qc_words or pos_qc_score:
                    all_pos_qc[qc_sub.name][subreddit] += 1

            # Negative QC
            # Negative QC: Score
            if qc_sub.qc_config["negative score"] != "":
                neg_qc_score = score <= int(qc_sub.qc_config["negative score"])
            else:
                neg_qc_score = True

            # Negative QC: Word Count
            if qc_sub.qc_config["negative word count"] != "":
                neg_qc_words = count_words(body) >= int(qc_sub.qc_config["negative word count"])
            else:
                neg_qc_words = True

            # Negative QC: Result
            if qc_sub.qc_config["negative criteria type"] == "AND":
                if neg_qc_words and neg_qc_score:
                    all_neg_qc[qc_sub.name][subreddit] += 1
            else:
                if neg_qc_words or neg_qc_score:
                    all_neg_qc[qc_sub.name][subreddit] += 1

    # Posts
    post_results = ps.search_submissions(author=author,
                                         after=after_time,
                                         before=before_time,
                                         filter=["id", "score", "subreddit"], )
    sub_post_karma = Counter()
    sub_pos_posts = Counter()
    sub_neg_posts = Counter()

    for ps_post in post_results:
        score = ps_post.score
        subreddit = str(ps_post.subreddit).lower()

        sub_post_karma[subreddit] += score
        if score > 0:
            sub_pos_posts[subreddit] += 1
        else:
            sub_neg_posts[subreddit] += 1

    # Insert data if all subs aren't in sync
    if len(not_exists_in_sub) > 0:
        target_sub.db.insert_sub_activity(username, all_pos_qc, all_neg_qc)
        target_sub.db.insert_accnt_activity(username, sub_comment_karma, sub_pos_comments, sub_neg_comments,
                                            sub_post_karma, sub_pos_posts, sub_neg_posts)
    else:
        target_sub.db.update_sub_activity(username, all_pos_qc, all_neg_qc)
        target_sub.db.update_accnt_activity(username, sub_comment_karma, sub_pos_comments, sub_neg_comments,
                                            sub_post_karma, sub_pos_posts, sub_neg_posts)


def count_words(body):
    body_list = body.split()
    return len(body_list)
