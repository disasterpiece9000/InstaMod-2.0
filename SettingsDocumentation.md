 # Settings File Documentation
 
 * **[Editing the Settings](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#editing-the-settings)**
 * **[Main Configuration](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#main-configuration)**
 * **[Flair](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#flair)**
 * **[Quality Comments](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#quality-comments)**
 * **[Progression Tiers](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#progression-tiers)**
    * [Secondary Progression Tier Criteria](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#secondary-progression-tier-criteria)
* **[Subreddit Activity Tags](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#subreddit-activity-tags)**
    * [Secondary Activity Tag Criteria](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#secondary-activity-tag-criteria)
* **[Thread Lock](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#thread-lock)**
* **[Subreddit Groups](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#subreddit-groups)**
 
 ## Editing the Settings
 
The settings for InstaMod uses the .ini format and is read from a wiki page on the subreddit titled "instamodsettings". Here's the cheat-sheet for working with .ini files:
 
 **Keys**
 
* Every key has a name and a value, delimited by an equals sign (=). The name appears to the left of the equals sign and the value appears to the right. 
* The key cannot contain the characters equal sign ( = ), semicolon ( ; ), or hashtag ( # ) as these are reserved characters. However, the value can contain any character. 
* Keys cannot contain duplicate names within the same section.
 
 **Sections**
 
* Keys are grouped into sections. The section name appears on a line by itself, in square brackets ( \[ ] ). All keys after the section declaration are associated with that section. There is no explicit "end of section" delimiter; sections end at the next section declaration, or the end of the file. Sections may not be nested.
* All sections listed in the documentation and the sample settings file must be present, even if the section is disabled. This does not include secondary criteria sections. 
* Each section must contain all it's coresponding keys. A key's value can only be left blank if specified in the documentation.

**Other**

* All text in the settings is case insensitive.
* Lines can be commented out using a hashbang ( # )
* Leading or trailing spaces do not matter

**Example:**

    [Section 1]
    key1=value
    key2 = value
    
    # Comment
    [Section 2]
    key1= VALUE
    key2 =  value


## Main Configuration

**Section Name:** [MAIN CONFIG]  

**Description:** Turn main features on or off

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| thread lock | Turn on/off the thread lock feature | True or False |
| tier flair | Turn on/off the progression flair feature | True or False |
| new account tag | Turn on/off the new account tag feature | True or False |
| activity flair | Turn on/off the activity flair feature | True or False |
| comment ratelimit | Turn on/off the comment ratelimit feature | True or False |
| toxicity report | Turn on/off the toxicity report feature | True or False |

## Flair

**Section Name:** [FLAIR]

**Description:** General settings for flair management

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| flair expiration | The number of days until a user's flair is reevaluated | Any integer > 0 |
| new account age | The number of months an account must be younger than to be considerd new | Any integer >= 0 |
| approved icons | A list of icons available to users with the "FLAIR CSS" permission |  A comma delimited list of icon ids |

## Quality Comments

**Section Name:** [QUALITY COMMENTS]

**Description:** Criteria for positive and negative QC

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| positive score | Comments with a score >= this meet the score criteria | Any integer |
| positive word count | Comments with a word count >= this meet the word count criteria | Any integer > 0 or leave blank to disable |
| positive toxicity low | Low threshold of the acceptable toxicity score range | Any integer from 0 - 99 or leave blank to disable |
| positive toxicity high | High threshold of the acceptable toxicity score range | Any integer from 0 - 99 or leave blank to disable |
| positive criteria type | Combination of criteria required to earn 1 positive QC | AND (all of them) or OR (at least one of them) |
| negative score | Comments with a score <= this meet the score criteria | Any integer |
| negative word count | Comments with a word count <= this meet the word count criteria | Any integer > 0 or leave blank to disable |
| negative toxicity low | Low threshold of the unacceptable toxicity score range | Any integer from 0 - 99 or leave blank to disable |
| negative toxicity high | High threshold of the unacceptable toxicity score range | Any integer from 0 - 99 or leave blank to disable |
| negative criteria type | Combination of criteria required to earn 1 negative QC | AND (all of them) or OR (at least one of them) |

## Progression Tiers

**Section Name:** [PROGRESSION TIER 1] 
* **Note:** Each subsequent tier must increment the number at the end. If a number is skipped then the tier will not be seen.

**Description:** Criteria for a user to be placed in the given tier. This section supports secondary criteria.

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| metric | Data point used for criteria | total comment karma, total post karma, total karma, comment karma, post karma, positive comments, negative comments, positive posts, negative posts, positive QC, negative QC, or net QC |
| target subs | Which subreddit(s) to pull the metric from. This data will be totaled to make the user value | A sub group name, a subgroup name appended with " - abbrev" to total all subreddits in the group with a matching abbreviation (Ex: SUB GROUP 1 - CC), or ALL to include data from every sub in the user's history. If total comment karma or total post karma are selected for metric then this section is ignored |
| comparison | Type of comparison to make between the user's value and the target value (Ex: user value >= target value) | \>, <, >=, <= |
| target value | Value for the right side of the comparison | Any integer |
| flair text | Flair text assigned if the user meets the criteria | Any text with no more than 64 characters or leave blank for none |
| flair css | Flair CSS assigned if the user meets the criteria | Any valid flair CSS ID or leave blank for none |
| permissions | Permission granted if the user meets the criteria | CUSTOM FLAIR, CUSTOM CSS, or leave blank for none |

### Secondary Progression Tier Criteria

**Section Name:** [PROGRESSION TIER 1 - AND] or [PROGRESSION TIER 1 - OR]
* **Note:** This section type is **not** required. Secondary progression tiers must match up with an existing progression tier of the same number.

**Description:** Each progression tier can have a secondary criteria specified. The second criteria is denoted by appending " - AND" or " - OR" to the parent section's name (Ex: "PROGRESSION TIER 1 - AND"). If AND is used then the user must meet both criteria. If OR is used then the user must meet at least one of the criteria.

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| metric | Data point used for criteria | total comment karma, total post karma, total karma, comment karma, post karma, positive comments, negative comments, positive posts, negative posts, positive QC, negative QC, or net QC |
| target subs | Which subreddit(s) to pull the metric from. This data will be totaled to make the user value | A sub group name or ALL to include data from every sub in the user's history. If total comment karma or total post karma are selected for metric then this section is ignored |
| comparison | Type of comparison to make between the user's value and the target value (Ex: user value >= target value) | \>, <, >=, <= |
| target value | Value for the right side of the comparison | Any integer |

## Subreddit Activity Tags

**Section Name:** [ACTIVITY TAG 1]
* **Note:** Each subsequent tag must increment the number at the end. If a number is skipped then the tag will not be seen.

**Description:** Criteria for a user to receive flair text for the given tag. This section supports secondary criteria.

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| metric | Data point used for criteria | total comment karma, total post karma, total karma, comment karma, post karma, positive comments, negative comments, positive posts, negative posts, positive QC, negative QC, or net QC |
| target subs | Which sub(s) to pull the metric from | A sub group name or ALL to include data from every sub in the user's history. If total comment karma or total post karma are selected for metric then this section is ignored |
| group subs | Subreddits from the sub group can either be processed individually or as a group (all values are totaled) | True or False |
| comparison | Type of comparison to make between the user's value and the target value (Ex: user value >= target value) | \>, <, >=, <= |
| target value | Value for the right side of the comparison | Any integer |
| display value | The user value and metric name can be appended to the tag's text. If a secondary criteria is given, the parent section's user value and metric are used. | True or False |
| sort | The order (based on user value) which subreddits that meet the criteria are displayed in the tag's text. This option is disabled if group subs is set to True | MOST COMMON (high to low), LEAST COMMON (low to high), or leave blank for random sort |
| sub cap | The maximum number of subreddits listed for the tag's text. This option is disabled if group subs is set to True | Any positive integer
| pre text | Text that comes before the subreddit's abbreviation in the tag's text. If group subs is set to True, then their is no abbreviation added to the tag | Any text or leave empty for none |
| post text | Text that comes after the subreddit's abbreviation in the tag's text. If group subs is set to True, then their is no abbreviation added to the tag | Any text or leave empty for none |
| permissions | Permission granted if the user meets the criteria | CUSTOM FLAIR, CUSTOM CSS, or leave blank for none |


### Secondary Activity Tag Criteria

**Section Name:** [ACTIVITY TAG 1 - AND] or [ACTIVITY TAG 1 - OR]
* **Note:** This section type is **not** required. Secondary activity tags must match up with an existing activity tag of the same number.
 
**Description:** Each activity tag can have a secondary criteria specified. The second criteria is denoted by appending " - AND" or " - OR" to the parent section's name (Ex: "ACTIVITY TAG 1 - AND"). If AND is used then the user must meet both criteria. If OR is used then the user must meet at least one of the criteria.

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| metric | Data point used for criteria | total comment karma, total post karma, total karma, comment karma, post karma, positive comments, negative comments, positive posts, negative posts, positive QC, negative QC, or net QC |
| target subs | Which sub(s) to pull the metric from | A sub group name or ALL to include data from every sub in the user's history. If total comment karma or total post karma are selected for metric then this section is ignored |
| group subs | Subreddits from the sub group can either be processed individually or as a group (all values are totaled) | True or False |
| comparison | Type of comparison to make between the user's value and the target value (Ex: user value >= target value) | \>, <, >=, <= |
| target value | Value for the right side of the comparison | Any integer |

## Thread Lock

**Section Name:** [THREAD LOCK 1]
* **Note:** Each subsequent thread lock must increment the number at the end. If a number is skipped then the thread lock will not be seen.

**Description:** Criteria for a user to be able to post in a locked thread

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| metric | Data point used for criteria | total comment karma, total post karma, total karma, comment karma, post karma, positive comments, negative comments, positive posts, negative posts, positive QC, negative QC, or net QC |
| target subs | Which subreddit(s) to pull the metric from. This data will be totaled to make the user value | A sub group name or ALL to include data from every sub in the user's history. If total comment karma or total post karma are selected for metric then this section is ignored |
| comparison | Type of comparison to make between the user's value and the target value (Ex: user value >= target value) | \>, <, >=, <= |
| target value | Value for the right side of the comparison | Any integer |
| flair ID | Post's flair text that signifies a thread is locked by this criteria | Any text |
| action | Moderator action taken against commenters that do not meet the criteria | REMOVE, REPORT, or SPAM |

## Subreddit Groups

**Section Name:** [SUB GROUP 1]
* **Note:** Each subsequent group must increment the number at the end. If a number is skipped then the group will not be seen.

**Description:** Groupings of subreddits and their corresponding abbreviations. Each key is a subreddit name and the value is it's abbreviation.

**Example:**
     
    [SUB GROUP 1]
    CryptoCurrency = CC
    CryptoMarkets = CM
    Bitcoin = BTC
    BitcoinMarkets = BTC
    
For a given activity tag where group subs is set to false, Bitcoin and BitcoinMarkets will have their user value combined. If group subs is set to true, then all subreddits will be combined regardless of their abbreviation.

For a given progression tier where target subs is set to SUB GROUP 1 - BTC, only Bitcoin and BitcoinMarkets will be selected and combined. If target subs is set to just SUB GROUP 1, then all subreddits will be combined regardless of their abbreviation.