import sys
import math
import heapq
from collections import deque

# -----------------------------
# GRAPH PARSER
# -----------------------------
def parse_file(filename):
    nodes = {}
    graph = {}
    origin = None
    goals = []

    section = None

    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            if line.startswith("Nodes"):
                section = "nodes"
                continue
            elif line.startswith("Edges"):
                section = "edges"
                continue
            elif line.startswith("Origin"):
                section = "origin"
                continue
            elif line.startswith("Destinations"):
                section = "dest"
                continue

            if section == "nodes":
                node, coord = line.split(":")
                x, y = coord.strip()[1:-1].split(",")
                nodes[int(node)] = (int(x), int(y))
                graph[int(node)] = []

            elif section == "edges":
                edge, cost = line.split(":")
                u, v = edge.strip()[1:-1].split(",")
                graph[int(u)].append((int(v), int(cost)))

            elif section == "origin":
                origin = int(line)

            elif section == "dest":
                goals = list(map(int, line.split(";")))

    return nodes, graph, origin, goals


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------
class Node:
    def __init__(self, state, parent=None, cost=0):
        self.state = state
        self.parent = parent
        self.cost = cost

    def __lt__(self, other):
        return self.state < other.state


def reconstruct_path(node):
    path = []
    while node:
        path.append(node.state)
        node = node.parent
    return path[::-1]


def heuristic(a, b, coords):
    (x1, y1) = coords[a]
    (x2, y2) = coords[b]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def min_heuristic(n, goals, coords):
    return min(heuristic(n, g, coords) for g in goals)


# -----------------------------
# BFS
# -----------------------------
def bfs(graph, start, goals):
    queue = deque([Node(start)])
    visited = set([start])
    count = 1

    while queue:
        node = queue.popleft()

        if node.state in goals:
            return node, count

        for neighbor, cost in sorted(graph[node.state]):
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(Node(neighbor, node))
                count += 1

    return None, count


# -----------------------------
# DFS
# -----------------------------
def dfs(graph, start, goals):
    stack = [Node(start)]
    visited = set()
    count = 1

    while stack:
        node = stack.pop()

        if node.state in visited:
            continue

        visited.add(node.state)

        if node.state in goals:
            return node, count

        for neighbor, cost in sorted(graph[node.state], reverse=True):
            stack.append(Node(neighbor, node))
            count += 1

    return None, count


# -----------------------------
# UCS (CUS1)
# -----------------------------
def ucs(graph, start, goals):
    pq = [(0, Node(start))]
    visited = {}

    count = 1

    while pq:
        cost, node = heapq.heappop(pq)

        if node.state in visited and visited[node.state] <= cost:
            continue

        visited[node.state] = cost

        if node.state in goals:
            return node, count

        for neighbor, c in graph[node.state]:
            heapq.heappush(pq, (cost + c, Node(neighbor, node, cost + c)))
            count += 1

    return None, count


# -----------------------------
# GBFS
# -----------------------------
def gbfs(graph, start, goals, coords):
    pq = [(min_heuristic(start, goals, coords), Node(start))]
    visited = set()
    count = 1

    while pq:
        _, node = heapq.heappop(pq)

        if node.state in visited:
            continue

        visited.add(node.state)

        if node.state in goals:
            return node, count

        for neighbor, _ in graph[node.state]:
            h = min_heuristic(neighbor, goals, coords)
            heapq.heappush(pq, (h, Node(neighbor, node)))
            count += 1

    return None, count


# -----------------------------
# A*
# -----------------------------
def astar(graph, start, goals, coords):
    pq = [(0, Node(start, cost=0))]
    visited = {}

    count = 1

    while pq:
        f, node = heapq.heappop(pq)

        if node.state in visited and visited[node.state] <= node.cost:
            continue

        visited[node.state] = node.cost

        if node.state in goals:
            return node, count

        for neighbor, c in graph[node.state]:
            g = node.cost + c
            h = min_heuristic(neighbor, goals, coords)
            heapq.heappush(pq, (g + h, Node(neighbor, node, g)))
            count += 1

    return None, count


# -----------------------------
# BIDIRECTIONAL BFS (CUS2)
# -----------------------------
def bidirectional_bfs(graph, start, goals):
    for goal in goals:
        q_start = deque([Node(start)])
        q_goal = deque([Node(goal)])

        visited_start = {start: Node(start)}
        visited_goal = {goal: Node(goal)}

        count = 2

        while q_start and q_goal:

            # Forward
            node_s = q_start.popleft()
            for neighbor, _ in graph[node_s.state]:
                if neighbor not in visited_start:
                    visited_start[neighbor] = Node(neighbor, node_s)
                    q_start.append(visited_start[neighbor])
                    count += 1

                    if neighbor in visited_goal:
                        return merge_paths(visited_start[neighbor], visited_goal[neighbor]), count

            # Backward
            node_g = q_goal.popleft()
            for neighbor, _ in graph[node_g.state]:
                if neighbor not in visited_goal:
                    visited_goal[neighbor] = Node(neighbor, node_g)
                    q_goal.append(visited_goal[neighbor])
                    count += 1

                    if neighbor in visited_start:
                        return merge_paths(visited_start[neighbor], visited_goal[neighbor]), count

    return None, count


def merge_paths(node1, node2):
    path1 = reconstruct_path(node1)
    path2 = reconstruct_path(node2)
    return path1 + path2[::-1][1:]


# -----------------------------
# MAIN
# -----------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage: python search.py <filename> <method>")
        return

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    coords, graph, start, goals = parse_file(filename)

    if method == "BFS":
        result, count = bfs(graph, start, goals)
    elif method == "DFS":
        result, count = dfs(graph, start, goals)
    elif method == "GBFS":
        result, count = gbfs(graph, start, goals, coords)
    elif method == "AS":
        result, count = astar(graph, start, goals, coords)
    elif method == "CUS1":
        result, count = ucs(graph, start, goals)
    elif method == "CUS2":
        result, count = bidirectional_bfs(graph, start, goals)
    else:
        print("Invalid method")
        return

    print(f"{filename} {method}")

    if result:
        path = reconstruct_path(result) if isinstance(result, Node) else result
        print(f"{path[-1]} {count}")
        print(" ".join(map(str, path)))
    else:
        print("No solution found")


if __name__ == "__main__":
    main()