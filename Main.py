import praw
from queue import Queue
import threading
from Subreddit import Subreddit
import ProcessComment

# PRAW Instance
r = praw.Reddit("InstaMod")
# List of subreddits
sub_list = [Subreddit("CryptoCurrency", r)]
# Queue for users to be analyzed
comment_queue = Queue()
# Lock for shared resources
lock = threading.Lock()
# Thread for processing comments
process_thread = threading.Thread(target=ProcessComment.fetch_queue,
                                  args=(r, comment_queue, lock, sub_list))

# Make multi-sub for subreddit stream
sub_str = ""
for sub in sub_list:
    sub_str += sub.sub_name + "+"
sub_str = sub_str[:-1]
all_subs = r.subreddit(sub_str)

# Main Method
process_thread.setDaemon(True)
process_thread.start()

while True:
    for comment in all_subs.stream.comments(pause_after=1, skip_existing=False):
        if comment is None:
            continue
        comment_queue.put(comment)
