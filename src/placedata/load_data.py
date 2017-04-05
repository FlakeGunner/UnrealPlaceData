'''
Created on 4 Apr 2017

@author: FlakeGunner
'''
from PIL import Image
import sqlite3
import struct
import datetime

def ColourReferenceLookup(rgb_tuple):
    colour_reference = dict()
    colour_reference[0] = (255,255,255)
    colour_reference[1] = (228,228,228)
    colour_reference[2] = (136,136,136)
    colour_reference[3] = (34,34,34)
    colour_reference[4] = (255,167,209)
    colour_reference[5] = (229,0,0)
    colour_reference[6] = (229,149,0)
    colour_reference[7] = (160,106,66)
    colour_reference[8] = (229,217,0)
    colour_reference[9] = (148,224,68)
    colour_reference[10] = (2,190,1)
    colour_reference[11] = (0,211,221)
    colour_reference[12] = (0,131,199)
    colour_reference[13] = (0,0,234)
    colour_reference[14] = (207,110,228)
    colour_reference[15] = (130,0,128)
    
    for colour_key, colour_value in colour_reference.items():
        if colour_value == rgb_tuple:
            return colour_key
        
    raise ValueError('Failed to lookup colour reference')

class BasePixel:
    def __init__(self, x, y, colour):
            self.x = x
            self.y = y
            self.colour = colour
    def __str__(self):
            return "Base Pixel[ X:" + str(self.x) + " Y:" + str(self.y) + " Colour:" + str(self.colour) + "]"
        
    def getSQLiteInsertString(self):
            return "(" + str(self.x) + "," + str(self.y) + "," + str(self.colour) + ")"

class DiffPixel:
        def __init__(self, timestamp, x, y, colour):
            self.timestamp = timestamp;
            self.x = x
            self.y = y
            self.colour = colour
        
        def __str__(self):
            return "Pixel Diff[ Timestamp:" + datetime.datetime.fromtimestamp(self.timestamp).strftime('%Y-%m-%d %H:%M:%S') + " X:" + str(self.x) + " Y:" + str(self.y) + " Colour:" + str(self.colour)
        
        def getSQLiteInsertString(self):
            return "(" + str(self.timestamp) + "," + str(self.x) + "," + str(self.y) + "," + str(self.colour) + ")"

def LoadPixelDiffsIntoSQLite():
    all_diffs = []
    print("starting to read in binary data")
    
    with open("diffs.bin", "rb") as binary_file:
        binary_file.seek(0)
        pixel_diff_bytes = binary_file.read(16)
        while pixel_diff_bytes:
            pixel_diff_tuple = struct.unpack('<IIII', pixel_diff_bytes)
            pixel_diff = DiffPixel(pixel_diff_tuple[0], pixel_diff_tuple[1], pixel_diff_tuple[2], pixel_diff_tuple[3])
            all_diffs.append(pixel_diff)
            pixel_diff_bytes = binary_file.read(16)
            
    print("completed reading in binary data")
    
    print("starting to write pixel diffs to SQLite table")
            
    conn = sqlite3.connect('PlaceData.db')
    c = conn.cursor()
    
    c.execute("drop table if exists pixel_diffs")
    
    c.execute('''CREATE TABLE pixel_diffs (timestamp int, x int, y int, colour int)''')
    
    for curDiff in  all_diffs:
        c.execute("INSERT INTO pixel_diffs VALUES " + curDiff.getSQLiteInsertString())
    
    conn.commit()
    
    conn.close()
    
    print("completed writing pixel diffs to SQLite table")

def LoadBasePixelsintoSQLite():
    all_base_pixels = []
    
    im = Image.open("base.png")
    width, height = im.size
    
    print("starting to read in png file to get base pixel values")
    
    for outer in range(0,width):
        for inner in range(0, height):
            all_base_pixels.append(BasePixel(outer,inner,ColourReferenceLookup(im.getpixel((outer,inner)))))
            
            
    print("completed reading in png file to get base pixel values")    
    
    print("starting to write base pixel to SQLite table")
    
    conn = sqlite3.connect('PlaceData.db')
    c = conn.cursor()
    
    c.execute("drop table if exists pixel_base") 
    
    c.execute('''CREATE TABLE pixel_base (x int, y int, colour int)''')
    
    for curPixel in  all_base_pixels:
        c.execute("INSERT INTO pixel_base VALUES " + curPixel.getSQLiteInsertString())
    
    conn.commit()
    
    conn.close()
    
    print("completed writing base pixel to SQLite table")
    
def GetPixelColour(pixel_timestamp, x, y):
    
    conn = sqlite3.connect('PlaceData.db')
    c = conn.cursor()
    
    #look up the base pixel colour
    t = (x, y)    
    c.execute('SELECT * FROM pixel_base WHERE x=? AND y=?', t)
    result_base = c.fetchone()
    
    if result_base is None:
        raise ValueError('Failed to lookup base pixel value for x = ' + str(x) + ' y = ' + str(y))
 
    base_colour = result_base[2]
    
    #check to see if the pixel changes for the given timestamp, get the colour value for the most recent timestamp if it does
    t = (x, y, pixel_timestamp)
    c.execute('SELECT colour FROM pixel_diffs WHERE x=? AND y=? AND timestamp <= ? ORDER BY timestamp DESC', t)
    result_diff = c.fetchone()
    
    if result_diff is None:
        return base_colour
    else:
        return result_diff[0]
    
    
    
if __name__ == "__main__":
    LoadPixelDiffsIntoSQLite()
    LoadBasePixelsintoSQLite()
    
    print(GetPixelColour(1490992863, 682, 504))
    print(GetPixelColour(1490992865, 682, 504))
    print(GetPixelColour(1490992866, 682, 504))
    print(GetPixelColour(1491129186, 682, 504))
    print(GetPixelColour(1491129185, 682, 504))
            