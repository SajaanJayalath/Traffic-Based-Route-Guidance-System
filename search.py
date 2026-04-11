import sys
import math
from collections import deque
import heapq


# ============================================================
# FILE PARSER
# ============================================================

def parse_file(filename):
    """
    Parses the problem file and returns:
      - nodes:        dict {node_id (int): (x, y)}
      - edges:        dict {node_id (int): [(neighbour_id, cost), ...]}
      - origin:       int
      - destinations: list of int
    """
    nodes = {}
    edges = {}
    origin = None
    destinations = []
    section = None

    with open(filename, 'r') as f:
        lines = [line.strip() for line in f.readlines()]

    for line in lines:
        if line == '':
            continue
        elif line == 'Nodes:':
            section = 'nodes'
        elif line == 'Edges:':
            section = 'edges'
        elif line == 'Origin:':
            section = 'origin'
        elif line == 'Destinations:':
            section = 'destinations'
        else:
            if section == 'nodes':
                # Format: 1: (4,1)
                colon_idx = line.index(':')
                node_id = int(line[:colon_idx].strip())
                coords_str = line[colon_idx + 1:].strip().strip('()')
                x, y = map(int, coords_str.split(','))
                nodes[node_id] = (x, y)
                edges[node_id] = []

            elif section == 'edges':
                # Format: (2,1): 4
                colon_idx = line.index(':')
                nodes_str = line[:colon_idx].strip().strip('()')
                cost = int(line[colon_idx + 1:].strip())
                from_node, to_node = map(int, nodes_str.split(','))
                edges[from_node].append((to_node, cost))

            elif section == 'origin':
                origin = int(line.strip())

            elif section == 'destinations':
                destinations = [int(d.strip()) for d in line.split(';')]

    return nodes, edges, origin, destinations


# ============================================================
# HEURISTIC
# ============================================================

def heuristic(nodes, node_id, goals):
    """
    Returns the minimum Euclidean (straight-line) distance
    from node_id to the nearest goal node.
    This is admissible — never overestimates actual cost.
    """
    x1, y1 = nodes[node_id]
    return min(
        math.sqrt((nodes[g][0] - x1) ** 2 + (nodes[g][1] - y1) ** 2)
        for g in goals
    )


# ============================================================
# PATH RECONSTRUCTION
# ============================================================

def reconstruct_path(came_from, goal):
    """
    Traces back through came_from to build path from origin to goal.
    came_from[node] = parent node (None for origin).
    """
    path = []
    node = goal
    while node is not None:
        path.append(node)
        node = came_from[node]
    path.reverse()
    return path


# ============================================================
# 1. BFS — Breadth-First Search (Uninformed)
# ============================================================

def bfs(nodes, edges, origin, destinations):
    """
    Explores nodes level by level using a FIFO queue.
    Guarantees path with fewest hops (not necessarily lowest cost).
    Neighbours added in ascending order for tie-breaking.
    """
    goals = set(destinations)

    if origin in goals:
        return origin, 1, [origin]

    queue = deque([origin])
    came_from = {origin: None}
    nodes_created = 1

    while queue:
        current = queue.popleft()

        # Expand neighbours in ascending node order (tie-breaking rule)
        for neighbour, _ in sorted(edges[current], key=lambda e: e[0]):
            if neighbour not in came_from:
                came_from[neighbour] = current
                nodes_created += 1

                if neighbour in goals:
                    return neighbour, nodes_created, reconstruct_path(came_from, neighbour)

                queue.append(neighbour)

    return None, nodes_created, []


# ============================================================
# 2. DFS — Depth-First Search (Uninformed)
# ============================================================

def dfs(nodes, edges, origin, destinations):
    """
    Explores as deep as possible before backtracking using a LIFO stack.
    Does NOT guarantee optimal path.
    Neighbours pushed in descending order so smallest pops first (tie-breaking).
    """
    goals = set(destinations)

    if origin in goals:
        return origin, 1, [origin]

    stack = [origin]
    came_from = {origin: None}
    nodes_created = 1

    while stack:
        current = stack.pop()

        if current in goals:
            return current, nodes_created, reconstruct_path(came_from, current)

        # Push descending so smallest node is on top of stack
        for neighbour, _ in sorted(edges[current], key=lambda e: e[0], reverse=True):
            if neighbour not in came_from:
                came_from[neighbour] = current
                nodes_created += 1
                stack.append(neighbour)

    return None, nodes_created, []


# ============================================================
# 3. GBFS — Greedy Best-First Search (Informed)
# ============================================================

def gbfs(nodes, edges, origin, destinations):
    """
    Always expands the node closest to the goal by heuristic.
    Priority = h(n) = Euclidean distance to nearest goal.
    Fast but NOT guaranteed optimal.
    Tie-breaking: smaller node number first (secondary sort key).
    """
    goals = set(destinations)

    if origin in goals:
        return origin, 1, [origin]

    # Heap entry: (h_value, node_id)
    heap = [(heuristic(nodes, origin, goals), origin)]
    came_from = {origin: None}
    nodes_created = 1

    while heap:
        _, current = heapq.heappop(heap)

        if current in goals:
            return current, nodes_created, reconstruct_path(came_from, current)

        for neighbour, _ in sorted(edges[current], key=lambda e: e[0]):
            if neighbour not in came_from:
                came_from[neighbour] = current
                nodes_created += 1
                h = heuristic(nodes, neighbour, goals)
                heapq.heappush(heap, (h, neighbour))

    return None, nodes_created, []


# ============================================================
# 4. A* — A Star Search (Informed)
# ============================================================

def astar(nodes, edges, origin, destinations):
    """
    Combines actual path cost g(n) and heuristic h(n).
    Priority = f(n) = g(n) + h(n).
    Guarantees optimal (lowest cost) path.
    Tie-breaking: smaller node number first (secondary sort key).
    """
    goals = set(destinations)

    if origin in goals:
        return origin, 1, [origin]

    # Heap entry: (f_value, node_id)
    heap = [(heuristic(nodes, origin, goals), origin)]
    came_from = {origin: None}
    g_cost = {origin: 0}
    nodes_created = 1

    while heap:
        f, current = heapq.heappop(heap)

        if current in goals:
            return current, nodes_created, reconstruct_path(came_from, current)

        for neighbour, cost in sorted(edges[current], key=lambda e: e[0]):
            new_g = g_cost[current] + cost

            if neighbour not in g_cost or new_g < g_cost[neighbour]:
                if neighbour not in g_cost:
                    nodes_created += 1
                g_cost[neighbour] = new_g
                came_from[neighbour] = current
                f_val = new_g + heuristic(nodes, neighbour, goals)
                heapq.heappush(heap, (f_val, neighbour))

    return None, nodes_created, []


# ============================================================
# 5. CUS1 — Uniform Cost Search (Uninformed Custom)
# ============================================================

def cus1(nodes, edges, origin, destinations):
    """
    CUS1: Uniform Cost Search (UCS).
    Expands nodes by lowest accumulated path cost g(n).
    No heuristic — purely cost-driven (uninformed).
    Guarantees optimal (lowest cost) path.
    Tie-breaking: smaller node number first.
    """
    goals = set(destinations)

    if origin in goals:
        return origin, 1, [origin]

    # Heap entry: (g_cost, node_id)
    heap = [(0, origin)]
    came_from = {origin: None}
    g_cost = {origin: 0}
    nodes_created = 1

    while heap:
        g, current = heapq.heappop(heap)

        if current in goals:
            return current, nodes_created, reconstruct_path(came_from, current)

        # Skip outdated heap entries
        if g > g_cost.get(current, float('inf')):
            continue

        for neighbour, cost in sorted(edges[current], key=lambda e: e[0]):
            new_g = g + cost

            if neighbour not in g_cost or new_g < g_cost[neighbour]:
                if neighbour not in g_cost:
                    nodes_created += 1
                g_cost[neighbour] = new_g
                came_from[neighbour] = current
                heapq.heappush(heap, (new_g, neighbour))

    return None, nodes_created, []


# ============================================================
# 6. CUS2 — Bidirectional BFS (Informed Custom)
# ============================================================

def cus2(nodes, edges, origin, destinations):
    """
    CUS2: Bidirectional BFS.
    Searches simultaneously from the origin AND from all goal nodes.
    Finds the path with the LEAST number of hops (moves).
    Uses goal knowledge — hence classified as informed.
    Much more efficient than standard BFS on large graphs.
    """
    goals = set(destinations)

    if origin in goals:
        return origin, 1, [origin]

    # Build reverse edges for backward search
    reverse_edges = {node: [] for node in nodes}
    for from_node, neighbours in edges.items():
        for to_node, cost in neighbours:
            reverse_edges[to_node].append((from_node, cost))

    # Forward frontier from origin
    fwd_visited = {origin: None}   # node: parent
    fwd_queue = deque([origin])

    # Backward frontier from all goals
    bwd_visited = {g: None for g in goals}
    bwd_queue = deque(sorted(goals))

    nodes_created = 1 + len(goals)

    def build_path(meeting):
        """
        Builds the full path through the meeting node.
        Returns (actual_goal, full_path).
        The actual goal is the last node in the backward chain.
        """
        # Forward half: origin ... meeting
        fwd_half = []
        node = meeting
        while node is not None:
            fwd_half.append(node)
            node = fwd_visited[node]
        fwd_half.reverse()

        # Backward half: after meeting node ... goal
        bwd_half = []
        node = bwd_visited[meeting]
        while node is not None:
            bwd_half.append(node)
            node = bwd_visited[node]

        full_path = fwd_half + bwd_half
        # The actual goal is the last node in the full path
        actual_goal = full_path[-1]
        return actual_goal, full_path

    while fwd_queue or bwd_queue:

        # Expand one node from forward frontier
        if fwd_queue:
            current = fwd_queue.popleft()
            for neighbour, _ in sorted(edges[current], key=lambda e: e[0]):
                if neighbour not in fwd_visited:
                    fwd_visited[neighbour] = current
                    nodes_created += 1
                    fwd_queue.append(neighbour)
                if neighbour in bwd_visited:
                    actual_goal, path = build_path(neighbour)
                    return actual_goal, nodes_created, path

        # Expand one node from backward frontier
        if bwd_queue:
            current = bwd_queue.popleft()
            for neighbour, _ in sorted(reverse_edges[current], key=lambda e: e[0]):
                if neighbour not in bwd_visited:
                    bwd_visited[neighbour] = current
                    nodes_created += 1
                    bwd_queue.append(neighbour)
                if neighbour in fwd_visited:
                    actual_goal, path = build_path(neighbour)
                    return actual_goal, nodes_created, path

    return None, nodes_created, []


# ============================================================
# MAIN
# ============================================================

def main():
    if len(sys.argv) != 3:
        print("Usage: python search.py <filename> <method>")
        print("Methods: DFS, BFS, GBFS, AS, CUS1, CUS2")
        sys.exit(1)

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    valid_methods = ['DFS', 'BFS', 'GBFS', 'AS', 'CUS1', 'CUS2']
    if method not in valid_methods:
        print(f"Invalid method. Choose from: {', '.join(valid_methods)}")
        sys.exit(1)

    try:
        nodes, edges, origin, destinations = parse_file(filename)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        sys.exit(1)

    algorithm = {
        'BFS':  bfs,
        'DFS':  dfs,
        'GBFS': gbfs,
        'AS':   astar,
        'CUS1': cus1,
        'CUS2': cus2,
    }

    goal, num_nodes, path = algorithm[method](nodes, edges, origin, destinations)

    # Print output in required format
    print(f"{filename} {method}")
    if goal is not None:
        print(f"{goal} {num_nodes}")
        print(' -> '.join(map(str, path)))
    else:
        print("No path found.")


if __name__ == '__main__':
    main()
