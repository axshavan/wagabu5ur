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

# create the grid of gradient points
wg5borders_grid = wg5borders.grid(pixelmap)

image = Image.new('RGB', (image.width * 4, image.height * 4), (255, 255, 255))  # to create a blank image
# dump border points to the picture
for col in wg5borders_grid:
    for point in col:
        pixel = (200, 200, 200)
        image.putpixel((point.x * 4, point.y * 4), pixel)

# calculate the gradients for the grid points
wg5borders_grid = wg5borders.grid_gradients(wg5borders_grid)

# get the border points out from the gradient grids
wg5borders_grid = wg5borders.border_points_from_grid(pixelmap, wg5borders_grid)

# reduce the number of border points
wg5borders_grid = wg5borders.reduce_border_points(wg5borders_grid)

# segments from the border points
wg5borders_segments = wg5borders.segment_from_border_points(wg5borders_grid)

# wg5borders_segments = wg5borders.remove_double_borders(wg5borders_segments)
#wg5borders_segments = wg5borders.reduce_segments(wg5borders_segments)

draw = ImageDraw.Draw(image)
points_count = 0
for col in wg5borders_grid:
    for cell in col:
        for point in cell:
            if point is not False:
                points_count += 1
                image.putpixel((point.x * 4, point.y * 4), (255, 0, 64))
                image.putpixel((point.x * 4 + 1, point.y * 4), (255, 0, 64))
                image.putpixel((point.x * 4 + 1, point.y * 4 + 1), (255, 0, 64))
                image.putpixel((point.x * 4, point.y * 4 + 1), (255, 0, 64))
print(points_count)

# dump border segments to the picture
if True:
    segments_count = 0
    draw = ImageDraw.Draw(image)
    for col in wg5borders_segments:
        for cell in col:
            for segment in cell:
                if segment is not False:
                    segments_count += 1
                    # if segment.direction == wg5borders.SEGMENT_TYPE_DIAGONAL_TLBR:
                    #     draw.line((segment.start_x * 4, segment.start_y * 4, segment.end_x * 4, segment.end_y * 4), fill=(0, 255, 0))
                    # elif segment.direction == wg5borders.SEGMENT_TYPE_DIAGONAL_BLTR:
                    #     draw.line((segment.start_x * 4, segment.start_y * 4, segment.end_x * 4, segment.end_y * 4), fill=(255, 0, 0))
                    # elif segment.direction == wg5borders.SEGMENT_TYPE_VERTICAL:
                    #     draw.line((segment.start_x * 4, segment.start_y * 4, segment.end_x * 4, segment.end_y * 4), fill=(0, 0, 255))
                    # else:
                    draw.line((segment.start_x * 4, segment.start_y * 4, segment.end_x * 4, segment.end_y * 4), fill=(0, 0, 0))
                    #image.putpixel((segment.start_x * 4, segment.start_y * 4), (64, 255, 0))
                    #image.putpixel((segment.end_x * 4, segment.end_y * 4), (0, 64, 255))
    print(segments_count)
image.save('out.jpg', quality=95)
