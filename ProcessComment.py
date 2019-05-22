import DataCollector
import FlairManager
import prawcore


def fetch_queue(r, q, lock, sub_list):
    for sub in sub_list:
        sub.make_db()
        
    while True:
        comment = q.get()
        q.task_done()
        
        # Find sub that the comment was placed in
        target_sub = None
        comment_sub = str(comment.subreddit).lower()
        for sub in sub_list:
            if sub.sub_name.lower() == comment_sub:
                target_sub = sub
                break

        update_flair = False
        if target_sub is not None:
            try:
                update_flair = DataCollector.get_data(comment, target_sub)
            except (prawcore.NotFound, prawcore.RequestException):
                continue
        
        prog_flair_enabled = str2bool(target_sub.main_config["progression flair"])
        new_accnt_flair_enabled = str2bool(target_sub.main_config["young account tag"])
        activity_flair_enabled = str2bool(target_sub.main_config["sub activity"])
        
        if update_flair and (prog_flair_enabled
                             or new_accnt_flair_enabled
                             or activity_flair_enabled):
            
            FlairManager.update_flair(r, comment.author, target_sub, prog_flair_enabled,
                                      new_accnt_flair_enabled, activity_flair_enabled)


def str2bool(txt):
    return txt.lower() in ("yes", "true", "t", "1")
