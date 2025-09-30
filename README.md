# Hi
This script turns a source video into a "digitized" version of it. Example input and output in `examples/`

## Install dependencies
```
pip3 install -r requirements.txt
```

## Run an example
The following example runs the script on the file `examples/SUNP0037.mp4` with a single cell of size 5, font size of the letters .15 and a baseline brightness of 10. `-d` shows you the render as it goes.
```
python3 digital.py -u examples -n "SUNP0037" -s 5 -f .15 -b 10 -d
```
