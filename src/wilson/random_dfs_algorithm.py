# -*- coding: utf-8 -*-
"""
A simple demo shows how to generat a maze with random depth-first search.
"""
import random
from maze import Maze


# firstly set the params of the image.
width = 101
height = 81
margin = 2
start = (margin, margin)
end = (width - margin - 1, height - margin - 1)
mypalette = [0, 0, 0, 200, 200, 200, 255, 0, 255, 150, 200, 100]

# now add a canvas to the maze.
maze = Maze(width, height, margin)
canvas = maze.add_canvas(scale=5, min_bits=2, palette=mypalette,
                         loop=0, filename='random_dfs.gif')

# paint the background image.
canvas.paint_background(wall_color=0)

# pad one-second delay, get ready!
canvas.pad_delay_frame(delay=100)
 
canvas.set_control_params(delay=3, speed=10, trans_index=3,
                          wall_color=0, tree_color=1, path_color=2)

stack = [(start, v) for v in maze.get_neighbors(start)]
maze.mark_cell(start, Maze.TREE)

# the main loop.
while len(stack) > 0:
    parent, child = stack.pop()
    if maze.in_tree(child):
        continue
    maze.mark_cell(child, Maze.TREE)
    maze.mark_wall(parent, child, Maze.TREE)
    neighbors = maze.get_neighbors(child)
    random.shuffle(neighbors)
    for v in neighbors:
        stack.append((child, v))

    canvas.refresh_frame()
canvas.clear_remaining_changes()

# pad five seconds delay to see the maze clearly.
canvas.pad_delay_frame(500)

# close the file and save the image.
canvas.save()
