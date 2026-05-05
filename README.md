# Hi
This script turns a source video into a "digitized" version of it. Example input and output in `examples/`

## Install dependencies
```
pip3 install -r requirements.txt
```

## Run an example
The following example runs the script on the file `examples/SUNP0037.mp4` with a single cell of size 5, font size of the letters .15 and a baseline brightness of 10. `-d` shows you the render as it goes.
```
python3 digital.py -u "examples" -n "SUNP0037" -s 5 -f .15 -b 10 -d
```
```
python3 asciify.py -u "examples" -n "SUNP0037" -s 10 -f 15 -b 0 -m 1.35 -a 1 -d
```

## Performance characteristics 
Both scripts are pretty slow. Much slower than actual frame rates, so it won't be realtime.
The time it takes to run the scripts is something like the following:

```
O(2^(max(width, height) / blocksize) * (width * height) * (1.5 if displayed else 1))
```

this isn't an interview so idgaf about being precise, i hope u understand what it means about the inputs and how they shape the time it takes.

Basically, it increases mostly proportionally to the width and height of the video, but the 
block size really matters. As blocksize approaches min(width, height), the time it takes
exponentially decays. So smaller blocks means exponentially longer time to run.

The scripts will tell you how much has processed and how much has left every 10%. I've had 6 hr
renders, so this is useful lol