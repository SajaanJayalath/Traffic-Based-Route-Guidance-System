# Traffic-Based Route Guidance System (TBRGS)

A comprehensive implementation of multiple pathfinding algorithms for route guidance, designed as part of the Swinburne University Introduction to AI course.

## Overview

This project implements six different search algorithms to find optimal routes in a weighted, directed graph representing a traffic network. The system evaluates routes based on different optimization criteria: path cost, number of hops, or heuristic-based guidance.

## Project Structure

```
Traffic Based Route Guidance System/
├── search.py                          # Main implementation file
└── test_cases/                        # Comprehensive test suite
    ├── TC01_baseline.txt              # Baseline example (mixed edges)
    ├── TC02_linear_path.txt           # Single straight-line path
    ├── TC03_origin_is_destination.txt # Goal at origin
    ├── TC04_multiple_destinations.txt # Three destination nodes
    ├── TC05_directed_one_way.txt      # Strictly one-way edges
    ├── TC06_reverse_blocked.txt       # No reverse travel allowed
    ├── TC07_mixed_edges.txt           # Mixed directed/bidirectional
    ├── TC08_no_path.txt               # Unreachable destination
    ├── TC09_disconnected_graph.txt    # Separate graph components
    ├── TC10_tiebreaking.txt           # Node tie-breaking test
    ├── TC11_cost_vs_hops.txt          # Cost vs. hops optimization
    ├── TC12_astar_vs_gbfs.txt         # A* vs GBFS optimality
    ├── TC13_cycle.txt                 # Graph with cycles
    ├── TC14_single_node.txt           # Minimal graph (no edges)
    ├── TC15_deep_chain.txt            # Long path reconstruction
    ├── PathFinder-test.txt            # Additional test
    └── TEST_CASES_DESCRIPTION.txt     # Detailed test case documentation
```

## Implemented Algorithms

### 1. **BFS — Breadth-First Search** (Uninformed)
- **Strategy**: Explores level by level using a FIFO queue
- **Optimality**: Fewest hops (tree depth) — not necessarily lowest cost
- **Use Case**: Finding shortest path by number of moves
- **Tie-breaking**: Expands smaller node IDs first

### 2. **DFS — Depth-First Search** (Uninformed)
- **Strategy**: Explores as deep as possible before backtracking using a LIFO stack
- **Optimality**: No guarantee of optimal path
- **Use Case**: Finding any path quickly; memory-efficient
- **Tie-breaking**: Pushes nodes in descending order for correct expansion order

### 3. **GBFS — Greedy Best-First Search** (Informed)
- **Strategy**: Always expands the node closest to goal via heuristic function
- **Heuristic**: Euclidean distance to nearest goal
- **Optimality**: Fast but NOT guaranteed optimal
- **Use Case**: Quick approximations when optimality isn't critical
- **Tie-breaking**: Smaller node number has priority

### 4. **A* — A Star Search** (Informed)
- **Strategy**: Combines actual cost g(n) and heuristic h(n); expands f(n) = g(n) + h(n)
- **Heuristic**: Euclidean distance to nearest goal (admissible)
- **Optimality**: **Guaranteed optimal** (lowest cost) path
- **Use Case**: Finding lowest-cost routes with good efficiency
- **Tie-breaking**: Smaller node number has priority

### 5. **CUS1 — Uniform Cost Search** (Uninformed Custom)
- **Strategy**: Expands nodes by lowest accumulated path cost
- **Optimality**: **Guaranteed optimal** (lowest cost) path
- **Use Case**: Cost-driven optimization without heuristic guidance
- **Tie-breaking**: Smaller node ID has priority in tie-breaking

### 6. **CUS2 — Bidirectional BFS** (Informed Custom)
- **Strategy**: Searches simultaneously from origin AND all goal nodes
- **Optimality**: Fewest hops (like BFS)
- **Efficiency**: Much more efficient than BFS on large graphs
- **Use Case**: Finding shortest path when multiple goals exist
- **Tie-breaking**: Nodes expanded in ascending order

## Input File Format

Test case files follow this structure:

```
Nodes:
<node_id>: (<x>, <y>)
...

Edges:
(<from_id>, <to_id>): <cost>
...

Origin:
<starting_node_id>

Destinations:
<goal_1>; <goal_2>; ...
```

### Example (TC01_baseline.txt):
```
Nodes:
1: (4,1)
2: (2,2)
3: (4,4)
4: (6,3)
5: (5,6)
6: (7,5)

Edges:
(2,1): 4
(3,1): 5
(1,3): 5
...

Origin:
2

Destinations:
5; 4
```

## Usage

### Running the Search

```bash
python search.py <test_file> <method>
```

**Parameters:**
- `<test_file>`: Path to test case file (e.g., `test_cases/TC01_baseline.txt`)
- `<method>`: Search algorithm to use: `BFS`, `DFS`, `GBFS`, `AS`, `CUS1`, or `CUS2`

### Examples

```bash
python search.py test_cases/TC01_baseline.txt BFS
python search.py test_cases/TC11_cost_vs_hops.txt AS
python search.py test_cases/TC13_cycle.txt CUS2
```

### Output Format

**Successful path found:**
```
<filename> <method>
<goal_node> <nodes_created>
<path as sequence: node1 -> node2 -> ... -> goalNode>
```

**No path exists:**
```
<filename> <method>
No path found.
```

## Key Implementation Details

### Heuristic Function
- **Function**: Euclidean (straight-line) distance from node to nearest goal
- **Admissibility**: Never overestimates actual cost (valid for A* and GBFS)
- **Formula**: $h(n) = \min_{g \in goals} \sqrt{(x_g - x_n)^2 + (y_g - y_n)^2}$

### Path Reconstruction
- Maintains `came_from` dictionary tracking parent of each visited node
- Traces back from goal to origin, then reverses to get forward path

### Tie-Breaking Rule
- When nodes have equal priority, smaller node ID is expanded first
- Ensures deterministic behavior and consistent results across test cases

### Node Counting
- `nodes_created` tracks the number of nodes created/visited during search
- Used to evaluate algorithm efficiency

## Algorithm Comparison

| Algorithm | Type | Optimal | Heuristic | Speed | Best For |
|---|---|---|---|---|---|
| BFS | Uninformed | By hops | No | Medium | Fewest moves |
| DFS | Uninformed | No | No | Fast | Any path |
| GBFS | Informed | No | Yes | Very Fast | Speed > optimality |
| A* | Informed | By cost | Yes | Fast | Optimal cost routes |
| CUS1 | Uninformed | By cost | No | Medium | Cost optimization |
| CUS2 | Informed | By hops | Yes | Very Fast | Multiple destinations |

## Test Suite Coverage

The project includes **15 comprehensive test cases** covering:

✓ Baseline mixed-edge graph  
✓ Single linear paths  
✓ Origin-destination identity  
✓ Multiple destination handling  
✓ Directed one-way edges  
✓ Blocked reverse paths  
✓ Mixed directed/bidirectional edges  
✓ Unreachable destinations  
✓ Disconnected graph components  
✓ Tie-breaking by node number  
✓ Cost vs. hop optimization  
✓ A* vs GBFS optimality comparison  
✓ Cyclic graphs  
✓ Single-node graphs  
✓ Deep chain path reconstruction  

See [test_cases/TEST_CASES_DESCRIPTION.txt](test_cases/TEST_CASES_DESCRIPTION.txt) for detailed expectations.

## Implementation Highlights

### Efficient Data Structures
- **Heaps** (priority queues): For informed search algorithms (A*, GBFS, CUS1)
- **Deques**: For BFS and CUS2 (queue-based exploration)
- **Lists**: For DFS (stack-based exploration)
- **Dictionaries**: For graph adjacency lists and bookkeeping

### Edge Cases Handled
- Origin is a goal node (immediate return)
- No path exists (disconnected/unreachable destinations)
- Single-node graphs
- Cycles in the graph
- Graph with multiple destinations

### Performance Optimizations
- Bidirectional BFS (CUS2) reduces search space by up to $\sqrt{2}$
- Heuristic guidance (A*, GBFS) prunes search tree significantly
- Skip outdated heap entries to avoid redundant processing

## Requirements

- Python 3.6+
- Standard library only (no external dependencies)
  - `sys`
  - `math`
  - `collections` (deque)
  - `heapq`

## Development Context

This project is developed as part of the **Introduction to AI** course at **Swinburne University**, demonstrating:
- Core search algorithm implementation
- Uninformed vs. informed search strategies
- Heuristic function design
- Graph representation and traversal
- Performance analysis and algorithm comparison

## Author

Created as a course assignment exploring fundamental AI search algorithms.

---

**Last Updated**: April 2026
