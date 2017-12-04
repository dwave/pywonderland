# -*- coding: utf-8 -*-
"""
A simple demo shows how to generate a maze with Prim's algorithm.
"""
import heapq
import random
from colorsys import hls_to_rgb
from maze import Maze
from search_algorithms import dfs


# firstly set the params of the image.
width = 121
height = 101
margin = 2
start = (margin, height - margin - 1)
end = (width - margin - 1, margin)
mypalette = [0, 0, 0, 200, 200, 200, 255, 0, 255]

for i in range(256):
    rgb = hls_to_rgb((i / 360.0) % 1, 0.5, 1.0)
    mypalette += map(lambda x: int(round(255 * x)), rgb)

# now add a canvas to the maze.
maze = Maze(width, height, margin)
canvas = maze.add_canvas(scale=5, min_bits=8, palette=mypalette,
                         loop=0, filename='prim.gif')

# paint the background image.
canvas.paint_background(wall_color=0)

# pad one-second delay, get ready!
canvas.pad_delay_frame(delay=100)

canvas.set_control_params(delay=3, speed=5, trans_index=3,
                          wall_color=0, tree_color=1, path_color=2)

queue = [(0, start, v) for v in maze.get_neighbors(start)]
maze.mark_cell(start, Maze.TREE)

# the main loop.
while len(queue) > 0:
    _, parent, child = heapq.heappop(queue)
    if maze.in_tree(child):
        continue

    maze.mark_cell(child, Maze.TREE)
    maze.mark_wall(parent, child, Maze.TREE)
    for v in maze.get_neighbors(child):
        # assign a weight to this edge only when it's needed.
        w = round(random.random(), 3)
        heapq.heappush(queue, (w, child, v))

    canvas.refresh_frame()
canvas.clear_remaining_changes()

# pad three seconds delay to see the maze clearly.
canvas.pad_delay_frame(300)

canvas.set_control_params(delay=5, speed=30, trans_index=0,
                          wall_color=0, tree_color=0, path_color=2, fill_color=3)

# solve the maze and pad five seconds delay to see the path clearly.
dfs(maze, start, end)
canvas.pad_delay_frame(500)

# close the file and save the image.
canvas.save()
