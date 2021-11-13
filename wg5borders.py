#!/bin/python3

GRID_STEP_X = 5
GRID_STEP_Y = 5
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
    direction = 0  # 0 - horizontal, 1 - vertical, 2 - diagonal tl-br, 3 - diagonal tr-bl


def grid(pixelmap, step_x: int = 0, step_y: int = 0) -> list:
    step_x = int(step_x)
    step_y = int(step_y)
    if step_x < 1:
        step_x = GRID_STEP_X
    if step_y < 1:
        step_y = GRID_STEP_Y
    x = 0
    y = 0
    grid = []
    for col in pixelmap:
        if x % step_x == 0:
            y = 0
            grid_col = []
            for pixel in col:
                if y % step_y == 0:
                    grid_node = WG5GridNode()
                    grid_node.x = x
                    grid_node.y = y
                    grid_node.pixel = (pixel[0] + pixel[1] + pixel[2]) / 3  # todo: convert to grayscale
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
                print(x,y)
                node.gradient_b = node.pixel - grid[x][y + 1].pixel
                if x < max_x:
                    node.gradient_br = node.pixel - grid[x + 1][y + 1].pixel
            if x < max_x:
                node.gradient_r = node.pixel - grid[x + 1][y].pixel
            grid[x][y] = node
            y += 1
        x += 1
    return grid


def borders_from_grid(pixelmap: list, grid: list) -> list:
    border_points = []
    x = 0
    for col in grid:
        for node in col:
            y = 0
            if abs(node.gradient_tr) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = 2
                border_point.x = node.x
                border_point.y = node.y
                border_points.append(border_point)
            if abs(node.gradient_r) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = 1
                border_point.x = node.x
                border_point.y = node.y
                border_points.append(border_point)
            if abs(node.gradient_b) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = 0
                border_point.x = node.x
                border_point.y = node.y
                border_points.append(border_point)
            if abs(node.gradient_br) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = 3
                border_point.x = node.x
                border_point.y = node.y
                border_points.append(border_point)
            y += 1
        x += 1
    return border_points
