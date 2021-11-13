#!/bin/python3
import sys
from PIL import Image, ImageDraw
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

wg5borders_grid = wg5borders.grid(pixelmap)
wg5borders_grid = wg5borders.grid_gradients(wg5borders_grid)
wg5borders_grid = wg5borders.border_points_from_grid(pixelmap, wg5borders_grid)
wg5borders_segments = wg5borders.segment_from_border_points(wg5borders_grid)
wg5borders_segments = wg5borders.linear_reduce_segments(wg5borders_segments)

# dump border segments to the picture
draw = ImageDraw.Draw(image)
for col in wg5borders_segments:
    for cell in col:
        for segment in cell:
            if segment is not False:
                draw.line((segment.start_x, segment.start_y, segment.end_x, segment.end_y), fill=128)
                image.putpixel((segment.start_x, segment.start_y), (255, 0, 0))
                image.putpixel((segment.end_x, segment.end_y), (0, 0, 255))


# dump border points to the picture
#for col in wg5borders_grid:
#    for cell in col:
#        for point in cell:
#            pixel = (0, 0, 0)
#            if point.direction == 1:
#                pixel = (255, 0, 0)
#            elif point.direction == 2:
#                pixel = (0, 255, 0)
#            elif point.direction == 3:
#                pixel = (0, 0, 255)
#            elif point.direction == 4:
#                pixel = (255, 128, 0)
#            image.putpixel((point.x, point.y), pixel)

image.save('out.jpg', quality=95)
