# HashFS-SQLite
A CLI Implementation of python HashFS library.

# TODO
- Rename Functionality
- Ability to change categories
- Set category when storing file
- List and manage categories

# Run
Just run it with `python hfs.py`

# Arguments
### Store (-s --store): 
`hfs.py -s ~/definitely_not_furry_p*rn.mp4` \
Store a file in the file system

### Get (-g --get): 
`hfs.py -g "archlinux-%-x86\_64.torrent"` \
`hfs.py -g "_rt of war%.pdf"` \
Search and find a File with sql wildcards (_ and %) and throw the content to stdout
- "_" represents a single character	(? in wildcard)
- "%" represents any character		(* in wildcard)
Use `\%` and `\_` for files that contains those characters

### Get with Hash (-w --get_w_hash): 
[comment]: # 'btw this is sha256sum of "Dekai Manga Archive [Fall 2020].torrent'
`hfs.py -w a73d9cfac1765fb821d5f3c3e2cc9f1801e84066edb78ba8a61adb513d187b91` \
Same as -g with hashid

### Delete (-d --delete): 
`hfs.py -d "xi - Freedom Dive.mp3"` \
Removes a file with sql wildcards

### Repair (-r --repair):
`hfs.py -r` \
Repair the filesystem's Structure

### List (-l --list):
`hfs.py -l` \
List all files

### Info (-i --info):
`hfs.py -i` \
Get Information about files/folders in the filesystem
