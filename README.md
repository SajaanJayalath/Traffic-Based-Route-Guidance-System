# Traffic-Based Route Guidance System (TBRGS)

A comprehensive implementation of multiple pathfinding algorithms for route guidance, designed as part of the Swinburne University Introduction to AI course.

## Overview

This project implements six different search algorithms to find optimal routes in a weighted, directed graph representing a traffic network. The system evaluates routes based on different optimization criteria: path cost, number of hops, or heuristic-based guidance.

## Project Structure

```text
Traffic Based Route Guidance System/
├── search.py
├── README.md
├── PathFinder-test.txt
├── TC01.txt
├── TC02.txt
├── TC03.txt
├── TC04.txt
├── TC05.txt
├── TC06.txt
├── TC07.txt
├── TC08.txt
├── TC09.txt
├── TC10.txt
├── TC11.txt
├── TC12.txt
├── TC13.txt
├── TC14.txt
├── TC15.txt
└── TEST_CASES_DESCRIPTION.txt
```

## Implemented Algorithms

### 1. BFS - Breadth-First Search (Uninformed)
- **Strategy**: Explores level by level using a FIFO queue
- **Optimality**: Fewest hops (tree depth), not necessarily lowest cost
- **Use Case**: Finding shortest path by number of moves
- **Tie-breaking**: Expands smaller node IDs first

### 2. DFS - Depth-First Search (Uninformed)
- **Strategy**: Explores as deep as possible before backtracking using a LIFO stack
- **Optimality**: No guarantee of optimal path
- **Use Case**: Finding any path quickly; memory-efficient
- **Tie-breaking**: Pushes nodes in descending order for correct expansion order

### 3. GBFS - Greedy Best-First Search (Informed)
- **Strategy**: Always expands the node closest to goal via heuristic function
- **Heuristic**: Euclidean distance to nearest goal
- **Optimality**: Fast but not guaranteed optimal
- **Use Case**: Quick approximations when optimality is not critical
- **Tie-breaking**: Smaller node number has priority

### 4. A* - A Star Search (Informed)
- **Strategy**: Combines actual cost `g(n)` and heuristic `h(n)`; expands `f(n) = g(n) + h(n)`
- **Heuristic**: Euclidean distance to nearest goal
- **Optimality**: Guaranteed optimal lowest-cost path
- **Use Case**: Finding lowest-cost routes with good efficiency
- **Tie-breaking**: Smaller node number has priority

### 5. CUS1 - Bidirectional BFS (Uninformed Custom)
- **Strategy**: Searches from the origin and the destination side at the same time
- **Optimality**: Finds a fewest-hops path, like BFS
- **Efficiency**: Often expands fewer states than one-direction BFS
- **Use Case**: Fast hop-based search across larger graphs
- **Tie-breaking**: Nodes expanded in ascending order

### 6. CUS2 - Bidirectional A* (Informed Custom)
- **Strategy**: Combines bidirectional search with heuristic guidance from both ends
- **Heuristic**: Euclidean distance to the nearest goal forward, and to the start backward
- **Optimality**: Cost-guided heuristic search with deterministic tie-breaking
- **Use Case**: Heuristic-driven custom search for route planning
- **Tie-breaking**: Equal-cost paths prefer the lexicographically smaller route

## Input File Format

Test case files follow this structure:

```text
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

### Example (`TC01.txt`)

```text
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
- `<test_file>`: Path to a test case file in the repository root, for example `TC01.txt`
- `<method>`: Search algorithm to use: `BFS`, `DFS`, `GBFS`, `AS`, `CUS1`, or `CUS2`

### Examples

```bash
python search.py TC01.txt BFS
python search.py TC11.txt AS
python search.py TC13.txt CUS2
```

### Output Format

**Successful path found:**

```text
<filename> <method>
<goal_node> <number_of_nodes>
<path as sequence: node1 node2 ... goalNode>
```

**No path exists:**

```text
<filename> <method>
No solution found
```

## Key Implementation Details

### Heuristic Function
- **Function**: Euclidean straight-line distance from a node to the nearest goal
- **Admissibility**: Never overestimates actual cost for A* and GBFS

### Path Reconstruction
- Tracks each visited node's parent
- Rebuilds the path from goal back to origin

### Tie-Breaking Rule
- When nodes have equal priority, smaller node IDs are expanded first
- This keeps behavior deterministic across test cases

### Node Counting
- `number_of_nodes` is the count of unique nodes encountered by the search
- Duplicate occurrences of the same node are not counted again
- This keeps the reported total aligned with the assignment output format

## Algorithm Comparison

| Algorithm | Type | Optimal | Heuristic | Speed | Best For |
|---|---|---|---|---|---|
| BFS | Uninformed | By hops | No | Medium | Fewest moves |
| DFS | Uninformed | No | No | Fast | Any path |
| GBFS | Informed | No | Yes | Very fast | Speed over optimality |
| A* | Informed | By cost | Yes | Fast | Optimal cost routes |
| CUS1 | Uninformed | By hops | No | Fast | Custom hop-based search |
| CUS2 | Informed | Heuristic-guided | Yes | Fast | Custom heuristic search |

## Test Suite Coverage

The project includes 15 test cases covering:

- Baseline mixed-edge graph
- Single linear paths
- Origin-destination identity
- Multiple destination handling
- Directed one-way edges
- Blocked reverse paths
- Mixed directed and bidirectional edges
- Unreachable destinations
- Disconnected graph components
- Tie-breaking by node number
- Cost vs. hop optimization
- A* vs GBFS optimality comparison
- Cyclic graphs
- Single-node graphs
- Deep chain path reconstruction

See [TEST_CASES_DESCRIPTION.txt](TEST_CASES_DESCRIPTION.txt) for detailed expectations.

## Requirements

- Python 3.6+
- Standard library only

## Development Context

This project was developed for the Introduction to AI course at Swinburne University and demonstrates:

- Core search algorithm implementation
- Uninformed vs informed search strategies
- Heuristic design
- Graph representation and traversal
- Performance comparison across algorithms

## Author

Created as a course assignment exploring fundamental AI search algorithms.

---

**Last Updated**: April 2026
