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
row = []
for x in range(image.width):
    row = []
    for y in range(image.height):
        pixel = image.getpixel((x, y))
        row.append(pixel)
    pixelmap.append(row)

wg5borders_grid = wg5borders.grid(pixelmap, wg5borders.GRID_STEP_X, wg5borders.GRID_STEP_Y)
wg5borders_grid = wg5borders.grid_gradients(wg5borders_grid)
wg5borders_grid = wg5borders.borders_from_grid(pixelmap, wg5borders_grid)

# dump borders to the picture
for point in wg5borders_grid:
    image.putpixel((point.x, point.y), (0, 0, 0))

image.save('out.jpg')
