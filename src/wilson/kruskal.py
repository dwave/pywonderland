# -*- coding: utf-8 -*-
"""
A simple demo shows how to generate a maze with Kruskal's algorithm.
"""
import random
from maze import Maze
from search_algorithms import astar

try:
    from tqdm import tqdm
except ImportError:
    tqdm = list
    print('Module \'tqdm\' not found, process bar prohibited.')


def find(parent, u):
    """find the root of the subtree that u belongs to."""
    v = u
    while parent[v] != v:
        v = parent[v]
    return v


def greater(u, v):
    """compare two different cells with the alphabetical order."""
    for x, y in zip(u, v):
        if x > y:
            return True
        if x < y:
            return False


# firstly set the params of the image.
width = 121
height = 101
margin = 2
start = (margin, height - margin - 1)
end = (width - margin - 1, margin)
mypalette = [0, 0, 0, 200, 200, 200, 255, 0, 255, 150, 200, 100]

# now add a canvas to the maze.
maze = Maze(width, height, margin)

# generate weights of the edges, each pair occurs only once in this dict.
edges = {(u, v): random.random() for u in maze.cells for v in maze.get_neighbors(u) if greater(u, v)}
# add canvas to the maze.
canvas = maze.add_canvas(scale=5, min_bits=2, palette=mypalette,
                         loop=0, filename='kruskal.gif')

# paint the background image.
canvas.paint_background(wall_color=0)

# pad one-second delay, get ready!
canvas.pad_delay_frame(delay=100)

canvas.set_control_params(delay=3, speed=30, trans_index=3,
                          wall_color=0, tree_color=1, path_color=2)

parent = {v: v for v in maze.cells}
rank = {v: 0 for v in maze.cells}

print('Generaing the maze using Kruskal\'s algorithm...')
for u, v in tqdm(sorted(edges, key=edges.get)):
    root1 = find(parent, u)
    root2 = find(parent, v)
    if root1 != root2:
        if rank[root1] > rank[root2]:
            parent[root2] = root1
        elif rank[root1] < rank[root2]:
            parent[root1] = root2
        else:
            parent[root1] = root2
            rank[root2] += 1

        maze.mark_cell(u, Maze.TREE)
        maze.mark_cell(v, Maze.TREE)
        maze.mark_wall(u, v, Maze.TREE)
        canvas.refresh_frame()
canvas.clear_remaining_changes()

# pad three seconds delay to see the maze clearly.
canvas.pad_delay_frame(300)

canvas.set_control_params(delay=5, speed=10, trans_index=0,
                          wall_color=0, tree_color=0, path_color=2, fill_color=3)

# solve the maze.
print('Solving the maze with A* algorithm...')
astar(maze, edges, start, end)

# pad five seconds delay to see the path clearly.
canvas.pad_delay_frame(500)

# close the file and save the image.
canvas.save()
print('Done!')
