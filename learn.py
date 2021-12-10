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
wg5borders_segments = wg5borders.segments_from_border_points(wg5borders_grid)

# reduce linear segments
wg5borders_segments = wg5borders.reduce_linear_segments(wg5borders_segments)

draw = ImageDraw.Draw(image)
points_count = 0
cells_count = 0
if True:
    for col in wg5borders_grid:
        for cell in col:
            cells_count += 1
            for point in cell:
                if point is not False:
                    points_count += 1
                    color = (64, 255, 64)
                    image.putpixel((point.x * 4, point.y * 4), color)
                    image.putpixel((point.x * 4 + 1, point.y * 4), color)
                    image.putpixel((point.x * 4 + 1, point.y * 4 + 1), color)
                    image.putpixel((point.x * 4, point.y * 4 + 1), color)
    print(points_count)

# dump border segments to the picture
if True:
    segments_count = 0
    draw = ImageDraw.Draw(image)
    for segment_col in wg5borders_segments:
        for segment_cell in segment_col:
            for segment in segment_cell:
                if segment is not False:

                    # if (segment.start_x == segment.end_x and segment.start_y == segment.end_y):
                    #     print('zero len segment')

                    segments_count += 1
                    draw.line((segment.start_x * 4, segment.start_y * 4, segment.end_x * 4 - 4, segment.end_y * 4), fill=(100, 100, 100))
                    color = (200, 0, 0)
                    image.putpixel((segment.start_x * 4, segment.start_y * 4), color)
                    image.putpixel((segment.start_x * 4 + 1, segment.start_y * 4), color)
                    image.putpixel((segment.start_x * 4, segment.start_y * 4 + 1), color)
                    image.putpixel((segment.start_x * 4 + 1, segment.start_y * 4 + 1), color)
                    color = (0, 64, 200)
                    image.putpixel((segment.end_x * 4 - 4, segment.end_y * 4), color)
                    image.putpixel((segment.end_x * 4 - 3, segment.end_y * 4), color)
                    image.putpixel((segment.end_x * 4 - 4, segment.end_y * 4 + 1), color)
                    image.putpixel((segment.end_x * 4 - 3, segment.end_y * 4 + 1), color)
    print(segments_count)
image.save('out.jpg', quality=95)
