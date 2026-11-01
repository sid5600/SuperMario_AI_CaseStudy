"""
Super Mario AI Case Study
Algorithm: Breadth-First Search (BFS)
Task: Find the shortest safe route to the Super Star.
Author: Siddhant Kumar Singh | Roll No: 2024109296
"""

from collections import deque

GRID = [
    [0, 0, 1, 0, 0, 0, 0],
    [0, 1, 1, 0, 1, 0, 0],
    [0, 0, 0, 0, 1, 0, 1],
    [1, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 1, 0],
    [0, 1, 0, 0, 0, 0, 0],
]

START = (0, 0)
GOAL = (5, 6)
MOVES = [(-1, 0), (1, 0), (0, -1), (0, 1)]


def breadth_first_search(grid, start, goal):
    queue = deque([(start, [start])])
    visited = {start}
    explored_order = []

    while queue:
        current, path = queue.popleft()
        explored_order.append(current)
        if current == goal:
            return path, explored_order

        for dr, dc in MOVES:
            nr, nc = current[0] + dr, current[1] + dc
            neighbor = (nr, nc)
            if (
                0 <= nr < len(grid)
                and 0 <= nc < len(grid[0])
                and grid[nr][nc] == 0
                and neighbor not in visited
            ):
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return [], explored_order


def main():
    path, explored = breadth_first_search(GRID, START, GOAL)
    print("Breadth-First Search — Shortest Safe Route")
    print(f"Start: {START} | Goal: {GOAL}")
    print(f"Nodes expanded: {len(explored)}")
    if path:
        print(f"Shortest path length: {len(path) - 1} moves")
        print(f"Path: {path}")
    else:
        print("The Super Star could not be reached.")


if __name__ == "__main__":
    main()
