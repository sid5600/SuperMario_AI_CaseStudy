"""
=====================================================================
  Super Mario AI Case Study
  Algorithm: Greedy Best-First Search (GBFS)
  Task:      Chase a Disappearing Super Star
  Author:    Siddhant Kumar Singh  |  Roll No: 2024109296
=====================================================================

Narrative:
-----------
Mario spots a Super Star on a distant platform. The star will vanish
after a short time, so Mario cannot afford careful exhaustive search.
His AI assistant applies Greedy Best-First Search, always expanding
whichever node seems closest to the star based on Manhattan-distance
heuristic. This is fast but not guaranteed optimal—sometimes the
"closest-looking" cell leads into a dead-end and Mario is forced to
backtrack.

PEAS Description:
  Performance : Reach the Super Star before the timer expires
  Environment : 2-D castle grid with walls, enemies, and the star
  Actuators   : Move Up / Down / Left / Right
  Sensors     : Current position, goal position, grid layout

Task Environment Properties:
  Fully Observable | Deterministic | Sequential | Static | Discrete | Single-Agent

Problem Formulation:
  State       : (row, col) position of Mario
  Initial     : user-defined start cell
  Goal        : cell containing the Super Star
  Actions     : {Up, Down, Left, Right}  (no diagonal)
  Heuristic   : h(n) = |row_n - row_goal| + |col_n - col_goal|  (Manhattan)
=====================================================================
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

ROWS = len(GRID)
COLS = len(GRID[0])

START = (0, 0)
GOAL  = (5, 6)

MOVES = {
    "UP":    (-1,  0),
    "DOWN":  ( 1,  0),
    "LEFT":  ( 0, -1),
    "RIGHT": ( 0,  1),
}


def heuristic(pos, goal):
    return abs(pos[0] - goal[0]) + abs(pos[1] - goal[1])


def greedy_bfs(grid, start, goal):
    open_list = []
    heapq.heappush(open_list, (heuristic(start, goal), start, [start]))

    visited = set()
    visited.add(start)
    explored_order = []

    print("\n" + "="*60)
    print("   Greedy Best-First Search — Chasing the Super Star")
    print("="*60)
    print(f"   Start : {start}")
    print(f"   Goal  : {goal}")
    print("="*60)
    print(f"\n{'Step':>4}  {'Current':>10}  {'h(n)':>6}  Neighbors Considered")
    print("-"*60)

    step = 0

    while open_list:
        h_val, current, path = heapq.heappop(open_list)
        explored_order.append(current)
        step += 1

        neighbors_info = []
        for direction, (dr, dc) in MOVES.items():
            nr, nc = current[0] + dr, current[1] + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == 0:
                neighbor = (nr, nc)
                h_n = heuristic(neighbor, goal)
                status = "visited" if neighbor in visited else f"h={h_n}"
                neighbors_info.append(f"{direction}:{neighbor}({status})")

        print(f"{step:>4}  {str(current):>10}  {h_val:>6}  {', '.join(neighbors_info)}")

        if current == goal:
            print("\n" + "="*60)
            print(f"   Super Star REACHED in {step} expansions!")
            print(f"   Path length : {len(path) - 1} moves")
            print("="*60)
            return path, explored_order, True

        for direction, (dr, dc) in MOVES.items():
            nr, nc = current[0] + dr, current[1] + dc
            if 0 <= nr < ROWS and 0 <= nc < COLS and grid[nr][nc] == 0:
                neighbor = (nr, nc)
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = path + [neighbor]
                    heapq.heappush(open_list, (heuristic(neighbor, goal), neighbor, new_path))

    print("\n   Super Star could NOT be reached.")
    return [], explored_order, False


def visualise(grid, path, start, goal):
    path_set = set(path)
    print("\n  Grid (S=Start, G=Goal, *=Path, #=Wall, .=Open)")
    print("  " + "-" * (COLS * 2 + 1))
    for r in range(ROWS):
        row_str = "  |"
        for c in range(COLS):
            cell = (r, c)
            if cell == start:
                ch = "S"
            elif cell == goal:
                ch = "G"
            elif cell in path_set:
                ch = "*"
            elif grid[r][c] == 1:
                ch = "#"
            else:
                ch = "."
            row_str += ch + " "
        print(row_str.rstrip() + "|")
    print("  " + "-" * (COLS * 2 + 1))


def main():
    path, explored, success = greedy_bfs(GRID, START, GOAL)

    print(f"\n  Exploration Order ({len(explored)} nodes):")
    for i, node in enumerate(explored, 1):
        print(f"    {i:>2}. {node}")

    if success:
        print(f"\n  Final Path ({len(path) - 1} moves):")
        for i, node in enumerate(path):
            tag = " <- START" if node == START else (" <- GOAL" if node == GOAL else "")
            print(f"    Step {i:>2}: {node}{tag}")
        visualise(GRID, path, START, GOAL)

    print("\n  Key Observations:")
    print("  * GBFS always expands the node that LOOKS closest to the goal.")
    print("  * It is faster than BFS but NOT guaranteed to find the shortest path.")
    print("  * If the heuristic is misleading, GBFS can take a longer detour.")
    print("  * Time Complexity: O(b^m)  |  Complete: No  |  Optimal: No\n")


if __name__ == "__main__":
    main()
