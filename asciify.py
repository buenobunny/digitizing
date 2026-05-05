import cv2
import numpy as np
import math
import random
import argparse
import time
from PIL import ImageFont, ImageDraw, Image
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--filename", help="File name without extension")
parser.add_argument("-s", "--blocksize", help="how big for a single cell (int)")
parser.add_argument("-d", "--display", help="should i display while doing", action=argparse.BooleanOptionalAction)
parser.add_argument("-a", "--append", help="file name appendage (file-<append>.mp4)")
parser.add_argument("-f", "--textsize", help="text size (int)")
parser.add_argument("-b", "--baseline", help="baseline brightness (int)")
parser.add_argument("-u", "--subdir", help="subdirectory to I/O from")
parser.add_argument("-t", "--typefont", help="what typefont file to use, full path (ttf)")
parser.add_argument("-m", "--multiplier", help="how much to multiply the brightness by, useful for adding contrast")

args = parser.parse_args()

if args.filename is None:
    raise Exception("but which file")

filename = args.filename

# TODO: add support for different input codecs
location = f"./{args.subdir}/{filename}.mp4" if args.subdir else f"{filename}.mp4"

# read the file given
cap = cv2.VideoCapture(location)

fps = cap.get(cv2.CAP_PROP_FPS)

blocksize = int(args.blocksize) or 20

# as opposed to digital.py, we must snap the height to nearest ceiling multiple of blocksize
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) - (cap.get(cv2.CAP_PROP_FRAME_WIDTH) % blocksize))
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) - (cap.get(cv2.CAP_PROP_FRAME_HEIGHT) % blocksize))
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

letter_size = float(args.textsize) if args.textsize is not None else .5

brightness_baseline = int(args.baseline) if args.baseline is not None else 10
multiplier = float(args.multiplier) if args.baseline is not None else 1

shouldDisplay = True if args.display is not None else False

appendage = args.append if args.append is not None else ""

# TODO: add support for different output codecs
writeName = f"{filename}-digitized{appendage}.mp4"
writeLocation = f"./{args.subdir}/{writeName}" if args.subdir else writeName
# start a file output
output = cv2.VideoWriter(writeLocation,cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))

# TODO: argument to take a csv file for the words
def read_file_lines(filename):
    with open(filename, 'r') as f:
        lines = [line.rstrip('\n') for line in f]
    return lines
# word choices!

char_by_brightness = [" ", ".", ",", ":", "*", "|", "+", "@", "#"]
# you can use more if the font supports it
#char_by_brightness = [" ", ".", ",", ":", "*", "|", "+", "@", "#", "░", "▒", "▓"]

singleY = int(height/blocksize)
singleX = int(width/blocksize)

scroll_rate = 2

total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
frames = 0
print_thresholds = [(i+1)/10 for i in range(10)]
start_time = time.time()

def count():
    global frames, total_frames, print_thresholds, start_time
    frames += 1
    if len(print_thresholds) and frames/total_frames > print_thresholds[0]:
        print_amt_left(frames, start_time, frames/total_frames)
        print_thresholds.pop(0)

def convert(seconds):
    min, sec = divmod(seconds, 60)
    hour, min = divmod(min, 60)
    return '%d:%02d:%02d' % (hour, min, sec)

def print_amt_left(curr_frames, start_time, percent_processed):
    total_time = time.time() - start_time
    remaining = (1 - percent_processed) * total_time / percent_processed
    print(f"{percent_processed:.0%} processed in {convert(total_time)}, remaining: {convert(remaining)}")

font = ImageFont.truetype('/Users/alexanderparra/Library/Fonts/VCR_OSD_MONO_1.001.ttf', size=letter_size)

print("running, click on the frame then press q to stop")

while (cap.isOpened()):

    ret, frame = cap.read()

    if frame is None:
        break
    frame = frame[:singleY*blocksize,:singleX*blocksize,:]

    # easier to read colors in grayscale apparently
    simple_avg = frame.mean(axis=2)
    blocks = simple_avg.reshape(singleY, blocksize, singleX, blocksize)
    blocks_avg = blocks.mean(axis=(1, 3))
    black = np.full((height, width, 3), 0, dtype=np.uint8)
    pilImg = Image.fromarray(black)
    draw = ImageDraw.Draw(pilImg)
    draw.rectangle(xy=[0,100,0,200], fill='red')

    for y in range(singleY):
        startY = (y)*blocksize
        for x in range(singleX):
            startX = (x)*blocksize
            avg = blocks_avg[y,x%singleX]
            brightness = (avg + brightness_baseline) / 255 * multiplier
            char_index = math.floor(brightness * len(char_by_brightness))
            char_index = 0 if char_index < 0 else char_index
            char_index = len(char_by_brightness) - 1 if char_index >= len(char_by_brightness) else char_index
            draw.text((startX,startY), char_by_brightness[char_index], (255,255,255), font=font)
    processed = np.array(pilImg)
    output.write(processed)
    count()

    if shouldDisplay:
        cv2.imshow('Digitized', processed)
    # define q as the exit button
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

end_time = time.time()
print(f"ending and releasing, avg frame time: {(end_time - start_time)/frames:.2f}s")
# release the video capture object
output.release()
cap.release()
# Closes all the windows currently opened.
cv2.destroyAllWindows()
