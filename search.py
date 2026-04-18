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


def should_update_best_path(current_path, current_cost, candidate_path, candidate_cost):
    if candidate_path is None:
        return False
    if current_path is None or candidate_cost < current_cost:
        return True
    if candidate_cost > current_cost:
        return False
    return tuple(candidate_path) < tuple(current_path)


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
    seen_states = {start}
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
            if neighbor not in seen_states:
                seen_states.add(neighbor)
                count += 1

    return None, count


# -----------------------------
# BIDIRECTIONAL BFS (CUS1)
# -----------------------------
def bidirectional_bfs(graph, start, goals):
    reverse_graph = {node: [] for node in graph}
    for source, neighbors in graph.items():
        for neighbor, cost in neighbors:
            reverse_graph[neighbor].append((source, cost))

    if start in goals:
        return [start], 1

    q_start = deque([Node(start)])
    goal_nodes = {goal: Node(goal) for goal in sorted(goals)}
    q_goal = deque(goal_nodes[goal] for goal in sorted(goals))

    visited_start = {start: q_start[0]}
    visited_goal = goal_nodes.copy()
    seen_states = set(visited_start) | set(visited_goal)
    count = len(seen_states)

    while q_start and q_goal:
        node_s = q_start.popleft()
        for neighbor, _ in sorted(graph[node_s.state]):
            if neighbor not in visited_start:
                visited_start[neighbor] = Node(neighbor, node_s)
                q_start.append(visited_start[neighbor])
                if neighbor not in seen_states:
                    seen_states.add(neighbor)
                    count += 1

            if neighbor in visited_goal:
                return merge_paths(visited_start[neighbor], visited_goal[neighbor]), count

        node_g = q_goal.popleft()
        for neighbor, _ in sorted(reverse_graph[node_g.state]):
            if neighbor not in visited_goal:
                visited_goal[neighbor] = Node(neighbor, node_g)
                q_goal.append(visited_goal[neighbor])
                if neighbor not in seen_states:
                    seen_states.add(neighbor)
                    count += 1

            if neighbor in visited_start:
                return merge_paths(visited_start[neighbor], visited_goal[neighbor]), count

    return None, count


# -----------------------------
# GBFS
# -----------------------------
def gbfs(graph, start, goals, coords):
    pq = [(min_heuristic(start, goals, coords), Node(start))]
    visited = set()
    seen_states = {start}
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
            if neighbor not in seen_states:
                seen_states.add(neighbor)
                count += 1

    return None, count


# -----------------------------
# A*
# -----------------------------
def astar(graph, start, goals, coords):
    pq = [(0, Node(start, cost=0))]
    visited = {}
    seen_states = {start}

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
            if neighbor not in seen_states:
                seen_states.add(neighbor)
                count += 1

    return None, count


# -----------------------------
# BIDIRECTIONAL A* (CUS2)
# -----------------------------
def bidirectional_astar(graph, start, goals, coords):
    reverse_graph = {node: [] for node in graph}
    for source, neighbors in graph.items():
        for neighbor, cost in neighbors:
            reverse_graph[neighbor].append((source, cost))

    if start in goals:
        return [start], 1

    start_node = Node(start, cost=0)
    goal_nodes = {goal: Node(goal, cost=0) for goal in sorted(goals)}

    pq_start = [(min_heuristic(start, goals, coords), start_node)]
    pq_goal = [(heuristic(goal, start, coords), goal_nodes[goal]) for goal in sorted(goals)]
    heapq.heapify(pq_goal)

    best_start = {start: 0}
    best_goal = {goal: 0 for goal in goals}
    nodes_start = {start: start_node}
    nodes_goal = goal_nodes.copy()

    closed_start = {}
    closed_goal = {}
    best_path_cost = math.inf
    best_path = None

    seen_states = set(nodes_start) | set(nodes_goal)
    count = len(seen_states)

    while pq_start and pq_goal:
        if pq_start[0][0] <= pq_goal[0][0]:
            _, node_s = heapq.heappop(pq_start)
            if node_s.cost > best_start.get(node_s.state, math.inf):
                continue
            if node_s.state in closed_start and closed_start[node_s.state] <= node_s.cost:
                continue
            closed_start[node_s.state] = node_s.cost

            if node_s.state in best_goal:
                total_cost = node_s.cost + best_goal[node_s.state]
                candidate_path = merge_paths(node_s, nodes_goal[node_s.state])
                if should_update_best_path(best_path, best_path_cost, candidate_path, total_cost):
                    best_path_cost = total_cost
                    best_path = candidate_path

            for neighbor, edge_cost in sorted(graph[node_s.state]):
                g = node_s.cost + edge_cost
                if g < best_start.get(neighbor, math.inf):
                    next_node = Node(neighbor, node_s, g)
                    best_start[neighbor] = g
                    nodes_start[neighbor] = next_node
                    f = g + min_heuristic(neighbor, goals, coords)
                    heapq.heappush(pq_start, (f, next_node))
                    if neighbor not in seen_states:
                        seen_states.add(neighbor)
                        count += 1

                if neighbor in best_goal:
                    total_cost = g + best_goal[neighbor]
                    candidate_path = merge_paths(nodes_start[neighbor], nodes_goal[neighbor])
                    if should_update_best_path(best_path, best_path_cost, candidate_path, total_cost):
                        best_path_cost = total_cost
                        best_path = candidate_path
        else:
            _, node_g = heapq.heappop(pq_goal)
            if node_g.cost > best_goal.get(node_g.state, math.inf):
                continue
            if node_g.state in closed_goal and closed_goal[node_g.state] <= node_g.cost:
                continue
            closed_goal[node_g.state] = node_g.cost

            if node_g.state in best_start:
                total_cost = node_g.cost + best_start[node_g.state]
                candidate_path = merge_paths(nodes_start[node_g.state], node_g)
                if should_update_best_path(best_path, best_path_cost, candidate_path, total_cost):
                    best_path_cost = total_cost
                    best_path = candidate_path

            for neighbor, edge_cost in sorted(reverse_graph[node_g.state]):
                g = node_g.cost + edge_cost
                if g < best_goal.get(neighbor, math.inf):
                    next_node = Node(neighbor, node_g, g)
                    best_goal[neighbor] = g
                    nodes_goal[neighbor] = next_node
                    f = g + heuristic(neighbor, start, coords)
                    heapq.heappush(pq_goal, (f, next_node))
                    if neighbor not in seen_states:
                        seen_states.add(neighbor)
                        count += 1

                if neighbor in best_start:
                    total_cost = g + best_start[neighbor]
                    candidate_path = merge_paths(nodes_start[neighbor], nodes_goal[neighbor])
                    if should_update_best_path(best_path, best_path_cost, candidate_path, total_cost):
                        best_path_cost = total_cost
                        best_path = candidate_path

        min_forward = pq_start[0][0] if pq_start else math.inf
        min_backward = pq_goal[0][0] if pq_goal else math.inf
        if best_path is not None and min(min_forward, min_backward) > best_path_cost:
            return best_path, count

    return best_path, count


def merge_paths(node1, node2):
    path1 = reconstruct_path(node1)
    path2 = reconstruct_path(node2)
    return path1 + path2[::-1][1:]


def compute_path_cost(graph, path):
    if not path or len(path) == 1:
        return 0

    total = 0
    for current, nxt in zip(path, path[1:]):
        for neighbor, cost in graph[current]:
            if neighbor == nxt:
                total += cost
                break
        else:
            raise ValueError(f"Invalid path segment: {current} -> {nxt}")

    return total


def run_search(filename, method):
    method = method.upper()
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
        result, count = bidirectional_bfs(graph, start, goals)
    elif method == "CUS2":
        result, count = bidirectional_astar(graph, start, goals, coords)
    else:
        raise ValueError("Invalid method")

    if not result:
        return {
            "filename": filename,
            "method": method,
            "coords": coords,
            "graph": graph,
            "origin": start,
            "goals": goals,
            "found": False,
            "goal": None,
            "count": count,
            "path": None,
            "path_cost": None,
        }

    path = reconstruct_path(result) if isinstance(result, Node) else result
    return {
        "filename": filename,
        "method": method,
        "coords": coords,
        "graph": graph,
        "origin": start,
        "goals": goals,
        "found": True,
        "goal": path[-1],
        "count": count,
        "path": path,
        "path_cost": compute_path_cost(graph, path),
    }


# -----------------------------
# MAIN
# -----------------------------
def main():
    if len(sys.argv) != 3:
        print("Usage: python search.py <filename> <method>")
        return

    filename = sys.argv[1]
    method = sys.argv[2].upper()

    try:
        outcome = run_search(filename, method)
    except ValueError:
        print("Invalid method")
        return

    print(f"{filename} {method}")

    if outcome["found"]:
        print(f"{outcome['goal']} {outcome['count']}")
        print(" -> ".join(map(str, outcome["path"])))
    else:
        print("No solution found")


if __name__ == "__main__":
    main()
