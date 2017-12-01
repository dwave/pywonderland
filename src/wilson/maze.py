# -*- coding: utf-8 -*-

from encoder import GIFWriter


class Canvas(object):
    """
    A canvas is built on top of a maze to encode it into frames.
    The core part is the `encode_frame` method below.
    """

    def __init__(self, maze, scale, min_bits, palette, loop, filename):
        """
        maze: an instance of the maze class.
        scale: each cell in the maze occupies scale*scale pixels in the image.
        filename: the output file.
        """
        self.maze = maze
        self.scale = scale
        self.writer = GIFWriter(maze.width * scale, maze.height * scale, min_bits, palette, loop)
        self.colormap = {i: i for i in range(1 << min_bits)}
        self.speed = 10        # output the frame once this number of cells are changed.
        self.trans_index = 3   # the index of the transparent color in the global color table.
        self.delay = 5         # delay between successive frames.
        self.target_file = open(filename, 'wb')
        self.target_file.write(self.writer.logical_screen_descriptor
                               + self.writer.global_color_table
                               + self.writer.loop_control)

    def encode_frame(self, static=False):
        """
        Encode current maze into one frame.
        If static is True then the graphics control block is not added.
        """
        # get the bounding box of this frame.
        if self.maze.frame_box is not None:
            left, top, right, bottom = self.maze.frame_box
        else:
            left, top, right, bottom = 0, 0, self.maze.width - 1, self.maze.height - 1

        # then get the image descriptor of this frame.
        width = right - left + 1
        height = bottom - top + 1
        descriptor = GIFWriter.image_descriptor(left * self.scale, top * self.scale,
                                                width * self.scale, height * self.scale)

        # a generator that yields the pixels of this frame.
        def get_frame_pixels():
            for i in range(width * height * self.scale * self.scale):
                y = i // (width * self.scale * self.scale)
                x = (i % (width * self.scale)) // self.scale
                val = self.maze.grid[x + left][y + top]
                c = self.colormap[val]
                yield c

        # encode the frame data via the LZW compression.
        frame = self.writer.LZW_encode(get_frame_pixels())

        # reset `num_changes` and `frame_box`.
        self.maze.num_changes = 0
        self.maze.frame_box = None

        if static:
            return descriptor + frame
        else:
            control = GIFWriter.graphics_control_block(self.delay, self.trans_index)
            return control + descriptor + frame

    def paint_background(self, **kwargs):
        """
        Insert current frame at the beginning to use it as the background.
        This does not require the graphics control block.
        """
        if kwargs:
            self.set_colors(**kwargs)
        self.target_file.write(self.encode_frame(static=True))

    def refresh_frame(self):
        if self.maze.num_changes >= self.speed:
            self.target_file.write(self.encode_frame(static=False))

    def clear_remaining_changes(self):
        if self.maze.num_changes > 0:
            self.target_file.write(self.encode_frame(static=False))

    def set_colors(self, **kwargs):
        color_dict = {'wall_color': 0, 'tree_color': 1,
                      'path_color': 2, 'fill_color': 3}
        for key, val in kwargs.items():
            self.colormap[color_dict[key]] = val

    def pad_delay_frame(self, delay):
        self.target_file.write(self.writer.pad_delay_frame(delay, self.trans_index))
        
    def set_control_params(self, speed=30, delay=3, trans_index=5, **kwargs):
        self.speed = speed
        self.delay = delay
        self.trans_index = trans_index
        self.set_colors(**kwargs)

    def save(self):
        self.target_file.write(bytearray([0x3B]))
        self.target_file.close()

  

class Maze(object):
    """
    This class defines the basic structure of a maze and some operations on it.
    """
    WALL = 0
    TREE = 1
    PATH = 2
    FILL = 3

    def __init__(self, width, height, margin, mask=None):
        """
        width, height: size of the maze, must both be odd numbers.
        margin: size of the border of the maze.

        The maze is represented by a grid with `height` rows and `width` columns,
        each cell in the maze has 4 possible states:

        0: it's a wall
        1: it's in the tree
        2: it's in the path
        3: it's filled (this will not be used until the maze-searching animation)

        Initially all cells are walls. Adjacent cells in the maze are spaced out by one cell.

        mask: must be None or a white/black image instance of PIL's Image class.
              This mask image must preserve the connectivity of the graph,
              otherwise the program will not terminate.
        """
        self.width = width
        self.height = height
        self.grid = [[0]*height for _ in range(width)]
        self.num_changes = 0   # a counter holds how many cells are changed.
        self.frame_box = None  # maintains the region that to be updated.
        self.path = []         # hold the path in the loop erased random walk.
        
        def get_mask_pixel(cell):
            if mask is None:
                return True
            else:
                return mask.getpixel(cell) == 255

        self.cells = []
        for y in range(margin, height - margin, 2):
            for x in range(margin, width - margin, 2):
                if get_mask_pixel((x, y)):
                    self.cells.append((x, y))

        def neighborhood(cell):
            x, y = cell
            neighbors = []
            if x >= 2 + margin and get_mask_pixel((x-2, y)):
                neighbors.append((x-2, y))
            if y >= 2 + margin and get_mask_pixel((x, y-2)):
                neighbors.append((x, y-2))
            if x <= width - 3 - margin and get_mask_pixel((x+2, y)):
                neighbors.append((x+2, y))
            if y <= height - 3 - margin and get_mask_pixel((x, y+2)):
                neighbors.append((x, y+2))
            return neighbors

        self.graph = {v: neighborhood(v) for v in self.cells}

    def get_neighbors(self, cell):
        return self.graph[cell]

    def mark_cell(self, cell, index):
        """Mark a cell and update `frame_box` and `num_changes`."""
        x, y = cell
        self.grid[x][y] = index

        if self.frame_box is not None:
            left, top, right, bottom = self.frame_box
            self.frame_box = (min(x, left), min(y, top),
                              max(x, right), max(y, bottom))
        else:
            self.frame_box = (x, y, x, y)

        self.num_changes += 1

    def mark_wall(self, cell_a, cell_b, index):
        """Mark the space between two adjacent cells."""
        wall = ((cell_a[0] + cell_b[0]) // 2,
                (cell_a[1] + cell_b[1]) // 2)
        self.mark_cell(wall, index)

    def mark_path(self, path, index):
        """Mark the cells in a path and the spaces between them."""
        for cell in path:
            self.mark_cell(cell, index)
        for cell_a, cell_b in zip(path[1:], path[:-1]):
            self.mark_wall(cell_a, cell_b, index)

    def is_wall(self, cell):
        """Check if a cell is wall."""
        x, y = cell
        return self.grid[x][y] == Maze.WALL

    def connected(self, cell_a, cell_b):
        """Check if two adjacent cells are connected."""
        x = (cell_a[0] + cell_b[0]) // 2
        y = (cell_a[1] + cell_b[1]) // 2
        return self.grid[x][y] == Maze.WALL

    def in_tree(self, cell):
        """Check if a cell is in the tree."""
        x, y = cell
        return self.grid[x][y] == Maze.TREE

    def in_path(self, cell):
        """Check if a cell is in the path."""
        x, y = cell
        return self.grid[x][y] == Maze.PATH

    def add_canvas(self, *args, **kwargs):
        self.canvas = Canvas(self, *args, **kwargs)
        return self.canvas
