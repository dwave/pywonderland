# -*- coding: utf-8 -*-
"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Make GIF animations of Wilson's uniform spanning tree algorithm
and the breadth-first search algorithm.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Usage:
      python wilson.py [-width] [-height] [-scale]
                       [-margin] [-bits]
                       [-loop] [-filename]
Optional arguments:
    width, height: size of the maze (not the image), should both be odd integers.
    scale: the size of the image will be (width * scale) * (height * scale).
           In other words, each cell in the maze will occupy a square of
           (scale * scale) pixels in the image.
    margin: size of the border of the image.
    bits: number of bits needed to represent all colors.
          This value determines the number of colors used in the image.
    loop: number of loops of the image, default to 0 (loop infinitely).
    filename: the output file.

Reference for Wilson's algorithm:

    Probability on Trees and Networks, by Russell Lyons and Yuval Peres.

Reference for the GIF89a specification:

    http://giflib.sourceforge.net/whatsinagif/index.html

Copyright (c) 2016 by Zhao Liang.
"""
import argparse
import random
from colorsys import hls_to_rgb
from maze import Maze
from search_algorithms import bfs

try:
    from tqdm import tqdm
except ImportError:
    print('Module \'tqdm\' not found, process bar prohibited.')
    tqdm = list


class Wilson(Maze):

    def run_wilson_algorithm(self, root):
        """Animating Wilson's uniform spanning tree algorithm."""
        # initially the tree only contains the root.
        self.mark_cell(root, Maze.TREE)

        # for each cell that is not in the tree,
        # start a loop erased random walk from this cell until the walk hits the tree.
        for cell in tqdm(self.cells):
            if not self.in_tree(cell):
                self.loop_erased_random_walk(cell)

        # possibly there are some changes that have not been written to the file.
        self.canvas.clear_remaining_changes()

    def loop_erased_random_walk(self, cell):
        """
        Start a loop erased random walk from a given cell until it hits the tree.
        """
        self.path = [cell]
        self.mark_cell(cell, Maze.PATH)
        current_cell = cell

        while not self.in_tree(current_cell):
            current_cell = self.move_one_step(current_cell)
            self.canvas.refresh_frame()

        # once the walk meets the tree, add the path to the tree.
        self.mark_path(self.path, Maze.TREE)

    def move_one_step(self, cell):
        """
        The most fundamental step in Wilson's algorithm:
        1. choose a random neighbor z of current cell and move to z.
        2. (a) if z is already in current path then a loop is found, erase this loop
               and continue the walk from z.
           (b) if z is already in the tree then finish this walk.
           (c) if z is neither in the path nor in the tree then append it to the path
               and continue the walk from z.
        """
        next_cell = random.choice(self.get_neighbors(cell))
        if self.in_path(next_cell):
            self.erase_loop(next_cell)
        elif self.in_tree(next_cell):
            self.add_to_path(next_cell)
            # `add_to_path` will change the cell to `PATH` so we need to reset it.
            self.mark_cell(next_cell, Maze.TREE)
        else:
            self.add_to_path(next_cell)
        return next_cell

    def erase_loop(self, cell):
        """When `cell` is visited twice a loop is found. Erase this loop.
        Do not forget the space between path[index] and path[index+1]."""
        index = self.path.index(cell)
        # erase the loop
        self.mark_path(self.path[index:], Maze.WALL)
        # re-mark this cell
        self.mark_cell(self.path[index], Maze.PATH)
        self.path = self.path[:index+1]

    def add_to_path(self, cell):
        self.mark_cell(cell, Maze.PATH)
        self.mark_wall(self.path[-1], cell, Maze.PATH)
        self.path.append(cell)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-width', type=int, default=121,
                        help='width of the maze')
    parser.add_argument('-height', type=int, default=97,
                        help='height of the maze')
    parser.add_argument('-margin', type=int, default=2,
                        help='border of the maze')
    parser.add_argument('-scale', type=int, default=5,
                        help='size of a cell in pixels')
    parser.add_argument('-loop', type=int, default=0,
                        help='number of loops of the animation, default to 0 (loop infinitely)')
    parser.add_argument('-bits', metavar='b', type=int, default=8,
                        help='an interger beteween 2-8 represents the minimal number of bits needed to\
                        represent the colors, this parameter determines the size of the global color table.')
    parser.add_argument('-filename', type=str, default='wilson.gif',
                        help='output file name')
    args = parser.parse_args()

    if (args.width * args.height % 2 == 0):
        raise ValueError('The width and height of the maze must both be odd integers!')

    mypalette = [0, 0, 0,         # wall color
                 200, 200, 200,   # tree color
                 255, 0, 255]     # path color

    # GIF files allows at most 256 colors in the global color table,
    # redundant colors will be discarded when we initialize the encoder.
    for i in range(256):
        rgb = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
        mypalette += map(lambda x: int(round(255 * x)), rgb)

    # Comment out the following two lines if you don't want to show text.
    from gentext import generate_text_mask
    mask = generate_text_mask(args.width, args.height, 'UST', '../resources/ubuntu.ttf', 60)

    maze = Wilson(args.width, args.height, args.margin, mask=mask)
    canvas = maze.add_canvas(scale=args.scale, min_bits=args.bits, palette=mypalette,
                             loop=args.loop, filename=args.filename)

    # Here we need to paint the blank background because the region that has not been
    # covered by any frame will be set to transparent by decoders.
    # Comment this line and watch the result if you don't understand this.
    canvas.paint_background(wall_color=0)

    # pad one second delay, get ready!
    canvas.pad_delay_frame(delay=100)

    # In the Wilson's algorithm animation no cells are filled,
    # hence it's safe to use color 3 as the transparent color.
    print('Generating the uniform spanning tree with Wilson\'s algorithm...')
    canvas.set_control_params(delay=2, speed=50, trans_index=3,
                              wall_color=0, tree_color=1, path_color=2)
    maze.run_wilson_algorithm(root=(2, 2))

    # Pad three seconds delay to help to see the resulting maze clearly.
    canvas.pad_delay_frame(delay=300)

    # In the dfs/bfs algorithm animation the walls are unchanged throughout,
    # hence it's safe to use color 0 as the transparent color.
    canvas.set_control_params(delay=5, speed=50, trans_index=0, wall_color=0,
                              tree_color=0, path_color=2, fill_color=3)
    start = (args.margin, args.margin)
    end = (args.width - args.margin - 1, args.height - args.margin - 1)
    print('Searching the resulting maze with BFS algorithm...')
    bfs(maze, start, end)

    # Pad five seconds delay to help to see the resulting path clearly.
    canvas.pad_delay_frame(delay=500)

    # Finally finish the animation and close the file.
    canvas.save()
    print('Done!')
