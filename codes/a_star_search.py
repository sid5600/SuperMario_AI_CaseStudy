"""
Super Mario AI Case Study
Algorithm: A* Search
Task: Find an efficient shortest route to the Super Star.
Author: Siddhant Kumar Singh | Roll No: 2024109296
"""

import heapq

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


def heuristic(position, goal):
    return abs(position[0] - goal[0]) + abs(position[1] - goal[1])


def a_star_search(grid, start, goal):
    open_list = [(heuristic(start, goal), 0, start, [start])]
    best_cost = {start: 0}
    explored_order = []

    while open_list:
        f_score, cost, current, path = heapq.heappop(open_list)
        if cost != best_cost.get(current):
            continue
        explored_order.append(current)
        if current == goal:
            return path, explored_order

        for dr, dc in MOVES:
            nr, nc = current[0] + dr, current[1] + dc
            neighbor = (nr, nc)
            if not (
                0 <= nr < len(grid)
                and 0 <= nc < len(grid[0])
                and grid[nr][nc] == 0
            ):
                continue

            new_cost = cost + 1
            if new_cost < best_cost.get(neighbor, float("inf")):
                best_cost[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal)
                heapq.heappush(
                    open_list, (priority, new_cost, neighbor, path + [neighbor])
                )

    return [], explored_order


def main():
    path, explored = a_star_search(GRID, START, GOAL)
    print("A* Search — Efficient Shortest Route")
    print(f"Start: {START} | Goal: {GOAL}")
    print(f"Nodes expanded: {len(explored)}")
    if path:
        print(f"Optimal path length: {len(path) - 1} moves")
        print(f"Path: {path}")
    else:
        print("The Super Star could not be reached.")


if __name__ == "__main__":
    main()
