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

TAN_INFINITY = 1000.0


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
    #angle = 0  # angle of the border, tan
    #segment_ids = []


class WG5Segment:
    start_x = 0  # pixel x
    start_y = 0  # pixel y
    end_x = 0  # pixel x
    end_y = 0  # pixel y
    #direction = 0
    #angle = 0  # angle of the segment, tan
    #end_cell_x = 0  # grid cell index
    #end_cell_y = 0  # grid cell index
    #start_segment_ids = []
    #end_segment_ids = []


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


# def angle_from_two_points(x1: int, y1: int, x2: int, y2: int) -> float:
#     if y1 == y2:
#         return TAN_INFINITY
#     return (x1 - x2) / (y1 - y2)


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
            # border_point_r = False
            # border_point_br = False
            # border_point_b = False
            # border_point_bl = False

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
                #border_point_r.angle = TAN_INFINITY
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
                # if border_point_r is not False:
                #     border_point_br.angle = angle_from_two_points(border_point_r.x, border_point_r.y, border_point_br.x, border_point_br.y)
                #     border_point_r.angle = border_point_br.angle
                # else:
                #     border_point_br.angle = -1
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
                # if border_point_br is not False:
                #     border_point_b.angle = angle_from_two_points(border_point_br.x, border_point_br.y, border_point_b.x, border_point_b.y)
                #     border_point_br.angle = border_point_b.angle
                # elif border_point_r is not False:
                #     border_point_b.angle = angle_from_two_points(border_point_r.x, border_point_r.y, border_point_b.x, border_point_b.y)
                #     border_point_r.angle = border_point_b.angle
                # else:
                #     border_point_b.angle = 0
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
                # if border_point_b is not False:
                #     border_point_bl.angle = angle_from_two_points(border_point_b.x, border_point_b.y, border_point_bl.x, border_point_bl.y)
                #     border_point_b.angle = border_point_bl.angle
                # elif border_point_br is not False:
                #     border_point_bl.angle = angle_from_two_points(border_point_br.x, border_point_br.y, border_point_bl.x, border_point_bl.y)
                #     border_point_br.angle = border_point_bl.angle
                # elif border_point_r is not False:
                #     border_point_bl.angle = angle_from_two_points(border_point_r.x, border_point_r.y, border_point_bl.x, border_point_bl.y)
                #     border_point_r.angle = border_point_bl.angle
                # else:
                #     border_point_bl.angle = 1
                border_points_cell.append(border_point)

            # if border_point_r is not False:
            #     border_points_cell.append(border_point_r)
            # if border_point_br is not False:
            #     border_points_cell.append(border_point_br)
            # if border_point_b is not False:
            #     border_points_cell.append(border_point_b)
            # if border_point_bl is not False:
            #     border_points_cell.append(border_point_bl)
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
                            #p.angle = (p.angle + r.angle) / 2
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
                                #p.angle = (p.angle + r.angle) / 2
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
                                #p.angle = (p.angle + r.angle) / 2
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
                                #p.angle = (p.angle + r.angle) / 2
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
                                #p.angle = (p.angle + r.angle) / 2
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
                                # start_segment_ids
                                # end_segment_ids
                                segment.start_x = p.x
                                segment.start_y = p.y
                                segment.end_x = i[0].x
                                segment.end_y = i[0].y
                                segments_list.append(segment)
    return segments_list

# def segments_from_border_points_1(border_points_grid: list) -> list:
#     segments_list = []
#     grid_maxx = len(border_points_grid) - 1
#     grid_maxy = len(border_points_grid[0]) - 1
#     for x in range(0, grid_maxx):
#         for y in range(0, grid_maxy):
#             grid_maxj = len(border_points_grid[x][y])
#             for j in range(0, grid_maxj):
#                 p = border_points_grid[x][y][j]
#                 if p is not False:
#
#                     # current cell
#                     for i in range(0, grid_maxj):
#                         r = border_points_grid[x][y][i]
#                         if r is False:
#                             continue
#                         if p.direction != r.direction:
#                             segment = WG5Segment()
#                             segment.start_x = p.x
#                             segment.start_y = p.y
#                             segment.end_x = r.x
#                             segment.end_y = r.y
#                             segments_list.append(segment)
#                             segment_id = len(segments_list) - 1
#                             if len(p.segment_ids) > 0:
#                                 for p_s_id in p.segment_ids:
#                                     if p_s_id != segment_id:
#                                         segments_list[segment_id].start_segment_ids.append(p_s_id)
#                                         segments_list[p_s_id].end_segment_ids.append(segment_id)
#                                         border_points_grid[x][y][j].segment_ids.append(segment_id)
#                             if len(r.segment_ids) > 0:
#                                 for r_s_id in p.segment_ids:
#                                     if r_s_id != segment_id:
#                                         segments_list[segment_id].end_segment_ids.append(r_s_id)
#                                         segments_list[r_s_id].start_segment_ids.append(segment_id)
#                                         border_points_grid[x][y][i].segment_ids.append(segment_id)
#
#                     # right
#                     if x < grid_maxx:
#                         for i in range(0, len(border_points_grid[x + 1][y])):
#                             r = border_points_grid[x + 1][y][i]
#                             if r is False:
#                                 continue
#                             segment = WG5Segment()
#                             segment.start_x = p.x
#                             segment.start_y = p.y
#                             segment.end_x = r.x
#                             segment.end_y = r.y
#                             segments_list.append(segment)
#                             segment_id = len(segments_list) - 1
#                             if len(p.segment_ids) > 0:
#                                 for p_s_id in p.segment_ids:
#                                     if p_s_id != segment_id:
#                                         segments_list[segment_id].start_segment_ids.append(p_s_id)
#                                         segments_list[p_s_id].end_segment_ids.append(segment_id)
#                                         border_points_grid[x + 1][y][j].segment_ids.append(segment_id)
#                             if len(r.segment_ids) > 0:
#                                 for r_s_id in p.segment_ids:
#                                     if r_s_id != segment_id:
#                                         segments_list[segment_id].end_segment_ids.append(r_s_id)
#                                         segments_list[r_s_id].start_segment_ids.append(segment_id)
#                                         border_points_grid[x + 1][y][i].segment_ids.append(segment_id)
#
#                     # bottom-right
#                     if y < grid_maxy and x < grid_maxx:
#                         for i in range(0, len(border_points_grid[x + 1][y + 1])):
#                             r = border_points_grid[x + 1][y + 1][i]
#                             if r is False:
#                                 continue
#                             segment = WG5Segment()
#                             segment.start_x = p.x
#                             segment.start_y = p.y
#                             segment.end_x = r.x
#                             segment.end_y = r.y
#                             segments_list.append(segment)
#                             segment_id = len(segments_list) - 1
#                             if len(p.segment_ids) > 0:
#                                 for p_s_id in p.segment_ids:
#                                     if p_s_id != segment_id:
#                                         segments_list[segment_id].start_segment_ids.append(p_s_id)
#                                         segments_list[p_s_id].end_segment_ids.append(segment_id)
#                                         border_points_grid[x + 1][y + 1][j].segment_ids.append(segment_id)
#                             if len(r.segment_ids) > 0:
#                                 for r_s_id in p.segment_ids:
#                                     if r_s_id != segment_id:
#                                         segments_list[segment_id].end_segment_ids.append(r_s_id)
#                                         segments_list[r_s_id].start_segment_ids.append(segment_id)
#                                         border_points_grid[x + 1][y + 1][i].segment_ids.append(segment_id)
#
#                     # bottom
#                     if y < grid_maxx:
#                         for i in range(0, len(border_points_grid[x][y + 1])):
#                             r = border_points_grid[x][y + 1][i]
#                             if r is False:
#                                 continue
#                             segment = WG5Segment()
#                             segment.start_x = p.x
#                             segment.start_y = p.y
#                             segment.end_x = r.x
#                             segment.end_y = r.y
#                             segments_list.append(segment)
#                             segment_id = len(segments_list) - 1
#                             if len(p.segment_ids) > 0:
#                                 for p_s_id in p.segment_ids:
#                                     if p_s_id != segment_id:
#                                         segments_list[segment_id].start_segment_ids.append(p_s_id)
#                                         segments_list[p_s_id].end_segment_ids.append(segment_id)
#                                         border_points_grid[x][y + 1][j].segment_ids.append(segment_id)
#                             if len(r.segment_ids) > 0:
#                                 for r_s_id in p.segment_ids:
#                                     if r_s_id != segment_id:
#                                         segments_list[segment_id].end_segment_ids.append(r_s_id)
#                                         segments_list[r_s_id].start_segment_ids.append(segment_id)
#                                         border_points_grid[x][y + 1][i].segment_ids.append(segment_id)
#
#                     # bottom-left
#                     if y < grid_maxx and x > 0:
#                         for i in range(0, len(border_points_grid[x - 1][y + 1])):
#                             r = border_points_grid[x - 1][y + 1][i]
#                             if r is False:
#                                 continue
#                             segment = WG5Segment()
#                             segment.start_x = p.x
#                             segment.start_y = p.y
#                             segment.end_x = r.x
#                             segment.end_y = r.y
#                             segments_list.append(segment)
#                             segment_id = len(segments_list) - 1
#                             if len(p.segment_ids) > 0:
#                                 for p_s_id in p.segment_ids:
#                                     if p_s_id != segment_id:
#                                         segments_list[segment_id].start_segment_ids.append(p_s_id)
#                                         segments_list[p_s_id].end_segment_ids.append(segment_id)
#                                         border_points_grid[x - 1][y + 1][j].segment_ids.append(segment_id)
#                             if len(r.segment_ids) > 0:
#                                 for r_s_id in p.segment_ids:
#                                     if r_s_id != segment_id:
#                                         segments_list[segment_id].end_segment_ids.append(r_s_id)
#                                         segments_list[r_s_id].start_segment_ids.append(segment_id)
#                                         border_points_grid[x - 1][y + 1][i].segment_ids.append(segment_id)
#
#         # segments_grid_col = []
#         # for y in range(0, bp_grid_maxy):
#         #     segments_grid_cell = []
#         #     if len(border_points_grid[x][y]) > 1:
#         #         bp_cell_len = len(border_points_grid[x][y])
#         #         for i in range(0, bp_cell_len - 1):
#         #             if border_points_grid[x][y][i] is False or border_points_grid[x][y][i + 1] is False:
#         #                 continue
#         #             segment = WG5Segment()
#         #             segment.start_x = border_points_grid[x][y][i].x
#         #             segment.start_y = border_points_grid[x][y][i].y
#         #             segment.end_x = border_points_grid[x][y][i + 1].x
#         #             segment.end_y = border_points_grid[x][y][i + 1].y
#         #             segment.end_cell_y = x
#         #             segment.end_cell_y = y
#         #             # direction ?
#         #             # angle ?
#         #             segments_grid_cell.append(segment)
#         #
#         #     for c in border_points_grid[x][y]:
#         #         if c is False:
#         #             continue
#         #
#         #         # right
#         #         if c.direction != BORDER_TYPE_VERTICAL:
#         #             for r in border_points_grid[x + 1][y]:
#         #                 if r is False:
#         #                     continue
#         #                 if r.direction == c.direction:
#         #                     segment = WG5Segment()
#         #                     segment.start_x = c.x
#         #                     segment.start_y = c.y
#         #                     segment.end_x = r.x
#         #                     segment.end_y = r.y
#         #                     #segment.direction = SEGMENT_TYPE_HORIZONTAL
#         #                     # angle ?
#         #                     segment.end_cell_x = x + 1
#         #                     segment.end_cell_y = y
#         #                     segments_grid_cell.append(segment)
#         #
#         #         # bottom-right
#         #         if c.direction != BORDER_TYPE_DIAGONAL_BLTR:
#         #             for r in border_points_grid[x + 1][y + 1]:
#         #                 if r is False:
#         #                     continue
#         #                 if r.direction == c.direction:
#         #                     segment = WG5Segment()
#         #                     segment.start_x = c.x
#         #                     segment.start_y = c.y
#         #                     segment.end_x = r.x
#         #                     segment.end_y = r.y
#         #                     #segment.direction = SEGMENT_TYPE_DIAGONAL_TLBR
#         #                     segment.end_cell_x = x + 1
#         #                     segment.end_cell_y = y + 1
#         #                     segments_grid_cell.append(segment)
#         #
#         #         # bottom
#         #         if c.direction != BORDER_TYPE_HORIZONTAL:
#         #             for r in border_points_grid[x][y + 1]:
#         #                 if r is False:
#         #                     continue
#         #                 if r.direction == c.direction:
#         #                     segment = WG5Segment()
#         #                     segment.start_x = c.x
#         #                     segment.start_y = c.y
#         #                     segment.end_x = r.x
#         #                     segment.end_y = r.y
#         #                     #segment.direction = SEGMENT_TYPE_VERTICAL
#         #                     # angle ?
#         #                     segment.end_cell_x = x
#         #                     segment.end_cell_y = y + 1
#         #                     segments_grid_cell.append(segment)
#         #
#         #         # bottom-left
#         #         if c.direction != BORDER_TYPE_DIAGONAL_TLBR and y > 0:
#         #             for r in border_points_grid[x + 1][y - 1]:
#         #                 if r is False:
#         #                     continue
#         #                 if r.direction == c.direction:
#         #                     segment = WG5Segment()
#         #                     segment.start_x = c.x
#         #                     segment.start_y = c.y
#         #                     segment.end_x = r.x
#         #                     segment.end_y = r.y
#         #                     #segment.direction = SEGMENT_TYPE_DIAGONAL_BLTR
#         #                     segment.end_cell_x = x + 1
#         #                     segment.end_cell_y = y - 1
#         #                     segments_grid_cell.append(segment)
#         #
#         #     segments_grid_col.append(segments_grid_cell)
#         # segments_grid.append(segments_grid_col)
#     return segments_list


# def remove_double_borders(segments_list: list) -> list:
#     maxx = len(segments_list) - 1
#     maxy = len(segments_list[0]) - 1
#     for x in range(0, maxx):
#         for y in range(0, maxy):
#             for z in segments_list[x][y]:
#                 if x < maxx and z is not False and z.direction == SEGMENT_TYPE_VERTICAL:
#                     for i in range(0, len(segments_list[x + 1][y])):
#                         if segments_list[x + 1][y][i] is not False and segments_list[x + 1][y][i].direction == z.direction:
#                             segments_list[x + 1][y][i] = False
#                             break
#                 if x < maxx and y < maxy and z is not False and z.direction == SEGMENT_TYPE_DIAGONAL_BLTR:
#                     for i in range(0, len(segments_list[x + 1][y + 1])):
#                         if segments_list[x + 1][y + 1][i] is not False and segments_list[x + 1][y + 1][i].direction == z.direction:
#                             segments_list[x + 1][y + 1][i] = False
#                             break
#                 if y < maxy and z is not False and z.direction == SEGMENT_TYPE_HORIZONTAL:
#                     for i in range(0, len(segments_list[x][y + 1])):
#                         if segments_list[x][y + 1][i] is not False and segments_list[x][y + 1][i].direction == z.direction:
#                             segments_list[x][y + 1][i] = False
#                             break
#                 if x > 0 and y < maxy and z is not False and z.direction == SEGMENT_TYPE_DIAGONAL_TLBR:
#                     for i in range(0, len(segments_list[x - 1][y + 1])):
#                         if segments_list[x - 1][y + 1][i] is not False and segments_list[x - 1][y + 1][i].direction == z.direction:
#                             segments_list[x - 1][y + 1][i] = False
#                             break
#     return segments_list


# def reduce_segments_recursive(current_segment: WG5Segment, segments_list: list) -> list:
#     cell_x = current_segment.end_cell_x
#     cell_y = current_segment.end_cell_y
#     for z in range(0, len(segments_list[cell_x][cell_y])):
#         if segments_list[cell_x][cell_y][z] is not False and (
#                 segments_list[cell_x][cell_y][z].direction == SEGMENT_TYPE_ANY or
#                 segments_list[cell_x][cell_y][z].direction == current_segment.direction):
#             current_segment.end_x = segments_list[cell_x][cell_y][z].end_x
#             current_segment.end_y = segments_list[cell_x][cell_y][z].end_y
#             current_segment.end_cell_x = segments_list[cell_x][cell_y][z].end_cell_x
#             current_segment.end_cell_y = segments_list[cell_x][cell_y][z].end_cell_y
#             segments_list[cell_x][cell_y][z] = False
#             current_segment, segments_list = reduce_segments_recursive(current_segment, segments_list)
#             break
#     return [current_segment, segments_list]


# def reduce_segments(segments_list: list) -> list:
#     for x in range(0, len(segments_list)):
#         for y in range(0, len(segments_list[0])):
#             for s in segments_list[x][y]:
#                 if s is not False:
#                     s, segments_list = reduce_segments_recursive(s, segments_list)
#     return segments_list


# def reduce_segments2(segments_list: list) -> list:
#     grid_maxx = len(segments_list) - 1
#     grid_maxy = len(segments_list[0]) - 1
#     result_grid = []
#     for x in range(1, grid_maxx + 3, 3):
#         result_row = []
#         for y in range(1, grid_maxy + 3, 3):
#             result_cell = []
#             op = {
#                 SEGMENT_TYPE_VERTICAL: [],
#                 SEGMENT_TYPE_DIAGONAL_BLTR: [],
#                 SEGMENT_TYPE_HORIZONTAL: [],
#                 SEGMENT_TYPE_DIAGONAL_TLBR: []
#             }
#             for x2 in range(-1, 1):
#                 if x + x2 <= grid_maxx:
#                     for y2 in range(-1, 1):
#                         if y + y2 <= grid_maxy:
#                             for p in segments_list[x + x2][y + y2]:
#                                 if p is not False:
#                                     op[p.direction].append(p)
#             for t in op:
#                 if len(op[t]) > 0:
#                     pass
#             result_row.append(result_cell)
#         result_grid.append(result_row)
#     return result_grid