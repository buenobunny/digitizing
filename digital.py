import cv2
import numpy as np
import math
import random
import argparse
import time
parser = argparse.ArgumentParser()
parser.add_argument("-n", "--filename", help="File name")
parser.add_argument("-s", "--single", help="how big for a single cell")
parser.add_argument("-d", "--display", help="should i display while doing", action=argparse.BooleanOptionalAction)
parser.add_argument("-a", "--append", help="file name append")
parser.add_argument("-f", "--text", help="text size")
parser.add_argument("-b", "--baseline", help="baseline brightness")
parser.add_argument("-u", "--subdir", help="any subdirectory")

args = parser.parse_args()

if args.filename is None:
    raise Exception("but which file")

filename = args.filename

# TODO: add support for different input codecs
location = f"./{args.subdir}/{filename}.mp4" if args.subdir else f"{filename}.mp4"

# read the file given
cap = cv2.VideoCapture(location)

fps = cap.get(cv2.CAP_PROP_FPS)

width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

letter_size = float(args.text) if args.text is not None else .5

brightness_baseline = int(args.baseline) if args.baseline is not None else 10

shouldDisplay = True if args.display is not None else False

appendage = args.append if args.append is not None else ""

# TODO: add support for different output codecs
writeName = f"{filename}-digitized{appendage}.mp4"
writeLocation = f"./{args.subdir}/{writeName}" if args.subdir else writeName
# start a file output
output = cv2.VideoWriter(writeLocation,cv2.VideoWriter_fourcc(*'mp4v'),fps,(width,height))

single = int(args.single) or 20

# TODO: argument to take a csv file for the words
# word choices!
s = ["akissfromabove","onmyknees","istarttopray",
"thoughticould","thecryingmoon","fallinginthecloud",
".zip",".mp3",".txt","ASSERTIONFAILED!!!",".wav",
"whowillyoube","THECLOUD","lingersintheair","whatsonyourmind",
"VIRTUALMEMORIES","eyesonme!","meltingicedcoffee","BETTEREVERYDAY?",
"onmyown"]

numReps = math.ceil(width / single / len(s))

x_range = int(width/single)

def comeupwithaline():

    linelen = 0
    add = ""
    while linelen - 1 < width / single:
        choice = random.randint(1,len(s)-1)
        linelen += len(s[choice])
        add = add + s[choice]
    return np.array([list(add[0:x_range])])

text = comeupwithaline()

singleY = int(height/single)
singleX = int(width/single)
# fucked shit to try to get random words
for y in range(singleY-1):
    text = np.vstack([text, comeupwithaline()])

scroll_rate = 2

#counters to make the text mooove
frames = 0
counter = 0
mover = 0
def count():
    global counter, mover, frames
    if counter % scroll_rate == 0:
        mover = (mover + 1) % singleY
    counter = (counter + 1) % scroll_rate
    frames += 1

def avg_bright(frame, startX, startY):
    #get the avg rgb colors for a block starting at..
    return np.mean(frame[startY:startY + single, startX:startX + single])
print("running, click on the frame then press q to stop")
start_time = time.time()

while (cap.isOpened()):

    ret, frame = cap.read()

    if frame is None:
        break

    # easier to read colors in grayscale apparently
    simple_avg = frame.mean(axis=2)
    blocks = simple_avg.reshape(singleY, single, singleX, single)
    blocks_avg = blocks.mean(axis=(1, 3))
    black = np.full((height, width, 3), 0, dtype=np.uint8)

    for y in range(singleY):
        startY = (y)*single
        yText = (y-mover)%singleY
        for x in range(singleX):
            startX = (x)*single
            avg = blocks_avg[y,x-1%singleX]
            brightness = (avg + brightness_baseline) // 80
            cv2.putText(black, text[yText,x], (startX,startY + single), 
                cv2.FONT_HERSHEY_PLAIN, letter_size * math.log(brightness+1), (0,(brightness * 64),0), 1, cv2.LINE_AA)

    count()
    output.write(black)

    if shouldDisplay:
        cv2.imshow('Digitized', black)
    # define q as the exit button
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break

end_time = time.time()
print(f"ending and releasing, avg frame time: {(end_time - start_time)/frames}")
# release the video capture object
output.release()
cap.release()
# Closes all the windows currently opened.
cv2.destroyAllWindows()
