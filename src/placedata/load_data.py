'''
Created on 4 Apr 2017

@author: FlakeGunner
'''
from PIL import Image
from collections import defaultdict
import sqlite3
import struct
import datetime
import os
import tempfile
import imageio
import logging

def ColourLookupRGBToKey(rgb_tuple):
    colour_reference = dict()
    colour_reference[0] = (255,255,255) #FFFFFF
    colour_reference[1] = (228,228,228) #E4E4E4
    colour_reference[2] = (136,136,136) #888888
    colour_reference[3] = (34,34,34) #222222
    colour_reference[4] = (255,167,209) #FFA7D1
    colour_reference[5] = (229,0,0) #E50000
    colour_reference[6] = (229,149,0) #E59500
    colour_reference[7] = (160,106,66) #A06A42
    colour_reference[8] = (229,217,0) #E5D900
    colour_reference[9] = (148,224,68) #94E044
    colour_reference[10] = (2,190,1) #02BE01
    colour_reference[11] = (0,211,221) #00D3DD
    colour_reference[12] = (0,131,199) #0083C7
    colour_reference[13] = (0,0,234) #0000EA
    colour_reference[14] = (207,110,228) #CF6EE4
    colour_reference[15] = (130,0,128) #820080
    
    for colour_key, colour_value in colour_reference.items():
        if colour_value == rgb_tuple:
            return colour_key
        
    raise ValueError('Failed to lookup colour reference')

def ColourLookupKeyToRGB(colour_key):
    colour_reference = dict()
    colour_reference[0] = (255,255,255) #FFFFFF
    colour_reference[1] = (228,228,228) #E4E4E4
    colour_reference[2] = (136,136,136) #888888
    colour_reference[3] = (34,34,34) #222222
    colour_reference[4] = (255,167,209) #FFA7D1
    colour_reference[5] = (229,0,0) #E50000
    colour_reference[6] = (229,149,0) #E59500
    colour_reference[7] = (160,106,66) #A06A42
    colour_reference[8] = (229,217,0) #E5D900
    colour_reference[9] = (148,224,68) #94E044
    colour_reference[10] = (2,190,1) #02BE01
    colour_reference[11] = (0,211,221) #00D3DD
    colour_reference[12] = (0,131,199) #0083C7
    colour_reference[13] = (0,0,234) #0000EA
    colour_reference[14] = (207,110,228) #CF6EE4
    colour_reference[15] = (130,0,128) #820080
    
    return colour_reference[colour_key]
        

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

def DropAllTables():
    conn = sqlite3.connect('PlaceData.db')
    c = conn.cursor()
    
    logging.info("Dropping all tables")
    
    c.execute("drop table if exists pixel_diffs")
    
    c.execute("drop table if exists pixel_base")
    
    conn.commit()
    
    conn.close()
    
    logging.info("Finished dropping all tables")
    

def PopulateSQLiteWithPixelDiffs():
    all_diffs = []
    logging.info("starting to read in binary data")
    
    with open("diffs.bin", "rb") as binary_file:
        binary_file.seek(0)
        pixel_diff_bytes = binary_file.read(16)
        while pixel_diff_bytes:
            pixel_diff_tuple = struct.unpack('<IIII', pixel_diff_bytes)
            pixel_diff = DiffPixel(pixel_diff_tuple[0], pixel_diff_tuple[1], pixel_diff_tuple[2], pixel_diff_tuple[3])
            all_diffs.append(pixel_diff)
            pixel_diff_bytes = binary_file.read(16)
            
    logging.info("completed reading in binary data")
    
    logging.info("starting to write pixel diffs to SQLite table")
            
    conn = sqlite3.connect('PlaceData.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE pixel_diffs (timestamp int, x int, y int, colour int)''')
    
    c.execute('''CREATE INDEX pixel_diffs_index ON pixel_diffs (timestamp, x, y)''')
    
    for curDiff in  all_diffs:
        c.execute("INSERT INTO pixel_diffs VALUES " + curDiff.getSQLiteInsertString())
    
    conn.commit()
    
    conn.close()
    
    logging.info("completed writing pixel diffs to SQLite table")
    

def PopulateSQLiteWithBasePixels():
    all_base_pixels = []
    
    im = Image.open("base.png")
    width, height = im.size
    
    logging.info("starting to read in png file to get base pixel values")
    
    for outer in range(0,width):
        for inner in range(0, height):
            all_base_pixels.append(BasePixel(outer,inner,ColourLookupRGBToKey(im.getpixel((outer,inner)))))
            
            
    logging.info("completed reading in png file to get base pixel values")    
    
    logging.info("starting to write base pixel to SQLite table")
    
    conn = sqlite3.connect('PlaceData.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE pixel_base (x int, y int, colour int)''')
    
    c.execute('''CREATE INDEX pixel_base_index ON pixel_base (x, y)''')
    
    for curPixel in  all_base_pixels:
        c.execute("INSERT INTO pixel_base VALUES " + curPixel.getSQLiteInsertString())
    
    conn.commit()
    
    conn.close()
    
    logging.info("completed writing base pixel to SQLite table")
    
    
def VerifyTableExists(table_name):
    conn = sqlite3.connect('PlaceData.db')
    c = conn.cursor()
    
    t = ("table", table_name)
    c.execute('SELECT name FROM sqlite_master WHERE type=? AND name=?', t)
    if c.fetchone() is None:
        raise ValueError("SQLite table: " + table_name + " does not exist, make sure you have populated SQLite tables")
    
    conn.close()
    
    
def LoadBasePixelsIntoMemory():
    VerifyTableExists("pixel_base")
    
    logging.info("loading base pixels into memory")
    #select all from pixel base table and store in dictionary
    conn = sqlite3.connect('PlaceData.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM pixel_base')
    
    base_pixels = {}
    
    for row in c.fetchall():
        base_pixels[(row[0],row[1])] = row[2]
    
    conn.close()
    
    logging.info("finished loading base pixels into memory")
    
    return base_pixels

def LoadDiffPixelsIntoMemory():
    VerifyTableExists("pixel_diffs")
    
    logging.info("loading pixel diffs into memory")
    #select all from pixel diffs table and store in dictionary
    conn = sqlite3.connect('PlaceData.db')
    c = conn.cursor()
    
    c.execute('SELECT * FROM pixel_diffs')
    
    pixel_diffs = defaultdict(list)
    
    for row in c.fetchall():
        pixel_diffs[(row[1],row[2])].append((row[0],row[3]))
        
    logging.info("finished loading pixel diffs into memory")
    
    return pixel_diffs
    
        
def GetPixelColour(pixel_timestamp, x, y, base_pixels, pixels_diffs):
    min_timestamp = 1490986860 #we don't have data before this timestamp
    
    #look up the base pixel colour
    base_colour = base_pixels[(x,y)]
    
    #if timestamp is before data starts, return base pixel
    if pixel_timestamp < min_timestamp:
        return base_colour
    
    
    diffs = pixels_diffs[x, y]
    
    #if there's no diffs for that pixel return base pixel
    if not diffs:
        return base_colour
    
    #if timestamp is less that first diff return base value
    if pixel_timestamp < diffs[0][0]:
        return base_colour
    
    #look through diffs to get closest diff
    for previous_diff, current_diff in zip(diffs, diffs[1:]):
        if pixel_timestamp == current_diff[0]:
            return current_diff[1]
        elif  pixel_timestamp < current_diff[0]:
            return previous_diff[1]
        
    #if there's no diff that matches return last pixel value in diffs
    return diffs[-1][1]
        
def GeneratePNG(png_timestamp, x1, y1, x2, y2, base_pixels, pixels_diffs, output_path = None, filename = None):
    #validate timestamp and x,y inputs
    if png_timestamp < 0:
        raise ValueError("Negative timestamp in generate png")
    if x2 <= x1:
        raise ValueError("x2 can't be equal or smaller than x1")
    if y2 <= y1:
        raise ValueError("y2 can't be equal or smaller than y1")
    if x1 < 0 or x1 > 999:
        raise ValueError("Bad x1 value in generate png")
    if y2 <= y1 or y1 < 0 or y1 > 999:
        raise ValueError("Bad y1 value in generate png")
    if x2 < 0 or x2 > 999:
        raise ValueError("Bad x2 value in generate png")
    if y2 < 0 or y2 > 999:
        raise ValueError("Bad y2 value in generate png")
    
    #set file output path and name
    if filename is None:
        filename = "place_" + str(png_timestamp) + "_" + str(x1) + "_" + str(y1) + "_" + str(x2) + "_" + str(y2) + ".png"
    
    logging.info("beginning to generate output image: " + filename)
    
    os.chdir(os.path.dirname(__file__))
    
    if output_path is None:
        outdir = os.getcwd()
    else:
        outdir = output_path
    
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    
    outfile = os.path.join(outdir, filename)
    
    #create output image and lookup pixel colour values
    im = Image.new( 'RGB', (x2 - x1 + 1, y2 - y1 + 1), "black")
    pixels = im.load() 
    for i in range(im.size[0]):   
        for j in range(im.size[1]):
            colour_key = GetPixelColour(png_timestamp, x1 + i, y1 + j, base_pixels, pixels_diffs)
            pixels[i,j] = ColourLookupKeyToRGB(colour_key)
            
    im.save(outfile, "PNG")
            
    logging.info("Completed generating output image: " + filename)
    
def GeneratePNGSequence(sequence_timestamp, length_sequence, length_step, x1, y1, x2, y2, base_pixels, pixels_diffs, out_path = None):
    logging.info("Started generating PNG Sequence")

    if out_path is None:
        out_path = os.path.join(os.getcwd(), "seq_" + str(x1) + "_" + str(y1) + "_" + str(x2) + "_" + str(y2))
    
    for index in range(length_sequence):
        GeneratePNG(sequence_timestamp + (index * length_step), x1, y1, x2, y2, base_pixels, pixels_diffs, out_path, str(sequence_timestamp + (index * length_step)) + ".png")
        
    logging.info("Finished generating PNG Sequence")

def GenerateGif(sequence_timestamp, length_sequence, length_step, x1, y1, x2, y2, base_pixels, pixels_diffs):
    logging.info("Started generating Gif")
    #create temp folder to hold intermediate pngs
    temp_dir = tempfile.TemporaryDirectory()
    GeneratePNGSequence(sequence_timestamp, length_sequence, length_step, x1, y1, x2, y2, base_pixels, pixels_diffs, temp_dir.name)
    
    frames = []
    
    for root, dirs, filenames in os.walk(temp_dir.name):
        for filename in filenames:
            if filename.endswith(".png"):
                frames.append(imageio.imread(os.path.join(temp_dir.name, filename)))
                
    kargs = { 'fps' : 60.0 }
    
    filename = str(sequence_timestamp) + "_" + str(x1) + "_" + str(y1) + "_" + str(x2) + "_" + str(y2) + "_" + str(length_sequence) + ".gif"
    
    imageio.mimsave(filename, frames, 'GIF-PIL', **kargs)
    
    logging.info("Finished generating Gif")
    
def main():
    FORMAT = '%(asctime)s - %(message)s'
    logging.basicConfig(format=FORMAT, filename='place_data.log', level=logging.INFO)
    
    logging.info("Starting up")
    
    
    DropAllTables()
    PopulateSQLiteWithPixelDiffs()
    PopulateSQLiteWithBasePixels()

    
    
    diff_pixels = LoadDiffPixelsIntoMemory()
    base_pixels = LoadBasePixelsIntoMemory()
    
    GeneratePNG(50, 0, 0, 999, 999, base_pixels, diff_pixels, "out_png", "filename.png")
    GeneratePNG(1491503573, 0, 0, 999, 999, base_pixels, diff_pixels, "out_png")
    GeneratePNG(1491080102, 0, 0, 999, 999, base_pixels, diff_pixels, "out_png")
    GeneratePNG(1491503573, 0, 0, 999, 999, base_pixels, diff_pixels, "out_png")
            
    GeneratePNGSequence(1491080102, 200, 120, 441, 615, 519, 733, base_pixels, diff_pixels, "blah")
    
    GeneratePNGSequence(1491080102, 200, 120, 441, 615, 519, 733, base_pixels, diff_pixels)
    GenerateGif(1490986860, 419, 600, 424, 523, 529, 750, base_pixels, diff_pixels)
    
    logging.info("Finished")
    
if __name__ == "__main__":
    main()
    
    