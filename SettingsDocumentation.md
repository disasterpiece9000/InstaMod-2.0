 # Settings File Documentation
 

 
 ## Getting Started
 
 This document details the options and requirements for the settings wiki page.
 
 If you are just getting started, here are some resources that may help:
 * [Completed settings page from /r/CryptoCurrency](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/ExampleSettings)
 * [Blank settings template](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsTemplate.ini)
 
 ### Index
 
* **[Editing the Settings](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#editing-the-settings)**
* **[Main Configuration](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#main-configuration)**
* **[Flair](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#flair)**
* **[Quality Comments](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#quality-comments)**
* **[Progression Tiers](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#progression-tiers)**
  * [Secondary Progression Tier Criteria](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#secondary-progression-tier-criteria)
* **[Subreddit Activity Tags](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#subreddit-activity-tags)**
  * [Secondary Activity Tag Criteria](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#secondary-activity-tag-criteria)
* **[Subreddit Groups](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#subreddit-groups)**
* **[PM Messages](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#pm-messages)**
 
 ## Editing the Settings
 
The settings for InstaMod uses the .ini format and is read from a wiki page on the subreddit titled "instamodsettings". Here's the cheat-sheet for working with .ini files:

**Example INI Format:**

    [Section 1]
    key1=value
    key2 = value
    
    # This is a comment
    [Section 2]
    key1= value
    key2 =  value
 
 **Keys**
 
* Every key has a name and a value, delimited by an equals sign (=). The name appears to the left of the equals sign and the value appears to the right. 
* The key cannot contain the characters equal sign ( = ), semicolon ( ; ), or hashbang ( # ) as these are reserved characters. However, the value can contain any character.
* Keys cannot contain duplicate names within the same section.
 
 **Sections**
 
* Keys are grouped into sections. The section name appears on a line by itself, in square brackets ( \[ ] ). All keys after the section declaration are associated with that section. There is no explicit "end of section" delimiter; sections end at the next section declaration, or the end of the file. Sections may not be nested.
* All sections listed in the documentation, with the exception of Progression Tiers, Activity Tiers, and Sub Groups, must be present.
* Each section must contain all it's corresponding keys. A key's value can only be left blank if specified in the documentation.

**Other**

* Keys are case insensitive but the values are not. However, for values where only True or False are accepted, multiple formats will be accepted and are not case sensitive.
  * True: true, yes, or on
  * False: false, no, or off
* Lines can be commented out using a hashbang ( # )
* Leading or trailing spaces do not matter


## Main Configuration

**Section Name:** [MAIN CONFIG]  

**Description:** Turn main features on or off

**Required:** Yes

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| progression tier | Turn on/off the progression flair feature | True or False |
| young account tag | Turn on/off the new account tag feature | True or False |
| activity tag | Turn on/off the activity flair feature | True or False |

## Flair

**Section Name:** [Flair]

**Description:** General settings for flair management

**Required:** Yes

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| flair expiration | The number of days until a user's flair is reevaluated | Any integer > 0 |
| new account age | The number of months an account must be younger than to be considered new | Any integer >= 0 |
| approved icons | A list of icons available to users with the "FLAIR CSS" permission |  A comma delimited list of icon ids |

## Quality Comments

**Section Name:** [Quality Comments]

**Description:** Quality comments is a criteria that you can define based on a comment's score and word count. Positive QC defines what a good comment consists of and Negative QC defines what a bad comment consists of. This can be used as a metric in the Progression and Activity section.

**Required:** Yes

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| positive score | Comments with a score >= this meet the score criteria | Any integer |
| positive word count | Comments with a word count >= this meet the word count criteria | Any integer > 0 or leave blank to disable |
| positive criteria type | Combination of criteria required to earn 1 positive QC | And (all of them) or Or (at least one of them) |
| negative score | Comments with a score <= this meet the score criteria | Any integer |
| negative word count | Comments with a word count <= this meet the word count criteria | Any integer > 0 or leave blank to disable |
| negative criteria type | Combination of criteria required to earn 1 negative QC | And (all of them) or Or (at least one of them) |
| exclude when op | Prevent user from gaining or losing QC from comments where they are also OP | True or False <br> **This overrides positive/negative criteria type** |

## Progression Tiers

**Section Name:** [Progression Tier 1] 
* **Note:** Each subsequent tier must increment the number at the end. If a number is skipped then the tier will not be seen.

**Description:** Sort users into tiers based on their account activity. This section supports secondary criteria.

**Required:** No

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| metric | Data point pulled from the user's history that is used for criteria | <ul><li>total comment karma, total post karma, total karma</li><li>comment karma, post karma</li><li>positive comments, negative comments</li><li>positive posts, negative posts</li><li>positive QC, negative QC, net QC |
| target subs | Which subreddit(s) to pull the metric from | <ul><li>Sub group name: SUB GROUP 1</li><li>Sub group name appended with " - abbrev": SUB GROUP 1 - CC</li><li>Sub group name appended with multiple comma delimited abbreviations: SUB GROUP 1 - CC, CM, CT</li><li>Subreddit name: CryptoCurrency</li><li>ALL to include data from every sub in the user's history</li></ul> **If total comment karma or total post karma are selected for metric then this section is ignored**|
| comparison | Criteria to determine if the user belongs in the tier | \>, <, >=, or <= followed by any integer <br />Put "percent" after the integer to restrict the tier to users in the top X% |
| flair text | Flair text assigned if the user meets the criteria | Any text with no more than 64 characters or leave blank for none |
| flair css | Flair CSS assigned if the user meets the criteria | Any valid flair CSS ID or leave blank for none |
| permissions | Permission granted if the user meets the criteria | CUSTOM FLAIR, CUSTOM CSS, CUSTOM TEXTor leave blank for none |

### Secondary Progression Tier Criteria

**Section Name:** [Progression Tier 1 - And] or [Progression Tier 1 - Or]
* **Note:** Secondary progression tiers must match up with an existing progression tier of the same number.

**Description:** Each progression tier can have **one** secondary criteria specified. The second criteria is denoted by appending " - And" or " - Or" to the parent section's name (Ex: "Progression Tier 1 - And"). If And is used then the user must meet both criteria. If Or is used then the user must meet at least one of the criteria.

**Required:** No

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| metric | Data point pulled from the user's history that is used for criteria | <ul><li>total comment karma, total post karma, total karma</li><li>comment karma, post karma</li><li>positive comments, negative comments</li><li>positive posts, negative posts</li><li>positive QC, negative QC, net QC |
| target subs | Which subreddit(s) to pull the metric from | <ul><li>Sub group name: SUB GROUP 1</li><li>Sub group name appended with " - abbrev": SUB GROUP 1 - CC</li><li>Sub group name appended with multiple comma delimited abbreviations: SUB GROUP 1 - CC, CM, CT</li><li>Subreddit name: CryptoCurrency</li><li>ALL to include data from every sub in the user's history</li></ul> **If total comment karma or total post karma are selected for metric then this section is ignored**|
| comparison | Criteria to determine if the user belongs in the tier | \>, <, >=, or <= followed by any integer <br />Put "percent" after the integer to restrict the tier to users in the top X% |
## Subreddit Activity Tags

**Section Name:** [Activity Tag 1]
* **Note:** Each subsequent tag must increment the number at the end. If a number is skipped then the tag will not be seen.

**Description:** Add tags to users flair . This section supports secondary criteria.

**Required:** No

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| metric | Data point pulled from the user's history that is used for criteria | <ul><li>total comment karma, total post karma, total karma</li><li>comment karma, post karma</li><li>positive comments, negative comments</li><li>positive posts, negative posts</li><li>positive QC, negative QC, net QC |
| target subs | Which subreddit(s) to pull the metric from | <ul><li>Sub group name: SUB GROUP 1</li><li>Sub group name appended with " - abbrev": SUB GROUP 1 - CC</li><li>Sub group name appended with multiple comma delimited abbreviations: SUB GROUP 1 - CC, CM, CT</li><li>Subreddit name: CryptoCurrency</li><li>ALL to include data from every sub in the user's history</li></ul> **If total comment karma or total post karma are selected for metric then this section is ignored**|
| comparison | Criteria to determine if the user belongs in the tier | \>, <, >=, or <= followed by any integer <br />Put "percent" after the integer to restrict the tier to users in the top X% |
| combine subs | Subreddits from the sub group can either be processed individually or as a group (all values are totaled) | True or False |
| display value | The user value and metric name can be appended to the tag's text. If a secondary criteria is given, the parent section's user value and metric are used. | True or False |
| sort | The order (based on user value) which subreddits that meet the criteria are displayed in the tag's text. This option is disabled if group subs is set to True | <ul><li>MOST COMMON (high to low)</li><li>LEAST COMMON (low to high)</li></ul>**This section defaults to most common if left blank** |
| sub cap | The maximum number of subreddits listed for the tag's text. This option is disabled if group subs is set to True | Any positive integer
| pre text | Text that comes before the activity tag. If group subs is set to True, then there is no abbreviation added to the tag | Any text or leave empty for none |
| post text | Text that comes after the activity tag. If group subs is set to True, then their is no abbreviation added to the tag | Any text or leave empty for none |
| permissions | Permission granted if the user meets the criteria | CUSTOM FLAIR, CUSTOM CSS, CUSTOM TEXT, or leave blank for none |


### Secondary Activity Tag Criteria

**Section Name:** [Activity Tag 1 - And] or [Activity Tag 1 - Or]
* **Note:** Secondary activity tags must match up with an existing activity tag of the same number. Sub groups are automatically combined (group subs = True).
 
**Description:** Each activity tag can have **one** secondary criteria specified. The second criteria is denoted by appending " - And" or " - Or" to the parent section's name (Ex: "Activity Tag 1 - And"). If And is used then the user must meet both criteria. If Or is used then the user must meet at least one of the criteria.

**Required:** No

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| metric | Data point pulled from the user's history that is used for criteria | <ul><li>total comment karma, total post karma, total karma</li><li>comment karma, post karma</li><li>positive comments, negative comments</li><li>positive posts, negative posts</li><li>positive QC, negative QC, net QC |
| target subs | Which subreddit(s) to pull the metric from | <ul><li>Sub group name: SUB GROUP 1</li><li>Sub group name appended with " - abbrev": SUB GROUP 1 - CC</li><li>Sub group name appended with multiple comma delimited abbreviations: SUB GROUP 1 - CC, CM, CT</li><li>Subreddit name: CryptoCurrency</li><li>ALL to include data from every sub in the user's history</li></ul> **If total comment karma or total post karma are selected for metric then this section is ignored**|
| comparison | Criteria to determine if the user belongs in the tier | \>, <, >=, or <= followed by any integer <br />Put "percent" after the integer to restrict the tier to users in the top X% |

### PM Messages

**Section Name:** [PM Messages]

**Description:** InstaMod will occasionally need to message users about new permissions, comment removals, etc. This section allows you to set the test that the message will contain

**Required:** Yes

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| custom flair subj | Subject of the PM sent when InstaMod notifies a user that they have been granted the custom flair permission | Any text that fits in a subject line |
| custom flair body | Body of the PM sent when InstaMod notifies a user that they have been granted the custom flair permission | Any text that fits in a body |
| custom css subj | Subject of the PM sent when InstaMod notifies a user that they have been granted the custom css permission | Any text that fits in a subject line |
| custom css body | Body of the PM sent when InstaMod notifies a user that they have been granted the custom css permission | Any text that fits in a body |


## Subreddit Groups

**Section Name:** [SUB GROUP 1]
* **Note:** Each subsequent group must increment the number at the end. If a number is skipped then the group will not be seen.

**Description:** Groupings of subreddits and their corresponding abbreviations. Each key is a subreddit name and the value is it's abbreviation.

**Required:** No

**Example:**
     
    [SUB GROUP 1]
    CryptoCurrency = CC
    CryptoMarkets = CM
    Bitcoin = BTC
    BitcoinMarkets = BTC
    
Subreddits in a sub group with identical abbreviations are automatically combined. Using the combine subs toggle in the Activity Tags module allows you to combine all the subreddits in the group. For a given activity tag where combine subs is set to true, then all subreddits will be combined regardless of their abbreviation. If combine subs is set to false then Bitcoin and Bitcoin markets will be combined. The Progression module does not contain a combine subs toggle because all subreddits in the specified group are combined by default.

If you would like to only select a certain abbreviation from a sub group, you can do so by appending " - ABBREV" to the sub group's name. For example, selecting "SUB GROUP 1 - BTC" will only select Bitcoin and BitcoinMarkets. You also have the option to select multiple abbreviations from a sub group by appending multiple comma delimited abbreviations. For example "SUB GROUP 1 - CC, BTC" will select Bitcoin, BitcoinMarkets, CryptoCurrency.
