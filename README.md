# UnrealPlaceData
A Tool to make timelapse gifs based on the data store of the Reddit r/place archive provided by [u/mncke](https://www.reddit.com/user/mncke).  Plan to have the script generate serialised UObjects for visualisation in Unreal Engine 4.

## Data Source
This script is using data collected by reddit user [u/mncke](https://www.reddit.com/user/mncke).

The data source is described in these two reddit posts:
- [/r/place Archive UPDATE and board-bitmap description](https://www.reddit.com/r/place/comments/62z2uu/rplace_archive_update_and_boardbitmap_description/)
- [/r/place ARCHIVE UPDATE](https://www.reddit.com/r/place/comments/6396u5/rplace_archive_update/)

## Requirements
- To run this script you need to have python 3.6 and the following python libraries: pillow 4.0, imageio 2, progressbar2.
- In the same directory you'll need base.png which is contained in this [zip file](http://abra.me/place/diffs.zip).
- You'll also need the diffs.bin file which is in this [zip file](http://abra.me/place/diffs.bin.zip).
- Script needs about 3 gigs of ram

## Installation
- When you're installing [python 3.6.1](https://www.python.org/downloads/release/python-361/) make sure you also install pip and add python to your path.
- After you've installed python, run these commands to make sure you're setup right:
```shell
python --version
pip3 --version
```
- You should see python 3.6.1 and pip 9.0.1
- Run the following pip commands to install the required libraries 
```shell
pip3 install pillow
pip3 install imageio
pip3 install progressbar2
```

## Using the script
- Download the latest version of the [makegif.py](https://raw.githubusercontent.com/FlakeGunner/UnrealPlaceData/master/src/placedata/makegif.py).
- Next you need base.png and diffs.bin. You can either grab [placedata.zip](https://drive.google.com/file/d/0B52IMA57BvO2NHd4aHAtdzVQZWs/view?usp=sharing) that has both files, or grab them from the original links above.
- Unzip these files in the same folder as makegif.py

## Note on Epoch Timestamps
- The script uses [Epoch timestamps](https://en.wikipedia.org/wiki/Unix_time) for script parameters.  Use this [handy tool](http://www.unixtimestamp.com/index.php) to get Epoch timestamps.  The data archive runs from Friday, **31-Mar-17 19:01:00 UTC**  to **Monday, 03-Apr-17 16:58:41 UTC**.

### Script Paramenters
```bash
usage: makegif.py [-h] [--silent] [x1] [y1] [x2] [y2] [timestamp] [delay]

Make timelapse gifs of r/place - Based on data archive provided by u/mncke

positional arguments:
  x1          X coordinate of pixel to start gif from, valid values: 1-1000,
              default: 0.
  y1          Y coordinate of pixel to start gif from, valid values: 1-1000,
              default:0.
  x2          X coordinate of pixel to finish gif from, valid values: 1-1000,
              must be greater than x1, default: 1000.
  y2          Y coordinate of pixel to finish gif from, valid values: 1-1000,
              must be greater than y1, default: 1000.
  timestamp   Epoch timestamp to start gif from. r/place data starts from:
              1490986860 and ends at 1491238721, default: 1490986860.
  delay       Delay in seconds between snapshots/gif frames, default:60.

optional arguments:
  -h, --help  show this help message and exit
  --silent    Don't display progress bars, runs a bit faster.
```
### Examples
- To make a gif from pixel (400, 400) to (600,600), starting a 36 hours into the archive, with a snapshot every 90 seconds
```bash
python makegif.py 400 400 600 600 1491080460 90
```
- To make a gif from (300, 700) to (450, 900), starting a day into the archive, with a snapshot every 5 minutes
```bash
python makegif.py 300 700 450 900 1491073260 300
```
- If you don't put in any parameters it uses default values, (1, 1) to (1000, 1000), full archive timespan and a snapshot every 60 seconds. (warning this takes a while)
```bash
python makegif.py
```
- If you want to speed up the script add the optional parameter --silent to turn off progress bars.  You can always tail the log file placedata.log to watch progress.
```bash
python makegif.py 300 700 450 900 1491073260 300 --silent
```

## Bugs / Features Requests
- If you find any bugs or would like a feature feel free to add an [issue](https://github.com/FlakeGunner/UnrealPlaceData/issues)

## Current functionality
- This script takes the base.png and diffs.bin created by [u/mncke](https://www.reddit.com/user/mncke) and stores that data in two SQLite tables.
- Loads that data into memory from SQLite tables
- Generate a gif for a given timestamp range.
- Command line interface to make a timelapse gif from a starting timestamp to the end of archive data.

## Planned features
- Add ability to make gifs with an ending timestamp that's taken from script parameters
- Add script parameters to specify gif filename
- Add script parameters to generate PNG and PNG sequences
- GUI
- Generate serialized Unreal Engine UObjects on disk 
- Add unit tests
- Pack for pypi
