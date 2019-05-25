 # Settings File Documentation
 
The settings for InstaMod uses the .ini format and is read from a wiki page on the subreddit titled "instamodsettings". Here are some general rules of thumb for editing or adding to the settings file:
 
 **Keys**
 
Every key has a name and a value, delimited by an equals sign (=). The name appears to the left of the equals sign. The key cannot contain the characters equal sign ( = ) or semicolon ( ; ) as these are reserved characters. The value can contain any character. 

    name=value
 
 **Sections**
 
Keys are grouped into sections. The section name appears on a line by itself, in square brackets (\[ ]). All keys after the section declaration are associated with that section. There is no explicit "end of section" delimiter; sections end at the next section declaration, or the end of the file. Sections may not be nested.

**Other**

All text in the settings is case insensitive.

Lines can be commented out using a hashtag ( # )

Keys and sections cannot contain duplicate names
