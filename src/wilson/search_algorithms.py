# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Implement several maze solving algorithms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from collections import deque
from maze import Maze


def bfs(maze, start, end):
    """
    Animating the breadth-first search algorithm with colors.
    The maze is colored according to their distance to the start.
    """
    def dist_to_color(d):
        depth = maze.canvas.writer.get_color_depth()
        return max(d % (1 << depth), 3)

    dist = 0
    from_to = dict()  # a dict to remember each step.
    queue = deque([(start, start, dist)])
    maze.mark_cell(start, dist_to_color(dist))
    visited = set([start])

    while len(queue) > 0:
        parent, child, dist = queue.popleft()
        from_to[child] = parent
        maze.mark_cell(child, dist_to_color(dist))
        maze.mark_wall(parent, child, dist_to_color(dist))

        for next_cell in maze.get_neighbors(child):
            if (next_cell not in visited) and (not maze.connected(child, next_cell)):
                queue.append((child, next_cell, dist + 1))
                visited.add(next_cell)

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()

    # retrieve the path
    path = [end]
    parent = end
    while parent != start:
        parent = from_to[parent]
        path.append(parent)
    maze.mark_path(path, Maze.PATH)
    # show the path
    maze.canvas.clear_remaining_changes()


def dfs(maze, start, end):
    """Animating the depth-first search algorithm."""
    from_to = dict()  # a dict to remember each step.
    stack = [(start, start)]
    maze.mark_cell(start, Maze.FILL)
    visited = set([start])
    
    while len(stack) > 0:
        parent, child = stack.pop()
        from_to[child] = parent
        maze.mark_cell(child, Maze.FILL)
        maze.mark_wall(parent, child, Maze.FILL)
        for next_cell in maze.get_neighbors(child):
            if (next_cell not in visited) and (not maze.connected(child, next_cell)):
                stack.append((child, next_cell))
                visited.add(next_cell)

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()

    # retrieve the path
    path = [end]
    parent = end
    while parent != start:
        parent = from_to[parent]
        path.append(parent)
    maze.mark_path(path, Maze.PATH)
    # show the path
    maze.canvas.clear_remaining_changes()
