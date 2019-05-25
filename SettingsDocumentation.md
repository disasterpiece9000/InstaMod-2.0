 # Settings File Documentation
 
The settings for InstaMod uses the .ini format and is read from a wiki page on the subreddit titled "instamodsettings". Here are some general rules of thumb for editing or adding to the settings file:
 
 **Keys**
 
Every key has a name and a value, delimited by an equals sign (=). The name appears to the left of the equals sign. The key cannot contain the characters equal sign ( = ) or semicolon ( ; ) as these are reserved characters. The value can contain any character. 
 
 **Sections**
 
Keys are grouped into sections. The section name appears on a line by itself, in square brackets (\[ ]). All keys after the section declaration are associated with that section. There is no explicit "end of section" delimiter; sections end at the next section declaration, or the end of the file. Sections may not be nested.

All sections listed in the documentation and the sample settings file must be present. This does not include AND/OR subsections for tier and activity sections. Each section must contain all it's coresponding keys.

**Other**

All text in the settings is case insensitive.

Lines can be commented out using a hashtag ( # )

Keys and sections cannot contain duplicate names.

## MAIN CONFIG

| Key | Description | Values |
| ----------- | ----------- | ----------- |
| thread lock | Turn on/off the thread lock feature | True or False |
| tier flair | Turn on/off the progression flair feature | Ture or False |
| new account tag | Turn on/off the new account tag feature | Ture or False |
| activity flair | Turn on/off the activity flair feature | Ture or False |
| comment ratelimit | Turn on/off the comment ratelimit feature | Ture or False |
| toxicity report | Turn on/off the toxicity report feature | Ture or False |
