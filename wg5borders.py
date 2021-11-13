#!/bin/python3

GRID_STEP = 5
BORDER_THRESHOLD = 25


class WG5GridNode:
    x = 0
    y = 0
    gradient_tr = 0  # top-right
    gradient_r = 0  # right
    gradient_br = 0  # bottom-right
    gradient_b = 0  # bottom
    pixel = []


class WG5BorderPoint:
    x = 0
    y = 0
    direction = 0  # 0 - not sure, 1 - vertical, 2 - diagonal bl-tr, 3 - horizontal, 4 - diagonal tl-br


class WG5Segment:
    start_x = 0
    start_y = 0
    end_x = 0
    end_y = 0
    rotation = 0
    direction = 0  # 0 - not sure, 1 - vertical, 2 - diagonal bl-tr, 3 - horizontal, 4 - diagonal tl-br

def grayscale_from_rgb(pixel) -> float:
    return (pixel[0] + pixel[1] + pixel[2]) / 3  # todo: make it less ugly


def grid(pixelmap, grid_step: int = 0) -> list:
    grid_step = int(grid_step)
    if grid_step < 1:
        grid_step = GRID_STEP
    grid = []
    for x in range(0, len(pixelmap)):
        if x % grid_step == 0:
            y = 0
            grid_col = []
            for pixel in pixelmap[x]:
                if y % grid_step == 0:
                    grid_node = WG5GridNode()
                    grid_node.x = x
                    grid_node.y = y
                    grid_node.pixel = grayscale_from_rgb(pixel)
                    grid_col.append(grid_node)
                y += 1
            grid.append(grid_col)
        x += 1
    return grid


def grid_gradients(grid: list) -> list:
    max_x = len(grid) - 1
    max_y = len(grid[max_x]) - 1
    for x in range(0, max_x + 1):
        for y in range(0, max_y + 1):
            if y > 0 and x < max_x:
                grid[x][y].gradient_tr = grid[x][y].pixel - grid[x + 1][y - 1].pixel
            if y < max_y:
                grid[x][y].gradient_b = grid[x][y].pixel - grid[x][y + 1].pixel
                if x < max_x:
                    grid[x][y].gradient_br = grid[x][y].pixel - grid[x + 1][y + 1].pixel
            if x < max_x:
                grid[x][y].gradient_r = grid[x][y].pixel - grid[x + 1][y].pixel
            y += 1
        x += 1
    return grid


def get_gradient_middle(gradient_set: list) -> int:
    diff_set = []
    max_diff = 0.0
    for a in range(0, len(gradient_set)):
        diff = abs(gradient_set[a] - gradient_set[a - 1]) if a > 0 else 0
        max_diff = max(max_diff, diff)
        diff_set.append(diff)
    for a in range(0, len(diff_set)):
        if diff_set[a] == max_diff:
            return a
    return 0


def border_points_from_grid(pixelmap: list, grid: list) -> list:
    border_points = []
    x = 0
    pixelmap_maxx = len(pixelmap) - 1
    pixelmap_maxy = len(pixelmap[pixelmap_maxx]) - 1
    for col in grid:
        border_points_col = []
        y = 0
        for node in col:
            border_points_cell = []
            if abs(node.gradient_tr) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = 4
                gradient_set = []
                for i in range(0, GRID_STEP + 1):
                    if node.x + i > pixelmap_maxx:
                        break
                    if node.y - i < 0:
                        break
                    gradient_set.append(grayscale_from_rgb(pixelmap[node.x + i][node.y - i]))
                i = get_gradient_middle(gradient_set)
                border_point.x = node.x + i
                border_point.y = node.y - i
                border_points_cell.append(border_point)
            if abs(node.gradient_r) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = 1
                gradient_set = []
                for i in range(0, GRID_STEP + 1):
                    if node.x + i > pixelmap_maxx:
                        break
                    gradient_set.append(grayscale_from_rgb(pixelmap[node.x + i][node.y]))
                i = get_gradient_middle(gradient_set)
                border_point.x = node.x + i
                border_point.y = node.y
                border_points_cell.append(border_point)
            if abs(node.gradient_b) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = 3
                gradient_set = []
                for i in range(0, GRID_STEP + 1):
                    if node.y + i > pixelmap_maxy:
                        break
                    gradient_set.append(grayscale_from_rgb(pixelmap[node.x][node.y + i]))
                i = get_gradient_middle(gradient_set)
                border_point.x = node.x
                border_point.y = node.y + i
                border_points_cell.append(border_point)
            if abs(node.gradient_br) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = 2
                gradient_set = []
                for i in range(0, GRID_STEP + 1):
                    if node.x + i > pixelmap_maxx:
                        break
                    if node.y + i > pixelmap_maxy:
                        break
                    gradient_set.append(grayscale_from_rgb(pixelmap[node.x + i][node.y + i]))
                i = get_gradient_middle(gradient_set)
                border_point.x = node.x + i
                border_point.y = node.y + i
                border_points_cell.append(border_point)
            border_points_col.append(border_points_cell)
            y += 1
        border_points.append(border_points_col)
        x += 1
    return border_points


def segment_from_border_points(grid: list) -> list:
    segments_list = []
    grid_maxx = len(grid) - 1
    grid_maxy = len(grid[grid_maxx]) - 1
    for x in range(0, grid_maxx + 1):
        segments_list_col = []
        for y in range(0, grid_maxy + 1):
            segments_list_cell = []
            for c in grid[x][y]:
                if (c.direction == 0 or c.direction == 1) and y < grid_maxy:
                    for r in grid[x][y + 1]:
                        if r.direction == 0 or r.direction == 1:
                            segment = WG5Segment()
                            segment.start_x = c.x
                            segment.start_y = c.y
                            segment.end_x = r.x
                            segment.end_y = r.y
                            segment.rotation = 0
                            segment.direction = 1
                            segments_list_cell.append(segment)
                            break
                if (c.direction == 0 or c.direction == 2) and 0 < y and x < grid_maxx:
                    for r in grid[x + 1][y - 1]:
                        if r.direction == 0 or r.direction == 2:
                            segment = WG5Segment()
                            segment.start_x = c.x
                            segment.start_y = c.y
                            segment.end_x = r.x
                            segment.end_y = r.y
                            segment.rotation = 90
                            segment.direction = 2
                            segments_list_cell.append(segment)
                            break
                if (c.direction == 0 or c.direction == 3) and x < grid_maxx:
                    for r in grid[x + 1][y]:
                        if r.direction == 0 or r.direction == 3:
                            segment = WG5Segment()
                            segment.start_x = c.x
                            segment.start_y = c.y
                            segment.end_x = r.x
                            segment.end_y = r.y
                            segment.rotation = 45
                            segment.direction = 3
                            segments_list_cell.append(segment)
                            break
                if (c.direction == 0 or c.direction == 4) and y < grid_maxy and x < grid_maxx:
                    for r in grid[x + 1][y + 1]:
                        if r.direction == 0 or r.direction == 4:
                            segment = WG5Segment()
                            segment.start_x = c.x
                            segment.start_y = c.y
                            segment.end_x = r.x
                            segment.end_y = r.y
                            segment.rotation = -45
                            segment.direction = 4
                            segments_list_cell.append(segment)
                            break
            segments_list_col.append(segments_list_cell)
        segments_list.append(segments_list_col)
    return segments_list


def linear_reduce_segments(segments_list: list) -> list:
    maxx = len(segments_list) - 1
    maxy = len(segments_list[maxx]) - 1
    for x in range(0, maxx + 1):
        for y in range(0, maxy + 1):
            for i in range(0, len(segments_list[x][y])):
                if segments_list[x][y][i] is not False:
                    if (segments_list[x][y][i].direction == 0 or segments_list[x][y][i].direction == 1) and y < maxy:
                        for j in range(0, len(segments_list[x][y + 1])):
                            if segments_list[x][y + 1][j] is not False and (segments_list[x][y + 1][j].direction == 0 or segments_list[x][y + 1][j].direction == 1):
                                segments_list[x][y][i].end_x = segments_list[x][y + 1][j].end_x
                                segments_list[x][y][i].end_y = segments_list[x][y + 1][j].end_y
                                segments_list[x][y + 1][j] = False
                                break
                    if (segments_list[x][y][i].direction == 0 or segments_list[x][y][i].direction == 2) and 0 < y and x < maxx:
                        for j in range(0, len(segments_list[x + 1][y - 1])):
                            if segments_list[x + 1][y - 1][j] is not False and (segments_list[x + 1][y - 1][j].direction == 0 or segments_list[x + 1][y - 1][j].direction == 2):
                                segments_list[x][y][i].end_x = segments_list[x + 1][y - 1][j].end_x
                                segments_list[x][y][i].end_y = segments_list[x + 1][y - 1][j].end_y
                                segments_list[x + 1][y - 1][j] = False
                                break
                    if (segments_list[x][y][i].direction == 0 or segments_list[x][y][i].direction == 3) and x < maxx:
                        for j in range(0, len(segments_list[x + 1][y])):
                            if segments_list[x + 1][y][j] is not False and (segments_list[x + 1][y][j].direction == 0 or segments_list[x + 1][y][j].direction == 3):
                                segments_list[x][y][i].end_x = segments_list[x + 1][y][j].end_x
                                segments_list[x][y][i].end_y = segments_list[x + 1][y][j].end_y
                                segments_list[x + 1][y][j] = False
                                break
                    if (segments_list[x][y][i].direction == 0 or segments_list[x][y][i].direction == 4) and y < maxy and x < maxx:
                        for j in range(0, len(segments_list[x + 1][y + 1])):
                            if segments_list[x + 1][y + 1][j] is not False and (segments_list[x + 1][y + 1][j].direction == 0 or segments_list[x + 1][y + 1][j].direction == 4):
                                segments_list[x][y][i].end_x = segments_list[x + 1][y + 1][j].end_x
                                segments_list[x][y][i].end_y = segments_list[x + 1][y + 1][j].end_y
                                segments_list[x + 1][y + 1][j] = False
                                break

    return segments_list
