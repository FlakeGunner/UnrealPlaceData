# UnrealPlaceData
A Tool to access the data store of the Reddit r/place archive provided by [u/mncke](https://www.reddit.com/user/mncke) that's convenient.

## Data Source
This python script is based on the data collected by reddit user [u/mncke](https://www.reddit.com/user/mncke).

The data source is described in these two reddit posts:
- [/r/place Archive UPDATE and board-bitmap description](https://www.reddit.com/r/place/comments/62z2uu/rplace_archive_update_and_boardbitmap_description/)
- [/r/place ARCHIVE UPDATE](https://www.reddit.com/r/place/comments/6396u5/rplace_archive_update/)

## Requirements
- To run this python script you need to use python 3.6 and the following python libraries: pillow 4.0, imageio 2, progressbar2 installed.
- In the same directory you'll need base.png which is contained in this [zip file](http://abra.me/place/diffs.zip).
- You'll need the diffs.bin file which is in this [zip file](http://abra.me/place/diffs.bin.zip).

## Current functionality
- This script takes the base.png and diffs.bin created by [u/mncke](https://www.reddit.com/user/mncke) and stores that data in two SQLite tables.
- Loads that data into memory from SQLite tables
- Generate a PNG for a given timestamp.
- Generate a Sequence of PNG for a given timestamp.
- Generate a gif for a given timestamp range.
- Command line interface

## Planned features
- GUI
- Generate serialized Unreal Engine UObjects on disk 
