"""
Graphical Parse Tree Visualizer
Draws parse trees as actual tree diagrams using Tkinter Canvas
"""

import tkinter as tk
from tkinter import ttk


class GraphicalTreeVisualizer:
    """Draws parse trees graphically"""

    def __init__(self, canvas):
        self.canvas = canvas
        self.node_width = 120
        self.node_height = 30
        self.level_height = 80
        self.padding = 10

    def draw_tree(self, tree):
        """Draw the parse tree on canvas"""
        if not tree:
            return

        # Clear canvas
        self.canvas.delete("all")

        # Calculate tree dimensions
        self.positions = {}
        self.calculate_positions(tree, 0, 0)

        # Adjust to center
        if self.positions:
            min_x = min(pos[0] for pos in self.positions.values())
            max_x = max(pos[0] for pos in self.positions.values())
            max_y = max(pos[1] for pos in self.positions.values())

            # Center horizontally
            canvas_width = max_x - min_x + 200
            canvas_height = max_y + 100

            # Configure canvas size
            self.canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

            offset_x = 100 - min_x
            offset_y = 50

            # Draw connections first (so they appear behind nodes)
            self.draw_connections(tree, offset_x, offset_y)

            # Draw nodes
            self.draw_nodes(tree, offset_x, offset_y)

    def calculate_positions(self, node, level, h_pos):
        """Calculate positions for all nodes"""
        if not node:
            return 0

        # Calculate positions for children first
        if hasattr(node, 'children') and node.children:
            child_positions = []
            current_pos = h_pos

            for child in node.children:
                child_width = self.calculate_positions(child, level + 1, current_pos)
                child_positions.append((current_pos, child_width))
                current_pos += child_width + self.padding

            # Position this node centered above children
            first_child_center = child_positions[0][0] + child_positions[0][1] / 2
            last_child_center = child_positions[-1][0] + child_positions[-1][1] / 2
            node_x = (first_child_center + last_child_center) / 2
            total_width = current_pos - h_pos
        else:
            # Leaf node
            node_x = h_pos + self.node_width / 2
            total_width = self.node_width

        node_y = level * self.level_height
        self.positions[id(node)] = (node_x, node_y)

        return total_width

    def draw_connections(self, node, offset_x, offset_y):
        """Draw lines connecting parent to children"""
        if not node or not hasattr(node, 'children'):
            return

        node_id = id(node)
        if node_id not in self.positions:
            return

        parent_x, parent_y = self.positions[node_id]
        parent_x += offset_x
        parent_y += offset_y + self.node_height

        for child in node.children:
            child_id = id(child)
            if child_id in self.positions:
                child_x, child_y = self.positions[child_id]
                child_x += offset_x
                child_y += offset_y

                # Draw line
                self.canvas.create_line(
                    parent_x, parent_y,
                    child_x, child_y,
                    fill="#666", width=2, tags="connection"
                )

                # Recursively draw children's connections
                self.draw_connections(child, offset_x, offset_y)

    def draw_nodes(self, node, offset_x, offset_y):
        """Draw all nodes as rectangles with text"""
        if not node:
            return

        node_id = id(node)
        if node_id not in self.positions:
            return

        x, y = self.positions[node_id]
        x += offset_x
        y += offset_y

        # Determine node color based on type
        color = self.get_node_color(node.node_type)

        # Draw rectangle
        x1 = x - self.node_width / 2
        y1 = y
        x2 = x + self.node_width / 2
        y2 = y + self.node_height

        rect = self.canvas.create_rectangle(
            x1, y1, x2, y2,
            fill=color, outline="#333", width=2,
            tags="node"
        )

        # Draw node type
        text = node.node_type
        if node.value:
            text += f"\n({node.value})"

        self.canvas.create_text(
            x, y + self.node_height / 2,
            text=text,
            font=("Arial", 8, "bold"),
            tags="text"
        )

        # Draw children
        if hasattr(node, 'children'):
            for child in node.children:
                self.draw_nodes(child, offset_x, offset_y)

    def get_node_color(self, node_type):
        """Get color for node type"""
        colors = {
            'PROGRAM': '#E8F4F8',
            'STATEMENT': '#D4E6F1',
            'CREATE_TABLE': '#A9CCE3',
            'INSERT': '#A9DFBF',
            'SELECT': '#F9E79F',
            'UPDATE': '#FAD7A0',
            'DELETE': '#F5B7B1',
            'IDENTIFIER': '#D7BDE2',
            'KEYWORD': '#85C1E2',
            'LITERAL': '#F8BBD0',
            'DATA_TYPE': '#C5E1A5',
            'OPERATOR': '#FFE082',
            'DELIMITER': '#E0E0E0',
            'ERROR': '#FFCDD2',
            'SUCCESS': '#C8E6C9',
        }
        return colors.get(node_type, '#FFFFFF')


class TreeVisualizerWindow:
    """Popup window for tree visualization"""

    def __init__(self, parent, tree, title="Parse Tree Visualization"):
        self.window = tk.Toplevel(parent)
        self.window.title(title)
        self.window.geometry("1000x700")

        # Create frame with canvas and scrollbars
        frame = ttk.Frame(self.window)
        frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create canvas with scrollbars
        self.canvas = tk.Canvas(frame, bg="white")

        h_scroll = ttk.Scrollbar(frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        v_scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.canvas.yview)

        self.canvas.configure(xscrollcommand=h_scroll.set, yscrollcommand=v_scroll.set)

        # Grid layout
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        v_scroll.grid(row=0, column=1, sticky=(tk.N, tk.S))
        h_scroll.grid(row=1, column=0, sticky=(tk.W, tk.E))

        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(0, weight=1)

        # Buttons
        btn_frame = ttk.Frame(self.window)
        btn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(btn_frame, text="Zoom In", command=self.zoom_in).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Zoom Out", command=self.zoom_out).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Reset Zoom", command=self.reset_zoom).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Close", command=self.window.destroy).pack(side=tk.RIGHT, padx=2)

        # Visualizer
        self.visualizer = GraphicalTreeVisualizer(self.canvas)
        self.zoom_level = 1.0

        # Draw tree
        if tree:
            self.visualizer.draw_tree(tree)

        # Mouse wheel zoom
        self.canvas.bind("<MouseWheel>", self.on_mousewheel)
        self.canvas.bind("<Button-4>", self.on_mousewheel)  # Linux
        self.canvas.bind("<Button-5>", self.on_mousewheel)  # Linux

    def zoom_in(self):
        """Zoom in"""
        self.zoom_level *= 1.2
        self.canvas.scale("all", 0, 0, 1.2, 1.2)
        self.update_scrollregion()

    def zoom_out(self):
        """Zoom out"""
        self.zoom_level /= 1.2
        self.canvas.scale("all", 0, 0, 1/1.2, 1/1.2)
        self.update_scrollregion()

    def reset_zoom(self):
        """Reset zoom to 1.0"""
        scale = 1.0 / self.zoom_level
        self.canvas.scale("all", 0, 0, scale, scale)
        self.zoom_level = 1.0
        self.update_scrollregion()

    def on_mousewheel(self, event):
        """Handle mouse wheel for zoom"""
        if event.num == 5 or event.delta < 0:
            self.zoom_out()
        else:
            self.zoom_in()

    def update_scrollregion(self):
        """Update scroll region after zoom"""
        bbox = self.canvas.bbox("all")
        if bbox:
            self.canvas.configure(scrollregion=bbox)
