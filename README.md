# plex-mirror-similar
Adds any missing artists to the similar artist tags in a Plex library so they are reciprocal. This isn't done automatically by Plex, and will greatly increase your ability to navigate between similar artists. Some might argue that similarity isn't always reciprocal, but I disagree.

WARNING: This is a simple script and does not have extensive error management. Use at your own risk. I STRONGLY suggest creating a new music library to test the script and/or use the search string or date options to limit it to a subset of artists. Only run it on your entire music library when you're sure it's behaving as desired. It may take several hours to run on a large music collection.

Set the following at runtime: e.g. "plex-mirror-similar.py -range=12h"
- -range=datetime (change only recent albums and related artists - date as yyyy-mm-dd or duration e.g. 6h, 14d, or 1y)
- -search=string (optional artist name, limit which artist(s) are changed, matches partial names)
- -unlink=string (optional artist to remove from all similar lists)

Customize the following in the script file:
- tags_to_rename (a list of find-replace pairs, e.g. [['old_one','new_one'],['old_two','new_two]], these will be replaced in all similar artist tag lists)
