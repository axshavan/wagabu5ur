#!/bin/python3
import sys
from PIL import Image
import wg5borders

if len(sys.argv) < 2:
    print("Usage: learn.py <image>")
    exit(0)

try:
    image = Image.open(sys.argv[1])
except Exception as e:
    print("Cannot open image " + sys.argv[1] + ": " + str(e))
    exit(0)

# load image data
pixelmap = []
pixelrow = []
for x in range(image.width):
    pixelrow = []
    for y in range(image.height):
        pixel = image.getpixel((x, y))
        pixelrow.append(pixel)
    pixelmap.append(pixelrow)

wg5borders_grid = wg5borders.grid(pixelmap, wg5borders.GRID_STEPX, wg5borders.GRID_STEPY)
# ...
