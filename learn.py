#!/bin/python3
import sys
from PIL import Image, ImageDraw
import wg5borders
import random


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

# make lines
#wg5borders_lines = wg5borders.lines_from_segments(wg5borders_segments)

draw = ImageDraw.Draw(image)

# dump border points to the picture
if False:
    points_count = 0
    cols_count = 0
    for col in wg5borders_grid:
        cells_count = 0
        for cell in col:
            for point in cell:
                if point is not False:
                    points_count += 1
                    color = (64, 180, 64)
                    image.putpixel((point.x * 4, point.y * 4), color)
                    image.putpixel((point.x * 4 + 1, point.y * 4), color)
                    image.putpixel((point.x * 4 + 1, point.y * 4 + 1), color)
                    image.putpixel((point.x * 4, point.y * 4 + 1), color)
                    draw.line((point.x * 4, point.y * 4, cols_count * 32, cells_count * 32), fill=(200, 255, 200))
            cells_count += 1
        cols_count += 1
    print('border point count', points_count)

# dump border segments to the picture
if True:
    segments_count = 0
    segment_col_counter = 0
    for segment_col in wg5borders_segments:
        segment_cell_counter = 0
        for segment_cell in segment_col:
            for segment in segment_cell:
                if segment is not False:
                    segments_count += 1
                    draw.line((segment.start_x * 4, segment.start_y * 4, segment.end_x * 4 - 4, segment.end_y * 4), fill=(100, 100, 100))
                    draw.line((segment.start_x * 4, segment.start_y * 4, segment_col_counter * 32, segment_cell_counter * 32), fill=(200, 200, 200))
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
            segment_cell_counter += 1
        segment_col_counter += 1
    print('segments count', segments_count)

# dump segment lines to the picture
if False:
    lines_count = 0
    line_segments_count = 0
    lines_col_counter = 0
    draw = ImageDraw.Draw(image)
    for lines_col in wg5borders_lines:
        lines_cell_counter = 0
        for lines_cell in lines_col:
            for line in lines_cell:
                random_color = (random.randrange(0, 200), random.randrange(0, 200), random.randrange(0, 200))
                lines_count += 1
                if lines_count > 0:
                    segment = line.segments[0]
                    draw.line((segment.start_x * 4, segment.start_y * 4, lines_col_counter * 32, lines_cell_counter * 32), fill=(200, 200, 200))
                    for segment in line.segments:
                        line_segments_count += 1
                        draw.line((segment.start_x * 4, segment.start_y * 4, segment.end_x * 4, segment.end_y * 4), fill=random_color)
                        color = (40, 40, 40)
                        image.putpixel((segment.start_x * 4, segment.start_y * 4), color)
                        image.putpixel((segment.start_x * 4 + 1, segment.start_y * 4), color)
                        image.putpixel((segment.start_x * 4, segment.start_y * 4 + 1), color)
                        image.putpixel((segment.start_x * 4 + 1, segment.start_y * 4 + 1), color)
                        color = (200, 60, 60)
                        image.putpixel((segment.end_x * 4, segment.end_y * 4), color)
                        image.putpixel((segment.end_x * 4 + 1, segment.end_y * 4), color)
                        image.putpixel((segment.end_x * 4, segment.end_y * 4 + 1), color)
                        image.putpixel((segment.end_x * 4 + 1, segment.end_y * 4 + 1), color)
            lines_cell_counter += 1
        lines_col_counter += 1
    print('lines count', lines_count)
    print('lines segments count', line_segments_count)

image.save('out.jpg', quality=95)
