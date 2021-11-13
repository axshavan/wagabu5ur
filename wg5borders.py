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


def grayscale_from_rgb(pixel) -> float:
    return (pixel[0] + pixel[1] + pixel[2]) / 3  # todo: make it less ugly


def grid(pixelmap, grid_step: int = 0) -> list:
    grid_step = int(grid_step)
    if grid_step < 1:
        grid_step = GRID_STEP
    x = 0
    grid = []
    for col in pixelmap:
        if x % grid_step == 0:
            y = 0
            grid_col = []
            for pixel in col:
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
    x = 0
    for col in grid:
        y = 0
        for node in col:
            if y > 0 and x < max_x:
                node.gradient_tr = node.pixel - grid[x + 1][y - 1].pixel
            if y < max_y:
                node.gradient_b = node.pixel - grid[x][y + 1].pixel
                if x < max_x:
                    node.gradient_br = node.pixel - grid[x + 1][y + 1].pixel
            if x < max_x:
                node.gradient_r = node.pixel - grid[x + 1][y].pixel
            grid[x][y] = node
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
        for node in col:
            y = 0
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
                border_points.append(border_point)
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
                border_points.append(border_point)
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
                border_points.append(border_point)
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
                border_points.append(border_point)
            y += 1
        x += 1
    return border_points


def reduce_border_points(border_points: list) -> list:
    reduced_border_points = []
    for i in range(0, len(border_points) - 1):
        if border_points[i].direction == 0:
            continue
        for j in range(i + 1, len(border_points)):
            if border_points[j].x - 1 <= border_points[i].x <= border_points[j].x + 1 and border_points[j].y - 1 <= border_points[i].y <= border_points[j].y + 1:
                border_points[j].direction = 0
            else:
                if border_points[i].x == border_points[j].x and abs(border_points[i].y - border_points[j].y) <= GRID_STEP:
                    for k in range(j + 1, len(border_points)):
                        if border_points[j].x == border_points[k].x and abs(border_points[j].y - border_points[k].y) <= GRID_STEP:
                            border_points[j].direction = 0
                if border_points[i].y == border_points[j].y and abs(border_points[i].x - border_points[j].x) <= GRID_STEP:
                    for k in range(j + 1, len(border_points)):
                        if border_points[j].y == border_points[k].y and abs(border_points[j].x - border_points[k].x) <= GRID_STEP:
                            border_points[j].direction = 0
        reduced_border_points.append(border_points[i])
    return reduced_border_points
