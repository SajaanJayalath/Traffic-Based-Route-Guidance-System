# Traffic-Based Route Guidance System (TBRGS)

A Python implementation of multiple search algorithms for route guidance, developed for the Swinburne University Introduction to AI course.

## Overview

This project solves route-finding problems on a weighted, directed graph that represents a traffic network. It supports six search methods and includes both:

- a command-line interface for assignment-style runs
- a Tkinter GUI for research/demo visualisation

Different algorithms optimise for different criteria such as hop count, traversal order, or heuristic/cost guidance.

## Project Structure

```text
Traffic Based Route Guidance System/
|-- search.py
|-- gui.py
|-- README.md
|-- PathFinder-test.txt
|-- TC01.txt
|-- TC02.txt
|-- TC03.txt
|-- TC04.txt
|-- TC05.txt
|-- TC06.txt
|-- TC07.txt
|-- TC08.txt
|-- TC09.txt
|-- TC10.txt
|-- TC11.txt
|-- TC12.txt
|-- TC13.txt
|-- TC14.txt
`-- TEST_CASES_DESCRIPTION.txt
```

## Implemented Algorithms

### 1. BFS - Breadth-First Search
- Strategy: explores level by level using a FIFO queue
- Uses cost during search: no
- Best for: fewest-hop solutions

### 2. DFS - Depth-First Search
- Strategy: explores as deep as possible before backtracking using a LIFO stack
- Uses cost during search: no
- Best for: finding any path quickly with simple memory usage

### 3. GBFS - Greedy Best-First Search
- Strategy: expands the node with the best heuristic estimate to a goal
- Uses cost during search: heuristic only
- Best for: fast goal-directed search when strict optimality is not required

### 4. AS - A* Search
- Strategy: expands using `f(n) = g(n) + h(n)`
- Uses cost during search: yes
- Best for: lowest-cost routes with heuristic guidance

### 5. CUS1 - Bidirectional BFS
- Strategy: runs hop-based search from both ends
- Uses cost during search: no
- Best for: fewest-hop bidirectional search

### 6. CUS2 - Bidirectional A*
- Strategy: combines bidirectional expansion with heuristic guidance
- Uses cost during search: yes
- Best for: custom heuristic route planning

## Input File Format

Each test case file uses this format:

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

Example:

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

### Command Line

Run a search with:

```bash
python search.py <test_file> <method>
```

Parameters:

- `<test_file>`: a test case file such as `TC01.txt`
- `<method>`: `BFS`, `DFS`, `GBFS`, `AS`, `CUS1`, or `CUS2`

Examples:

```bash
python search.py TC01.txt BFS
python search.py TC11.txt AS
python search.py TC13.txt CUS2
```

Command-line output format:

Successful path:

```text
<filename> <method>
<goal_node> <number_of_nodes>
<node1> -> <node2> -> ... -> <goal_node>
```

No path:

```text
<filename> <method>
No solution found
```

### GUI

Launch the research GUI with:

```bash
python gui.py
```

GUI behaviour:

- starts blank with no graph displayed
- requires the user to select both a test case and an algorithm
- only updates after the user presses `Run Search`
- does not automatically rerun when selections change
- uses the input `(x, y)` coordinates to draw a Cartesian-style graph
- renders opposite directions separately when both edges exist between two nodes
- highlights the final route and displays the chosen goal, explored-node count, and path

Cost display in the GUI:

- `BFS`, `DFS`, and `CUS1` hide edge-cost labels because they do not use cost during search
- `GBFS`, `AS`, and `CUS2` show edge-cost labels

## Key Implementation Details

### Heuristic
- Euclidean straight-line distance to the nearest goal
- Used by `GBFS`, `AS`, and `CUS2`

### Path Reconstruction
- Each node stores its parent
- The final path is rebuilt from the goal back to the origin

### Cost Handling
- `BFS`, `DFS`, and `CUS1` ignore edge cost when choosing which node to expand
- `GBFS`, `AS`, and `CUS2` use heuristic and/or cost information during search
- The project can still compute and report the final path cost after a path is found

### Tie-Breaking
- When priorities are equal, smaller node IDs are preferred
- This keeps results deterministic across test cases

### Node Counting
- `number_of_nodes` is the count of unique nodes encountered by the search
- Duplicate encounters are not counted again

## Test Suite Coverage

The repository includes 15 test cases covering:

- baseline mixed-edge graphs
- single linear paths
- origin equals destination
- multiple destinations
- one-way directed edges
- blocked reverse paths
- mixed directed and bidirectional edges
- unreachable destinations
- disconnected graph components
- tie-breaking by node number
- DFS traversal-order contrast
- A* vs GBFS comparison
- cyclic graphs
- single-node graphs
- deep-chain path reconstruction

See [TEST_CASES_DESCRIPTION.txt](TEST_CASES_DESCRIPTION.txt) for detailed expected results.

## Requirements

- Python 3.6+
- standard library only
- Tkinter available in the local Python installation for the GUI

## Development Context

This project demonstrates:

- graph parsing
- uninformed and informed search
- heuristic design
- deterministic tie-breaking
- route visualisation on coordinate-based graphs

## Author

Created as a course assignment exploring fundamental AI search algorithms.

---

**Last Updated**: April 2026
