# -*- coding: utf-8 -*-

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Implementation of several maze solving algorithms
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
import heapq
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
    cameFrom = dict()  # a dict to remember each step.
    queue = deque([(start, start, dist)])
    maze.mark_cell(start, dist_to_color(dist))
    visited = set([start])

    while len(queue) > 0:
        parent, child, dist = queue.popleft()
        cameFrom[child] = parent
        maze.mark_cell(child, dist_to_color(dist))
        maze.mark_wall(parent, child, dist_to_color(dist))

        for nextCell in maze.get_neighbors(child):
            if (nextCell not in visited) and (not maze.barrier(child, nextCell)):
                queue.append((child, nextCell, dist + 1))
                visited.add(nextCell)

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()

    # retrieve the path
    path = [end]
    parent = end
    while parent != start:
        parent = cameFrom[parent]
        path.append(parent)
    maze.mark_path(path, Maze.PATH)
    # show the path
    maze.canvas.clear_remaining_changes()


def dfs(maze, start, end):
    """Animating the depth-first search algorithm."""
    def dist_to_color(d):
        depth = maze.canvas.writer.get_color_depth()
        return max(d % (1 << depth), 3)

    dist = 0
    cameFrom = dict()  # a dict to remember each step.
    stack = [(start, start, dist)]
    maze.mark_cell(start, dist_to_color(dist))
    visited = set([start])
    
    while len(stack) > 0:
        parent, child, dist = stack.pop()
        cameFrom[child] = parent
        maze.mark_cell(child, dist_to_color(dist))
        maze.mark_wall(parent, child, dist_to_color(dist))
        for nextCell in maze.get_neighbors(child):
            if (nextCell not in visited) and (not maze.barrier(child, nextCell)):
                stack.append((child, nextCell, dist + 1))
                visited.add(nextCell)

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()

    # retrieve the path
    path = [end]
    parent = end
    while parent != start:
        parent = cameFrom[parent]
        path.append(parent)
    maze.mark_path(path, Maze.PATH)
    # show the path
    maze.canvas.clear_remaining_changes()


def astar(maze, edges, start, end):
    """The A-star search algorithm."""
    def manhattan(u, v):
        """The heuristic distance between two cells."""
        return abs(u[0] - v[0]) + abs(u[1] - v[1])

    def get_weight(edgeWeights, a, b):
        """Return the weight of an edge in the grid."""
        try:
            return edgeWeights[(a, b)]
        except KeyError:
            return edgeWeights[(b, a)]

    priorityQueue = [(0, start, start)]
    cameFrom = dict()
    costSoFar = {start: 0}
    while len(priorityQueue) > 0:
        _, parent, child = heapq.heappop(priorityQueue)
        maze.mark_cell(child, Maze.FILL)
        maze.mark_wall(parent, child, Maze.FILL)
        if child == end:
            break

        for nextCell in maze.get_neighbors(child):
            newCost = costSoFar[parent] + get_weight(edges, child, nextCell)
            if (nextCell not in costSoFar or newCost < costSoFar[nextCell]) and (not maze.barrier(nextCell, child)):
                costSoFar[nextCell] = newCost
                priority = newCost + manhattan(nextCell, end)
                heapq.heappush(priorityQueue, (priority, child, nextCell))
                cameFrom[nextCell] = child

        maze.canvas.refresh_frame()
    maze.canvas.clear_remaining_changes()

    # retrieve the path
    path = [end]
    parent = end
    while parent != start:
        parent = cameFrom[parent]
        path.append(parent)
    maze.mark_path(path, Maze.PATH)
    # show the path
    maze.canvas.clear_remaining_changes()
