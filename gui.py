import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from search import run_search


METHODS = ["BFS", "DFS", "GBFS", "AS", "CUS1", "CUS2"]
NON_COST_METHODS = {"BFS", "DFS", "CUS1"}
CANVAS_WIDTH = 900
CANVAS_HEIGHT = 620
PADDING = 70
NODE_RADIUS = 18
AXIS_PAD_LEFT = 85
AXIS_PAD_RIGHT = 35
AXIS_PAD_TOP = 35
AXIS_PAD_BOTTOM = 70


class RouteGuidanceGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Traffic-Based Route Guidance System")
        self.root.geometry("1260x760")
        self.root.minsize(1120, 680)

        self.base_dir = Path(__file__).resolve().parent
        self.test_files = self._discover_test_files()
        self.current_result = None
        self.node_positions = {}

        self.selected_file = tk.StringVar(value="")
        self.selected_method = tk.StringVar(value="")

        self.status_text = tk.StringVar(value="Choose a test case and algorithm, then press Run Search.")
        self.goal_text = tk.StringVar(value="-")
        self.nodes_text = tk.StringVar(value="-")
        self.cost_text = tk.StringVar(value="-")
        self.path_text = tk.StringVar(value="-")

        self._build_styles()
        self._build_layout()

    def _discover_test_files(self):
        return sorted(path.name for path in self.base_dir.glob("TC*.txt"))

    def _build_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Root.TFrame", background="#f4f1ea")
        style.configure("Panel.TFrame", background="#e8e0d1")
        style.configure("CanvasWrap.TFrame", background="#f4f1ea")
        style.configure("Header.TLabel", background="#e8e0d1", foreground="#2c241b", font=("Segoe UI Semibold", 15))
        style.configure("Body.TLabel", background="#e8e0d1", foreground="#3b3228", font=("Segoe UI", 10))
        style.configure("Value.TLabel", background="#e8e0d1", foreground="#1d1812", font=("Consolas", 10))
        style.configure("Primary.TButton", font=("Segoe UI Semibold", 10))

    def _build_layout(self):
        self.root.configure(bg="#f4f1ea")

        container = ttk.Frame(self.root, style="Root.TFrame", padding=16)
        container.pack(fill="both", expand=True)
        container.columnconfigure(1, weight=1)
        container.rowconfigure(0, weight=1)

        control_panel = ttk.Frame(container, style="Panel.TFrame", padding=18)
        control_panel.grid(row=0, column=0, sticky="nsw", padx=(0, 16))

        canvas_panel = ttk.Frame(container, style="CanvasWrap.TFrame")
        canvas_panel.grid(row=0, column=1, sticky="nsew")
        canvas_panel.columnconfigure(0, weight=1)
        canvas_panel.rowconfigure(1, weight=1)

        ttk.Label(control_panel, text="TBRGS Research GUI", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            control_panel,
            text="Visualise route search behaviour across all assignment algorithms.",
            style="Body.TLabel",
            wraplength=260,
            justify="left",
        ).pack(anchor="w", pady=(6, 18))

        ttk.Label(control_panel, text="Test Case", style="Body.TLabel").pack(anchor="w")
        file_box = ttk.Combobox(
            control_panel,
            textvariable=self.selected_file,
            values=self.test_files,
            state="readonly",
            width=18,
        )
        file_box.pack(anchor="w", fill="x", pady=(4, 12))

        ttk.Label(control_panel, text="Algorithm", style="Body.TLabel").pack(anchor="w")
        method_box = ttk.Combobox(
            control_panel,
            textvariable=self.selected_method,
            values=METHODS,
            state="readonly",
            width=18,
        )
        method_box.pack(anchor="w", fill="x", pady=(4, 12))

        ttk.Button(control_panel, text="Run Search", style="Primary.TButton", command=self.run_search).pack(
            anchor="w", fill="x", pady=(0, 8)
        )
        ttk.Button(control_panel, text="Clear Path", command=self.clear_path).pack(anchor="w", fill="x", pady=(0, 18))

        ttk.Separator(control_panel).pack(fill="x", pady=(0, 18))

        ttk.Label(control_panel, text="Result", style="Header.TLabel").pack(anchor="w", pady=(0, 8))
        self._add_metric(control_panel, "Goal", self.goal_text)
        self._add_metric(control_panel, "Nodes Explored", self.nodes_text)
        self._add_metric(control_panel, "Path Cost", self.cost_text)

        ttk.Label(control_panel, text="Path", style="Body.TLabel").pack(anchor="w", pady=(12, 4))
        ttk.Label(
            control_panel,
            textvariable=self.path_text,
            style="Value.TLabel",
            wraplength=260,
            justify="left",
        ).pack(anchor="w", fill="x")

        ttk.Separator(control_panel).pack(fill="x", pady=(18, 18))
        ttk.Label(control_panel, text="Legend", style="Header.TLabel").pack(anchor="w", pady=(0, 8))
        for label in [
            "Blue: origin",
            "Red: destination",
            "Gold: computed path",
            "Dashed arrow: directed edge",
        ]:
            ttk.Label(control_panel, text=label, style="Body.TLabel", wraplength=260, justify="left").pack(anchor="w")

        title_frame = ttk.Frame(canvas_panel, style="CanvasWrap.TFrame")
        title_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        title_frame.columnconfigure(0, weight=1)

        self.title_label = ttk.Label(title_frame, text="Graph View", font=("Segoe UI Semibold", 16), background="#f4f1ea")
        self.title_label.grid(row=0, column=0, sticky="w")
        ttk.Label(
            title_frame,
            textvariable=self.status_text,
            background="#f4f1ea",
            foreground="#5b4c3d",
            font=("Segoe UI", 10),
        ).grid(row=1, column=0, sticky="w", pady=(4, 0))

        self.canvas = tk.Canvas(
            canvas_panel,
            width=CANVAS_WIDTH,
            height=CANVAS_HEIGHT,
            bg="#fbf8f2",
            highlightthickness=1,
            highlightbackground="#c9bba8",
        )
        self.canvas.grid(row=1, column=0, sticky="nsew")

    def _add_metric(self, parent, label, value_var):
        ttk.Label(parent, text=label, style="Body.TLabel").pack(anchor="w")
        ttk.Label(parent, textvariable=value_var, style="Value.TLabel").pack(anchor="w", pady=(2, 8))

    def run_search(self):
        filename = self.selected_file.get()
        method = self.selected_method.get()

        if not filename or not method:
            messagebox.showerror("Missing selection", "Select both a test case and an algorithm before running the search.")
            return

        try:
            self.current_result = run_search(str(self.base_dir / filename), method)
        except Exception as exc:
            messagebox.showerror("Search failed", str(exc))
            return

        self._update_summary()
        self._draw_graph()

    def clear_path(self):
        self.current_result = None
        self.goal_text.set("-")
        self.nodes_text.set("-")
        self.cost_text.set("-")
        self.path_text.set("-")
        self.title_label.configure(text="Graph View")
        self.status_text.set("Choose a test case and algorithm, then press Run Search.")
        self.canvas.delete("all")

    def _update_summary(self):
        result = self.current_result
        self.title_label.configure(text=f"Graph View: {Path(result['filename']).name} / {result['method']}")

        if result["found"]:
            self.goal_text.set(str(result["goal"]))
            self.nodes_text.set(str(result["count"]))
            if result["method"] in NON_COST_METHODS:
                self.cost_text.set("Not used")
            else:
                self.cost_text.set(str(result["path_cost"]))
            self.path_text.set(" -> ".join(map(str, result["path"])))
            self.status_text.set("Path found and highlighted on the graph.")
        else:
            self.goal_text.set("No solution")
            self.nodes_text.set(str(result["count"]))
            self.cost_text.set("-")
            self.path_text.set("No path found")
            self.status_text.set("No solution found for the selected search method.")

    def _draw_graph(self):
        if not self.current_result:
            return

        result = self.current_result
        coords = result["coords"]
        graph = result["graph"]
        origin = result["origin"]
        goals = set(result["goals"])
        path_edges = set()

        if result["path"]:
            path_edges = set(zip(result["path"], result["path"][1:]))

        self.canvas.delete("all")
        self.node_positions = self._scale_positions(coords)
        self._draw_axes(coords)

        for source, neighbors in graph.items():
            for target, cost in neighbors:
                x1, y1 = self.node_positions[source]
                x2, y2 = self.node_positions[target]
                highlight = (source, target) in path_edges
                reverse_exists = any(neighbor == source for neighbor, _ in graph.get(target, []))
                show_cost = result["method"] not in NON_COST_METHODS
                self._draw_directed_edge(source, target, x1, y1, x2, y2, cost, highlight, reverse_exists, show_cost)

        for node_id, (x, y) in self.node_positions.items():
            if node_id == origin:
                fill = "#2f80ed"
                outline = "#1e4d86"
            elif node_id in goals:
                fill = "#e45757"
                outline = "#872727"
            else:
                fill = "#f5efe4"
                outline = "#52463b"

            if result["path"] and node_id in result["path"]:
                outline = "#d99800"
                width = 4
            else:
                width = 2

            self.canvas.create_oval(
                x - NODE_RADIUS,
                y - NODE_RADIUS,
                x + NODE_RADIUS,
                y + NODE_RADIUS,
                fill=fill,
                outline=outline,
                width=width,
            )
            self.canvas.create_text(x, y, text=str(node_id), font=("Segoe UI Semibold", 10), fill="#1f1a15")

    def _scale_positions(self, coords):
        xs = [point[0] for point in coords.values()]
        ys = [point[1] for point in coords.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)
        usable_width = CANVAS_WIDTH - AXIS_PAD_LEFT - AXIS_PAD_RIGHT
        usable_height = CANVAS_HEIGHT - AXIS_PAD_TOP - AXIS_PAD_BOTTOM

        positions = {}
        for node_id, (x, y) in coords.items():
            scaled_x = AXIS_PAD_LEFT + ((x - min_x) / span_x) * usable_width
            scaled_y = CANVAS_HEIGHT - AXIS_PAD_BOTTOM - ((y - min_y) / span_y) * usable_height
            positions[node_id] = (scaled_x, scaled_y)

        return positions

    def _draw_axes(self, coords):
        xs = [point[0] for point in coords.values()]
        ys = [point[1] for point in coords.values()]

        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)

        left = AXIS_PAD_LEFT
        right = CANVAS_WIDTH - AXIS_PAD_RIGHT
        top = AXIS_PAD_TOP
        bottom = CANVAS_HEIGHT - AXIS_PAD_BOTTOM

        self.canvas.create_rectangle(left, top, right, bottom, outline="#ded3c4", width=1, fill="")
        self.canvas.create_line(left, bottom, right, bottom, fill="#5b4c3d", width=2)
        self.canvas.create_line(left, bottom, left, top, fill="#5b4c3d", width=2)

        self.canvas.create_text(
            (left + right) / 2,
            CANVAS_HEIGHT - 28,
            text="X coordinate",
            font=("Segoe UI", 10),
            fill="#4e4134",
        )
        self.canvas.create_text(
            28,
            (top + bottom) / 2,
            text="Y coordinate",
            angle=90,
            font=("Segoe UI", 10),
            fill="#4e4134",
        )

        for value in self._build_ticks(min_x, max_x):
            x = self._map_x(value, min_x, max_x)
            self.canvas.create_line(x, bottom, x, top, fill="#eee5d7", width=1)
            self.canvas.create_line(x, bottom, x, bottom + 6, fill="#5b4c3d", width=1)
            self.canvas.create_text(x, bottom + 20, text=str(value), font=("Consolas", 9), fill="#4e4134")

        for value in self._build_ticks(min_y, max_y):
            y = self._map_y(value, min_y, max_y)
            self.canvas.create_line(left, y, right, y, fill="#eee5d7", width=1)
            self.canvas.create_line(left - 6, y, left, y, fill="#5b4c3d", width=1)
            self.canvas.create_text(left - 24, y, text=str(value), font=("Consolas", 9), fill="#4e4134")

    def _build_ticks(self, minimum, maximum):
        if minimum == maximum:
            return [minimum]
        return list(range(minimum, maximum + 1))

    def _map_x(self, value, min_x, max_x):
        span_x = max(max_x - min_x, 1)
        usable_width = CANVAS_WIDTH - AXIS_PAD_LEFT - AXIS_PAD_RIGHT
        return AXIS_PAD_LEFT + ((value - min_x) / span_x) * usable_width

    def _map_y(self, value, min_y, max_y):
        span_y = max(max_y - min_y, 1)
        usable_height = CANVAS_HEIGHT - AXIS_PAD_TOP - AXIS_PAD_BOTTOM
        return CANVAS_HEIGHT - AXIS_PAD_BOTTOM - ((value - min_y) / span_y) * usable_height

    def _draw_directed_edge(self, source, target, x1, y1, x2, y2, cost, highlight, reverse_exists, show_cost):
        if reverse_exists:
            low, high = sorted((source, target))
            low_x, low_y = self.node_positions[low]
            high_x, high_y = self.node_positions[high]

            base_dx = high_x - low_x
            base_dy = high_y - low_y
            base_length = max((base_dx ** 2 + base_dy ** 2) ** 0.5, 1)
            ux = base_dx / base_length
            uy = base_dy / base_length
            nx = -uy
            ny = ux

            if source == low:
                start_cx, start_cy = low_x, low_y
                end_cx, end_cy = high_x, high_y
                bend_sign = 1
            else:
                start_cx, start_cy = high_x, high_y
                end_cx, end_cy = low_x, low_y
                bend_sign = -1

            start_x = start_cx + ux * NODE_RADIUS * (1 if source == low else -1) + nx * 12 * bend_sign
            start_y = start_cy + uy * NODE_RADIUS * (1 if source == low else -1) + ny * 12 * bend_sign
            end_x = end_cx - ux * NODE_RADIUS * (1 if source == low else -1) + nx * 12 * bend_sign
            end_y = end_cy - uy * NODE_RADIUS * (1 if source == low else -1) + ny * 12 * bend_sign

            mid_x = (start_cx + end_cx) / 2
            mid_y = (start_cy + end_cy) / 2
            control_x = mid_x + nx * 42 * bend_sign
            control_y = mid_y + ny * 42 * bend_sign
            label_x = mid_x + nx * 58 * bend_sign
            label_y = mid_y + ny * 58 * bend_sign
        else:
            dx = x2 - x1
            dy = y2 - y1
            length = max((dx ** 2 + dy ** 2) ** 0.5, 1)
            ux = dx / length
            uy = dy / length

            start_x = x1 + ux * NODE_RADIUS
            start_y = y1 + uy * NODE_RADIUS
            end_x = x2 - ux * NODE_RADIUS
            end_y = y2 - uy * NODE_RADIUS
            label_x = (start_x + end_x) / 2
            label_y = (start_y + end_y) / 2

        color = "#d99800" if highlight else "#7b6a58"
        width = 4 if highlight else 2
        dash = None if highlight else (6, 4)

        if reverse_exists:
            self.canvas.create_line(
                start_x,
                start_y,
                control_x,
                control_y,
                end_x,
                end_y,
                smooth=True,
                fill=color,
                width=width,
                arrow=tk.LAST,
                arrowshape=(12, 14, 4),
                dash=dash,
            )
        else:
            self.canvas.create_line(
                start_x,
                start_y,
                end_x,
                end_y,
                fill=color,
                width=width,
                arrow=tk.LAST,
                arrowshape=(12, 14, 4),
                dash=dash,
            )

        if show_cost:
            label_bg = "#fff3cd" if highlight else "#efe6d7"
            label = f"{source}->{target} ({cost})"
            label_width = max(34, 4 + len(label) * 4)
            self.canvas.create_rectangle(
                label_x - label_width,
                label_y - 10,
                label_x + label_width,
                label_y + 10,
                fill=label_bg,
                outline="",
            )
            self.canvas.create_text(label_x, label_y, text=label, font=("Consolas", 8), fill="#2a241c")


def main():
    root = tk.Tk()
    app = RouteGuidanceGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
