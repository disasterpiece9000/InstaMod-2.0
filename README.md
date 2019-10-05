# InstaMod v2.0 - Customizable user flair system

InstaMod is a toolbox of features that moderators can implement and tailor fit to their needs. With a robust feature set and unlimited combinations of settings, InstaMod gives moderators the ability to customize and moderate their community in ways that AutoModerator can't. 

To get a better idea of the customization options available, please check out the [settings documentation](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md) or one of the subreddits currently using InstaMod
* [/r/CryptoCurrency](https://www.reddit.com/r/CryptoCurrency)
* [/r/CryptoTechnology](https://www.reddit.com/r/CryptoTechnology)
* [/r/CryptoMarkets](https://www.reddit.com/r/CryptoMarkets)

## Features - Flair Management

### User Tiers

As a user participates more and more in the community, their flair can change to represent their involvement. Certain tiers, or levels of user participation, can grant the user access to special privileges. This includes the ability to assign themself custom flair and the ability to add CSS to their automatic flair. This system rewards frequent contributors and encourages new users to stop lurking and start participating!

### Activity Tags

Moderators can configure InstaMod to include information about user' account history in their flair . It could display a user's top 3 most used related communities, or it could be setup to display the subreddits where the user has been consistently downvoted. These are just a few examples of the endless combinations of settings at your disposal.

### PM Commands

PM commands allow users and moderators to quickly and easily interact with InstaMod.

| Command | Description | Permitted Users |
| ----------- | ----------- | ----------- |
| !noautoflair | Prevents InstaMod from assigning automatic flair to the specified user. This allows moderators to assign a user flair without InstaMod overwriting it and without that user getting full custom flair permissions. | Moderators |
| !giveflairperm | Gives the specified user custom flair permissions. The user will be automatically notified after the command is processed. | Moderators |
| !updatesettings | Re-read the wiki settings page so that settings changes can take place instantly. InstaMod automatically re-checks settings each hour | Moderators |
| !wipe | Remove all stored flair data and reanalyze every users flair. This will only delete the subreddit's data | Moderators |
| !updatethem| Update the specified user's account data and flair, regardless of if their information is out of date | Moderators |
| !updateme | Update the senders account data and flair, regardless of if their information is out of date | All users |
| !flair | Change the user's flair text and CSS to whatever they specify | Users with custom flair permissions |
| !css | Change the user's CSS to whatever they specify | Users with custom CSS permissions |

_____

## How to run

Unlike most bots, InstaMod is designed to simultaneously support multiple subreddits. This means that adding it to your subreddit doesn't require any technical knowledge or hosting capability! If you are interested in incorporating it into your subreddit all you need to do is create a wiki page called "InstaModSettings", fill it with the information specified in the [settings documentation](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md), and [contact me](https://www.reddit.com/message/compose?to=shimmyjimmy97&subject=InstaMod&message=) so that I can import your subreddit.

If you would like to run your own version of InstaMod, here are the required components:
* Python 3.7.4
* SQLite 3.25.0 or higher
* PRAW 6.3.2
* Fill in your Reddit account credentials in the praw.ini file
* Fill in all the subreddits the bot will run on (delimited by new lines) in the subreddit_master_list.txt file

## Upcomming Features - Content Moderation

### Toxicity Report

Using the [Perspective API](https://www.perspectiveapi.com/#/home), InstaMod can instantly identify toxic comments and take action before anyone even reads it. Depending on how confident the API is that the comment is toxic, it can either be reported, marked as spam, or outright removed. This is a powerful tool for improving the quality and civility of conversations in a community.


### Custom Ratelimiting

Reddit has a built in rate-limit system to prevent spam, but with InstaMod this can be expanded and customized to ensure that users in your subreddit cannot spam comments and posts. For example, moderators could configure this to prevent new accounts from posting more than one submission a day, limit everyone to no more than 3 posts a week, or even limit trolls to one comment per hour.

### Advanced Thread Locking

Traditional thread locking is inherently all-or-nothing. With InstaMod, a post's comment section can be filtered to disallow certain types of comments or users. This allows users to have a conversation, while still containing the reason the thread was locked in the first place. It could be used to prevent brigades, block toxic comments, or restrict a thread to only long-time community members.

If a user doesn't meet the requirements, then their comment can either be removed or marked spam. There is also an option to automatically notify the user of their comment's deletion. Moderators simply have to assign a post a specific flair for it to be locked.
