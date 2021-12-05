#!/bin/python3

GRID_STEP = 8  # the size of the grid cell, in pixels
BORDER_THRESHOLD = 25  # the threshold of the difference in lightness enough to be a border
BORDER_POINTS_MERGE_THRESHOLD = 4  # max distance between border points to merge the into one, in pixels

BORDER_TYPE_VERTICAL = 1
BORDER_TYPE_DIAGONAL_BLTR = 2
BORDER_TYPE_HORIZONTAL = 3
BORDER_TYPE_DIAGONAL_TLBR = 4

SEGMENT_TYPE_VERTICAL = 1
SEGMENT_TYPE_DIAGONAL_BLTR = 2
SEGMENT_TYPE_HORIZONTAL = 3
SEGMENT_TYPE_DIAGONAL_TLBR = 4


class WG5GridNode:
    x = 0  # pixel x
    y = 0  # pixel y
    gradient_r = 0  # right
    gradient_br = 0  # bottom-right
    gradient_b = 0  # bottom
    gradient_bl = 0  # bottom-left
    pixel = []


class WG5BorderPoint:
    x = 0  # pixel x
    y = 0  # pixel y
    direction = 0


class WG5Segment:
    start_x = 0  # pixel x
    start_y = 0  # pixel y
    end_x = 0  # pixel x
    end_y = 0  # pixel y


def grayscale_from_rgb(pixel) -> float:
    return (pixel[0] + pixel[1] + pixel[2]) / 3


def grid(pixelmap) -> list:
    grid = []
    for x in range(0, len(pixelmap)):
        if x % GRID_STEP == 0:
            y = 0
            grid_col = []
            for pixel in pixelmap[x]:
                if y % GRID_STEP == 0:
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
            if y < max_y:
                grid[x][y].gradient_b = grid[x][y].pixel - grid[x][y + 1].pixel
                if x < max_x:
                    grid[x][y].gradient_br = grid[x][y].pixel - grid[x + 1][y + 1].pixel
                if x > 0:
                    grid[x][y].gradient_bl = grid[x][y].pixel - grid[x - 1][y + 1].pixel
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

            # right
            if abs(node.gradient_r) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = BORDER_TYPE_VERTICAL
                gradient_set = []
                for i in range(0, GRID_STEP + 1):
                    if node.x + i > pixelmap_maxx:
                        break
                    gradient_set.append(grayscale_from_rgb(pixelmap[node.x + i][node.y]))
                i = get_gradient_middle(gradient_set)
                border_point.x = node.x + i
                border_point.y = node.y
                border_points_cell.append(border_point)

            # bottom-right
            if abs(node.gradient_br) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = BORDER_TYPE_DIAGONAL_BLTR
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

            # bottom
            if abs(node.gradient_b) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = BORDER_TYPE_HORIZONTAL
                gradient_set = []
                for i in range(0, GRID_STEP + 1):
                    if node.y + i > pixelmap_maxy:
                        break
                    gradient_set.append(grayscale_from_rgb(pixelmap[node.x][node.y + i]))
                i = get_gradient_middle(gradient_set)
                border_point.x = node.x
                border_point.y = node.y + i
                border_points_cell.append(border_point)

            # bottom-left
            if abs(node.gradient_bl) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = BORDER_TYPE_DIAGONAL_TLBR
                gradient_set = []
                for i in range(0, GRID_STEP + 1):
                    if node.x - i < 0:
                        break
                    if node.y + i > pixelmap_maxy:
                        break
                    gradient_set.append(grayscale_from_rgb(pixelmap[node.x - i][node.y + i]))
                i = get_gradient_middle(gradient_set)
                border_point.x = node.x - i
                border_point.y = node.y + i
                border_points_cell.append(border_point)

            border_points_col.append(border_points_cell)
            y += 1
        border_points.append(border_points_col)
        x += 1
    return border_points


def compress_border_points_grid(border_points_grid: list, side_length: int) -> list:
    result_grid = {}
    grid_maxx = len(border_points_grid)
    grid_maxy = len(border_points_grid[0])
    for x in range(0, grid_maxx):
        newx = int(x / side_length)
        if newx not in result_grid:
            result_grid[newx] = {}
        for y in range(0, grid_maxy):
            newy = int(y / side_length)
            if newy not in result_grid[newx]:
                result_grid[newx][newy] = []
            for p in border_points_grid[x][y]:
                result_grid[newx][newy].append(p)
    for x in result_grid:
        result_grid[x] = list(result_grid[x].values())
    return list(result_grid.values())


def reduce_border_points(border_points_grid: list) -> list:
    border_points_grid = compress_border_points_grid(border_points_grid, 2)
    grid_maxx = len(border_points_grid) - 1
    grid_maxy = len(border_points_grid[0]) - 1
    for x in range(0, grid_maxx):
        for y in range(0, grid_maxy):
            grid_maxj = len(border_points_grid[x][y])
            for j in range(0, grid_maxj):
                p = border_points_grid[x][y][j]
                if p is not False:

                    # current cell
                    for i in range(0, grid_maxj):
                        r = border_points_grid[x][y][i]
                        if r is False:
                            continue
                        if (
                                p.direction != r.direction and
                                abs(p.x - r.x) <= BORDER_POINTS_MERGE_THRESHOLD and
                                abs(p.y - r.y) <= BORDER_POINTS_MERGE_THRESHOLD):
                            p.x = round((p.x + r.x) / 2)
                            p.y = round((p.y + r.y) / 2)
                            border_points_grid[x][y][i] = False

                    # right
                    if x < grid_maxx:
                        for i in range(0, len(border_points_grid[x + 1][y])):
                            r = border_points_grid[x + 1][y][i]
                            if r is False:
                                continue
                            if (
                                    abs(p.x - r.x) <= BORDER_POINTS_MERGE_THRESHOLD and
                                    abs(p.y - r.y) <= BORDER_POINTS_MERGE_THRESHOLD):
                                p.x = round((p.x + r.x) / 2)
                                p.y = round((p.y + r.y) / 2)
                                border_points_grid[x + 1][y][i] = False

                    # bottom-right
                    if y < grid_maxy and x < grid_maxx:
                        for i in range(0, len(border_points_grid[x + 1][y + 1])):
                            r = border_points_grid[x + 1][y + 1][i]
                            if r is False:
                                continue
                            if (
                                    abs(p.x - r.x) <= BORDER_POINTS_MERGE_THRESHOLD and
                                    abs(p.y - r.y) <= BORDER_POINTS_MERGE_THRESHOLD):
                                p.x = round((p.x + r.x) / 2)
                                p.y = round((p.y + r.y) / 2)
                                border_points_grid[x + 1][y + 1][i] = False

                    # bottom
                    if y < grid_maxx:
                        for i in range(0, len(border_points_grid[x][y + 1])):
                            r = border_points_grid[x][y + 1][i]
                            if r is False:
                                continue
                            if (
                                    abs(p.x - r.x) <= BORDER_POINTS_MERGE_THRESHOLD and
                                    abs(p.y - r.y) <= BORDER_POINTS_MERGE_THRESHOLD):
                                p.x = round((p.x + r.x) / 2)
                                p.y = round((p.y + r.y) / 2)
                                border_points_grid[x][y + 1][i] = False

                    # bottom-left
                    if y < grid_maxx and x > 0:
                        for i in range(0, len(border_points_grid[x - 1][y + 1])):
                            r = border_points_grid[x - 1][y + 1][i]
                            if r is False:
                                continue
                            if (
                                    abs(p.x - r.x) <= BORDER_POINTS_MERGE_THRESHOLD and
                                    abs(p.y - r.y) <= BORDER_POINTS_MERGE_THRESHOLD):
                                p.x = round((p.x + r.x) / 2)
                                p.y = round((p.y + r.y) / 2)
                                border_points_grid[x - 1][y + 1][i] = False

                    border_points_grid[x][y][j] = p
    return border_points_grid


def segments_from_border_points(border_points_grid: list) -> list:
    segments_list = []
    grid_maxx = len(border_points_grid) - 1
    grid_maxy = len(border_points_grid[0]) - 1
    for x in range(0, grid_maxx):
        for y in range(0, grid_maxy):
            grid_maxj = len(border_points_grid[x][y])
            for j in range(0, grid_maxj):
                p = border_points_grid[x][y][j]
                if p is not False:
                    closest_points = []

                    # current cell
                    for i in range(0, grid_maxj):
                        r = border_points_grid[x][y][i]
                        if r is False:
                            continue
                        if p.direction != r.direction:
                            closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y)])

                    # right
                    if x < grid_maxx:
                        for i in range(0, len(border_points_grid[x + 1][y])):
                            r = border_points_grid[x + 1][y][i]
                            if r is False:
                                continue
                            closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y)])

                    # bottom-right
                    if y < grid_maxy and x < grid_maxx:
                        for i in range(0, len(border_points_grid[x + 1][y + 1])):
                            r = border_points_grid[x + 1][y + 1][i]
                            if r is False:
                                continue
                            closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y)])

                    # bottom
                    if y < grid_maxx:
                        for i in range(0, len(border_points_grid[x][y + 1])):
                            r = border_points_grid[x][y + 1][i]
                            if r is False:
                                continue
                            closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y)])

                    # bottom-left
                    if y < grid_maxx and x > 0:
                        for i in range(0, len(border_points_grid[x - 1][y + 1])):
                            r = border_points_grid[x - 1][y + 1][i]
                            if r is False:
                                continue
                            closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y)])

                    if len(closest_points) > 0:
                        dist1 = 0
                        dist2 = 0
                        for i in closest_points:
                            dist1 = i[1] if i[1] < dist1 or dist1 == 0 else dist1
                            dist2 = i[1] if (i[1] < dist1 < dist2) or dist2 == 0 else dist2
                        if dist1 > 2 * GRID_STEP * GRID_STEP:
                            dist1 = 0
                        if dist2 > 2 * GRID_STEP * GRID_STEP:
                            dist2 = 0
                        for i in closest_points:
                            if i[1] == dist1 or i[1] == dist2:
                                segment = WG5Segment()
                                segment.start_x = p.x
                                segment.start_y = p.y
                                segment.end_x = i[0].x
                                segment.end_y = i[0].y
                                segments_list.append(segment)
    return segments_list
