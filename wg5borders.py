#!/bin/python3

GRID_STEP = 8  # the size of the grid cell, in pixels
BORDER_THRESHOLD = 25  # the threshold of the difference in lightness enough to be a border
BORDER_POINTS_MERGE_THRESHOLD = 4  # max distance between border points to merge the into one, in pixels
LINE_JOIN_THRESHOLD = 10  # max distance between corner points in the different lines to be treated as one line

BORDER_TYPE_VERTICAL = 1
BORDER_TYPE_DIAGONAL_BLTR = 2
BORDER_TYPE_HORIZONTAL = 3
BORDER_TYPE_DIAGONAL_TLBR = 4

TAN_INFINITY = 10001.0
TAN_THRESHOLD = 0.2  # threshold of the tan(angle) to merge the segments

global_segments_counter = 0
global_line_segments_counter = 0
global_line_counter = 0


class WG5GridNode:
    x = 0  # pixel x
    y = 0  # pixel y
    gradient_r = 0  # right
    gradient_br = 0  # bottom-right
    gradient_b = 0  # bottom
    gradient_bl = 0  # bottom-left
    pixel = []

    def __repr__(self):
        return 'WG5GridNode (' + str(self.x) + ', ' + str(self.y) + ')'\
            + ' r:' + str(self.gradient_r)\
            + ' br:' + str(self.gradient_br)\
            + ' b:' + str(self.gradient_b)\
            + ' bl:' + str(self.gradient_bl)


class WG5BorderPoint:
    x = 0  # pixel x
    y = 0  # pixel y
    direction = 0
    weight = 1  # how many original points contains this one after reducing

    def __repr__(self):
        return 'WG5BorderPoint (' + str(self.x) + ', ' + str(self.y) + ')'\
            + ' dir:' + str(self.direction) + ' w:' + str(self.weight)


class Grid:
    cell_size = GRID_STEP  # cell width/length in pixels
    iter_col = 0  # internal iterator index

    def __init__(self, cell_size=GRID_STEP):
        self.cell_size = GRID_STEP
        self.data = []

    def __iter__(self):
        self.iter_col = 0
        return self

    def __next__(self):
        self.iter_col += 1
        if self.iter_col > len(self.data):
            raise StopIteration
        return self.data[self.iter_col - 1]

    def __getitem__(self, item):
        return self.data[item]

    def repr_str_recursive(self, item, depth, counter) -> str:
        result = ''
        for i in range(0, 2 * depth):
            result += ' '
        result += str(counter) + ': '
        if hasattr(item, '__iter__'):
            counter = 0
            if len(item):
                result += "[\n"
                depth += 1
                for subitem in item:
                    result += self.repr_str_recursive(subitem, depth, counter)
                    counter += 1
                depth -= 1
                for i in range(0, 2 * depth):
                    result += ' '
                result += "]\n"
                return result
            else:
                result += "[]\n"
                return result
        else:
            return result + str(item) + "\n"

    def __repr__(self):
        result = "[\n"
        counter = 0
        for item in self.data:
            result += self.repr_str_recursive(item, 1, counter)
            counter += 1
        result += "]\n"
        return result

    def start_new_column(self):
        self.data.append([])

    def append_cell(self, cell):
        data_cols_len = len(self.data)
        if data_cols_len < 1:
            self.start_new_column()
            data_cols_len = 1
        self.data[data_cols_len - 1].append(cell)

    def append_to_cell(self, x, y, value) -> bool:
        if 0 <= x < len(self.data):
            if 0 <= y < len(self.data[x]):
                self.data[x][y].append(value)
        # some index is out of range
        return False

    def len_x(self) -> int:
        return len(self.data)

    def len_y(self) -> int:
        return len(self.data[0]) if self.len_x() > 0 else 0

    def init_empty_3dim(self, size_x, size_y):  # init empty 3-dimensional array size_x * size_y * 1
        self.data = []
        for x in range(0, size_x):
            col = []
            for y in range(0, size_y):
                col.append([])
            self.data.append(col)


class WG5Segment:
    start_x = 0  # pixel x
    start_y = 0  # pixel y
    end_x = 0  # pixel x
    end_y = 0  # pixel y
    end_cell_x = 0  # cell x
    end_cell_y = 0  # cell y
    id = 0

    def __init__(self, id=-1):
        if id == -1:
            global global_segments_counter
            id = global_segments_counter
            global_segments_counter += 1
        self.id = id

    def __eq__(self, other):
        if self.id != 0 and self.id == other.id:
            return True
        if (
                self.start_x == other.start_x and
                self.start_y == other.start_y and
                self.end_x == other.end_x and
                self.end_y == other.end_y):
            return True
        if (
                self.start_x == other.end_x and
                self.start_y == other.end_y and
                self.end_x == other.start_x and
                self.end_y == other.start_y):
            return True
        return False

    def __repr__(self):
        return 'WG5Segment (' + str(self.start_x) + ', ' + str(self.start_y) + ') -> '\
            + '(' + str(self.end_x) + ', ' + str(self.end_y) + '), '\
            + '[' + str(self.end_cell_x) + ', ' + str(self.end_cell_y) + ']'


class WG5LineSegment(WG5Segment):
    def __init__(self, id=-1):
        if id == -1:
            global global_line_segments_counter
            id = global_line_segments_counter
            global_line_segments_counter += 1
        self.id = id

    def init_from_segment(self, segment: WG5Segment):
        self.start_x = segment.start_x
        self.start_y = segment.start_y
        self.end_x = segment.end_x
        self.end_y = segment.end_y
        self.end_cell_x = segment.end_cell_x
        self.end_cell_y = segment.end_cell_y


class WG5Line:
    def __init__(self, id=-1):
        self.segments = []
        if id == -1:
            global global_line_counter
            id = global_line_counter
            global_line_counter += 1
        self.id = id

    def attach_segment(self, segment: WG5LineSegment) -> bool:
        add_segment_to_line = len(self.segments) == 0
        for s in self.segments:
            if s == segment:
                return False
            if (
                    (s.start_x == segment.start_x and s.start_y == segment.start_y) or
                    (s.end_x == segment.end_x and s.end_y == segment.end_y) or
                    (s.start_x == segment.end_x and s.start_y == segment.end_y) or
                    (s.end_x == segment.start_x and s.end_y == segment.start_y) or True
            ):
                add_segment_to_line = True
        if add_segment_to_line is False:
            return False
        self.segments.append(segment)
        return True


def grayscale_from_rgb(pixel) -> float:
    return (pixel[0] + pixel[1] + pixel[2]) / 3


def grid(pixelmap) -> Grid:
    result = Grid()
    for x in range(0, len(pixelmap)):
        if x % GRID_STEP == 0:
            y = 0
            result.start_new_column()
            for pixel in pixelmap[x]:
                if y % GRID_STEP == 0:
                    grid_node = WG5GridNode()
                    grid_node.x = x
                    grid_node.y = y
                    grid_node.pixel = grayscale_from_rgb(pixel)
                    result.append_cell(grid_node)
                y += 1
        x += 1
    return result


def grid_gradients(grid: Grid) -> Grid:
    grid_maxx = grid.len_x() - 1
    grid_maxy = grid.len_y() - 1
    for x in range(0, grid_maxx + 1):
        for y in range(0, grid_maxy + 1):
            if y < grid_maxy:
                grid[x][y].gradient_b = grid[x][y].pixel - grid[x][y + 1].pixel
                if x < grid_maxx:
                    grid[x][y].gradient_br = grid[x][y].pixel - grid[x + 1][y + 1].pixel
                    grid[x][y].gradient_bl = grid[x + 1][y].pixel - grid[x][y + 1].pixel
            if x < grid_maxx:
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


def border_points_from_grid(pixelmap: list, grid: Grid) -> Grid:
    result = Grid()
    x = 0
    pixelmap_maxx = len(pixelmap) - 1
    pixelmap_maxy = len(pixelmap[pixelmap_maxx]) - 1
    for col in grid:
        result.start_new_column()
        y = 0
        for node in col:
            result_cell = []

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
                result_cell.append(border_point)

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
                result_cell.append(border_point)

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
                result_cell.append(border_point)

            # bottom-left
            if abs(node.gradient_bl) > BORDER_THRESHOLD:
                border_point = WG5BorderPoint()
                border_point.direction = BORDER_TYPE_DIAGONAL_TLBR
                gradient_set = []
                for i in range(0, GRID_STEP + 1):
                    if node.x + GRID_STEP - i < 0:
                        break
                    if node.y + GRID_STEP + i > pixelmap_maxy:
                        break
                    gradient_set.append(grayscale_from_rgb(pixelmap[node.x + GRID_STEP - i][node.y + i]))
                i = get_gradient_middle(gradient_set)
                border_point.x = node.x + GRID_STEP - i
                border_point.y = node.y + i
                result_cell.append(border_point)

            result.append_cell(result_cell)
            y += 1
        x += 1
    return result


def remap_grid_after_reduce_border_points(border_points_grid: Grid) -> Grid:
    result = Grid(border_points_grid.cell_size)
    grid_maxx = border_points_grid.len_x()
    grid_maxy = border_points_grid.len_y()
    result.init_empty_3dim(grid_maxx, grid_maxy)
    grid_maxx -= 1
    grid_maxy -= 1
    for x in range(0, grid_maxx):
        for y in range(0, grid_maxy):
            for j in border_points_grid[x][y]:
                if j is not False:
                    result.append_to_cell(int(j.x // result.cell_size), int(j.y // result.cell_size), j)
    return result


def reduce_border_points(border_points_grid: Grid) -> Grid:
    global BORDER_POINTS_MERGE_THRESHOLD
    grid_maxx = border_points_grid.len_x() - 1
    grid_maxy = border_points_grid.len_y() - 1
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
                            p.x -= round((p.x - r.x) / (p.weight + r.weight))
                            p.y -= round((p.y - r.y) / (p.weight + r.weight))
                            p.weight += r.weight
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
                                p.x -= round((p.x - r.x) / (p.weight + r.weight))
                                p.y -= round((p.y - r.y) / (p.weight + r.weight))
                                p.weight += r.weight
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
                                p.x -= round((p.x - r.x) / (p.weight + r.weight))
                                p.y -= round((p.y - r.y) / (p.weight + r.weight))
                                p.weight += r.weight
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
                                p.x -= round((p.x - r.x) / (p.weight + r.weight))
                                p.y -= round((p.y - r.y) / (p.weight + r.weight))
                                p.weight += r.weight
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
                                p.x -= round((p.x - r.x) / (p.weight + r.weight))
                                p.y -= round((p.y - r.y) / (p.weight + r.weight))
                                p.weight += r.weight
                                border_points_grid[x - 1][y + 1][i] = False

                    border_points_grid[x][y][j] = p
    return remap_grid_after_reduce_border_points(border_points_grid)


def segments_from_border_points(border_points_grid: Grid) -> Grid:
    result = Grid()
    grid_maxx = border_points_grid.len_x()
    grid_maxy = border_points_grid.len_y()
    for x in range(0, grid_maxx):
        result.start_new_column()
        for y in range(0, grid_maxy):
            result_cell = []
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
                        if p.direction != r.direction and (p.x != r.x or p.y != r.y):
                            closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y), x, y])

                    # right
                    if x < grid_maxx:
                        for i in range(0, len(border_points_grid[x + 1][y])):
                            r = border_points_grid[x + 1][y][i]
                            if r is False:
                                continue
                            if p.x != r.x or p.y != r.y:
                                closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y), x + 1, y])

                    # bottom-right
                    if y < grid_maxy and x < grid_maxx:
                        for i in range(0, len(border_points_grid[x + 1][y + 1])):
                            r = border_points_grid[x + 1][y + 1][i]
                            if r is False:
                                continue
                            if p.x != r.x or p.y != r.y:
                                closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y), x + 1, y + 1])

                    # bottom
                    if y < grid_maxx:
                        for i in range(0, len(border_points_grid[x][y + 1])):
                            r = border_points_grid[x][y + 1][i]
                            if r is False:
                                continue
                            if p.x != r.x or p.y != r.y:
                                closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y), x, y + 1])

                    # bottom-left
                    if y < grid_maxx and x > 0:
                        for i in range(0, len(border_points_grid[x - 1][y + 1])):
                            r = border_points_grid[x - 1][y + 1][i]
                            if r is False:
                                continue
                            if p.x != r.x or p.y != r.y:
                                closest_points.append([r, (p.x - r.x) * (p.x - r.x) + (p.y - r.y) * (p.y - r.y), x - 1, y + 1])

                    if len(closest_points) > 0:
                        dist1 = 0
                        dist2 = 2 * GRID_STEP * GRID_STEP + 1
                        for i in closest_points:
                            if i[1] == 0:
                                continue
                            dist1 = i[1] if i[1] < dist1 or dist1 == 0 else dist1
                        for i in closest_points:
                            dist2 = i[1] if dist1 < i[1] < dist2 else dist2
                        if dist1 > 2.5 * GRID_STEP * GRID_STEP:
                            dist1 = 0
                        if dist2 > 2.5 * GRID_STEP * GRID_STEP:
                            dist2 = 0
                        for i in closest_points:
                            if i[1] == 0:
                                continue
                            if i[1] == dist1 or i[1] == dist2:
                                segment = WG5Segment()
                                segment.start_x = p.x
                                segment.start_y = p.y
                                segment.end_x = i[0].x
                                segment.end_y = i[0].y
                                segment.end_cell_x = i[2]
                                segment.end_cell_y = i[3]
                                result_cell.append(segment)

            result.append_cell(result_cell)
    return result


# todo here are the gaps formed
def reduce_linear_segments_recursive(current_segment: WG5Segment, segments_grid: Grid) -> list:
    cell_x = current_segment.end_cell_x
    cell_y = current_segment.end_cell_y
    if current_segment.start_y == current_segment.end_y:
        cur_tg = TAN_INFINITY
    else:
        cur_tg = (current_segment.start_x - current_segment.end_x) / (current_segment.start_y - current_segment.end_y)
    if current_segment.start_x == current_segment.end_x:
        cur_ctg = TAN_INFINITY
    else:
        cur_ctg = (current_segment.start_y - current_segment.end_y) / (current_segment.start_x - current_segment.end_x)
    for z in range(0, len(segments_grid[cell_x][cell_y])):
        reduce_segment = False
        if segments_grid[cell_x][cell_y][z] is not False:
            r = segments_grid[cell_x][cell_y][z]
            if (
                    current_segment.start_x == r.start_x and
                    current_segment.start_y == r.start_y and
                    current_segment.end_x == r.end_x and
                    current_segment.end_y == r.end_y):
                continue
            if r.start_y == r.end_y:
                r_tg = TAN_INFINITY
            else:
                r_tg = (r.start_x - r.end_x) / (r.start_y - r.end_y)
            if r.start_x == r.end_x:
                r_ctg = TAN_INFINITY
            else:
                r_ctg = (r.start_y - r.end_y) / (r.start_x - r.end_x)
            if (cur_tg == -r_tg and cur_tg != 0) or (cur_ctg == -r_ctg and cur_ctg != 0):
                continue
            if -1 <= cur_tg <= 1:  # +45 deg ... -45 deg or 135 deg ... -135 deg
                if cur_tg == r_tg or abs((cur_tg - r_tg) / (cur_tg + r_tg)) < TAN_THRESHOLD:
                    reduce_segment = True
            elif -1 <= cur_ctg <= 1:  # -45 deg ... -135 deg or 45 deg ... 135 deg
                if cur_ctg == r_ctg or abs((cur_ctg - r_ctg) / (cur_ctg + r_ctg)) < TAN_THRESHOLD:
                    reduce_segment = True
        if reduce_segment is True:
            if current_segment != segments_grid[cell_x][cell_y][z]:
                current_segment.end_x = segments_grid[cell_x][cell_y][z].end_x
                current_segment.end_y = segments_grid[cell_x][cell_y][z].end_y
                current_segment.end_cell_x = segments_grid[cell_x][cell_y][z].end_cell_x
                current_segment.end_cell_y = segments_grid[cell_x][cell_y][z].end_cell_y
                segments_grid[cell_x][cell_y][z] = False
                current_segment, segments_list = reduce_linear_segments_recursive(current_segment, segments_grid)
    return [current_segment, segments_grid]


def reduce_linear_segments(segments_grid: Grid) -> Grid:
    for x in range(0, segments_grid.len_x()):
        for y in range(0, segments_grid.len_y()):
            for s in segments_grid[x][y]:
                if s is not False:
                    s, segments_grid = reduce_linear_segments_recursive(s, segments_grid)
    return segments_grid


def attach_segment_to_line_recursive(segments_grid: Grid, line: WG5Line, current_segment: WG5Segment) -> Grid:
    segment = WG5LineSegment()
    segment.init_from_segment(current_segment)
    if line.attach_segment(segment) is False:
        return segments_grid
    grid_maxs = len(segments_grid[segment.end_cell_x][segment.end_cell_y])
    for s in range(0, grid_maxs):
        if segments_grid[segment.end_cell_x][segment.end_cell_y][s] is not False:
            attach_segment_to_line_recursive(
                segments_grid,
                line,
                segments_grid[segment.end_cell_x][segment.end_cell_y][s]
            )
            segments_grid[segment.end_cell_x][segment.end_cell_y][s] = False
    return segments_grid


def lines_from_segments(segments_grid: Grid) -> Grid:
    result = Grid()
    grid_maxx = segments_grid.len_x()
    grid_maxy = segments_grid.len_y()
    for x in range(0, grid_maxx):
        result.start_new_column()
        for y in range(0, grid_maxy):
            result_cell = []
            grid_maxs = len(segments_grid[x][y])
            for s in range(0, grid_maxs):
                if segments_grid[x][y][s] is not False:
                    line = WG5Line()
                    segments_grid = attach_segment_to_line_recursive(segments_grid, line, segments_grid[x][y][s])
                    segments_grid[x][y][s] = False
                    result_cell.append(line)
            result.append_cell(result_cell)
    return result


def check_and_attach_line_to_line(line1: WG5Line, line2: WG5Line) -> bool:
    global LINE_JOIN_THRESHOLD
    if line1.id == line2.id:
        return False
    flag_join = False
    for i in line1.segments:
        for j in line2.segments:
            segment = False
            if abs(i.start_x - j.start_x) < LINE_JOIN_THRESHOLD and abs(i.start_y - j.start_y) < LINE_JOIN_THRESHOLD:
                segment = WG5LineSegment()
                segment.start_x = i.start_x
                segment.start_y = i.start_y
                segment.end_x = j.start_x
                segment.end_y = j.start_y
                segment.end_cell_x = 0
                segment.end_cell_y = 0
                flag_join = True
            if abs(i.start_x - j.end_x) < LINE_JOIN_THRESHOLD and abs(i.start_y - j.end_y) < LINE_JOIN_THRESHOLD:
                segment = WG5LineSegment()
                segment.start_x = i.start_x
                segment.start_y = i.start_y
                segment.end_x = j.end_x
                segment.end_y = j.end_y
                segment.end_cell_x = 0
                segment.end_cell_y = 0
                flag_join = True
            if abs(i.end_x - j.start_x) < LINE_JOIN_THRESHOLD and abs(i.end_y - j.start_y) < LINE_JOIN_THRESHOLD:
                segment = WG5LineSegment()
                segment.start_x = i.end_x
                segment.start_y = i.end_y
                segment.end_x = j.start_x
                segment.end_y = j.start_y
                segment.end_cell_x = 0
                segment.end_cell_y = 0
                flag_join = True
            if abs(i.end_x - j.end_x) < LINE_JOIN_THRESHOLD and abs(i.end_y - j.end_y) < LINE_JOIN_THRESHOLD:
                segment = WG5LineSegment()
                segment.start_x = i.end_x
                segment.start_y = i.end_y
                segment.end_x = j.end_x
                segment.end_y = j.end_y
                segment.end_cell_x = 0
                segment.end_cell_y = 0
                flag_join = True
            if flag_join:
                if segment:
                    line1.attach_segment(segment)
                for s in line2.segments:
                    line1.attach_segment(s)
                return True
    return False


def join_lines(lines_grid: Grid) -> Grid:
    grid_maxx = lines_grid.len_x()
    grid_maxy = lines_grid.len_y()
    for x1 in range(0, grid_maxx):
        for y1 in range(0, grid_maxy):
            for s1 in range(0, len(lines_grid[x1][y1])):
                if lines_grid[x1][y1][s1] is not False:
                    for x2 in range(0, grid_maxx):
                        for y2 in range(0, grid_maxy):
                            for s2 in range(0, len(lines_grid[x2][y2])):
                                if lines_grid[x2][y2][s2] is not False:
                                    if check_and_attach_line_to_line(lines_grid[x1][y1][s1], lines_grid[x2][y2][s2]):
                                        lines_grid[x2][y2][s2] = False

    return lines_grid