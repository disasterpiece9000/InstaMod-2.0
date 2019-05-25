 # Settings File Documentation
 
 * **[Intro](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#intro)**
 * **[MAIN CONFIG](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#main-config)**
 * **[FLAIR](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#flair)**
 * **[QUALITY COMMENTS](https://github.com/disasterpiece9000/InstaMod-2.0/blob/master/SettingsDocumentation.md#quality-comments)**
 
 ## Intro
 
The settings for InstaMod uses the .ini format and is read from a wiki page on the subreddit titled "instamodsettings". Here are some general rules of thumb for editing or adding to the settings file:
 
 **Keys**
 
Every key has a name and a value, delimited by an equals sign (=). The name appears to the left of the equals sign. The key cannot contain the characters equal sign ( = ) or semicolon ( ; ) as these are reserved characters. The value can contain any character. 
 
 **Sections**
 
Keys are grouped into sections. The section name appears on a line by itself, in square brackets (\[ ]). All keys after the section declaration are associated with that section. There is no explicit "end of section" delimiter; sections end at the next section declaration, or the end of the file. Sections may not be nested.

All sections listed in the documentation and the sample settings file must be present, even if the section is disabled. This does not include AND/OR subsections for tier and activity sections. Each section must contain all it's coresponding keys.

**Other**

All text in the settings is case insensitive.

Lines can be commented out using a hashtag ( # )

Keys and sections cannot contain duplicate names.

**Example**
'''
[Section 1]
'''

## MAIN CONFIG

Turn main features on or off

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| thread lock | Turn on/off the thread lock feature | True or False |
| tier flair | Turn on/off the progression flair feature | Ture or False |
| new account tag | Turn on/off the new account tag feature | Ture or False |
| activity flair | Turn on/off the activity flair feature | Ture or False |
| comment ratelimit | Turn on/off the comment ratelimit feature | Ture or False |
| toxicity report | Turn on/off the toxicity report feature | Ture or False |

## FLAIR

General settings for flair management

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| flair expiration | The number of until user's flair is reevaluated | Any integer > 0 |
| new account age | The number of months an account must be younger than to be considerd new | Any integer > 0 |
| approved icons | A list of icons available to users with the "FLAIR CSS" permission |  A comma delimited list of icon ids |

## QUALITY COMMENTS

Criteria for positive and negative QC

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| positive score | Comments with a score >= this meet the score criteria | Any integer |
| positive word count | Comments with a word count >= this meet the word count criteria | Any integer > 0 or None to disable |
| positive toxicity low | Low threshold of the acceptible toxicity score range | Any integer from 0 - 99 |
| positive toxicity high | High threshold of the acceptible toxicity score range | Any integer from 0 - 99 |
| positive criteria type | Combination of criteria required to earn 1 positive QC | AND (all of them) or OR (at least one of them) |
| negative score | Comments with a score <= this meet the score criteria | Any integer |
| negative word count | Comments with a word count <= this meet the word count criteria | Any integer > 0 or None to disable |
| negative toxicity low | Low threshold of the unacceptible toxicity score range | Any integer from 0 - 99 |
| negative toxicity high | High threshold of the unacceptible toxicity score range | Any integer from 0 - 99 |
| negative criteria type | Combination of criteria required to earn 1 negative QC | AND (all of them) or OR (at least one of them) |
