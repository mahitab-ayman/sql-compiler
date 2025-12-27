"""
Visual Parse Tree Generator
Creates visual representations of parse trees using graphviz or ASCII art
"""

from parser import ParseTreeNode
import os


class ParseTreeVisualizer:
    """Visualizes parse trees"""
    
    def __init__(self):
        self.node_counter = 0
        self.node_ids = {}
    
    def visualize(self, parse_tree, output_file):
        """Generate visual parse tree using graphviz if available"""
        try:
            import graphviz
        except ImportError:
            raise ImportError("graphviz library not found. Install with: pip install graphviz")
        
        # Create graph
        dot = graphviz.Digraph(comment='Parse Tree', format='png')
        dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
        dot.attr('graph', rankdir='TB')
        
        # Build graph
        self._build_graph(dot, parse_tree, None)
        
        # Render
        dot.render(output_file, cleanup=True)
    
    def _build_graph(self, dot, node, parent_id):
        """Recursively build graph from parse tree"""
        if node is None:
            return
        
        # Create node label
        label = node.node_type
        if node.value:
            label += f"\\n{node.value}"
        if node.data_type:
            label += f"\\n[type: {node.data_type}]"
        if node.symbol_ref:
            label += f"\\n[ref: {node.symbol_ref}]"
        
        # Create unique node ID
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        
        # Add node to graph
        dot.node(node_id, label)
        
        # Connect to parent
        if parent_id:
            dot.edge(parent_id, node_id)
        
        # Process children
        for child in node.children:
            self._build_graph(dot, child, node_id)
    
    def print_ascii_tree(self, parse_tree):
        """Print ASCII art representation of parse tree"""
        print("\n" + "=" * 60)
        print("ASCII PARSE TREE VISUALIZATION")
        print("=" * 60 + "\n")
        
        if parse_tree:
            self._print_ascii_node(parse_tree, "", True, True)
        else:
            print("(Empty tree)")
        
        print("\n" + "=" * 60)
    
    def _print_ascii_node(self, node, prefix, is_last, is_root=False):
        """Recursively print ASCII tree"""
        if node is None:
            return
        
        # Determine connector
        if is_root:
            connector = ""
            new_prefix = prefix
        else:
            connector = "└── " if is_last else "├── "
            new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Build node label
        label = f"{node.node_type}"
        if node.value:
            label += f" ({node.value})"
        if node.data_type:
            label += f" [type: {node.data_type}]"
        if node.symbol_ref:
            label += f" [ref: {node.symbol_ref}]"
        
        print(prefix + connector + label)
        
        # Print children
        children = node.children
        for i, child in enumerate(children):
            is_last_child = (i == len(children) - 1)
            self._print_ascii_node(child, new_prefix, is_last_child)
    
    def export_to_dot(self, parse_tree, output_file):
        """Export parse tree to Graphviz DOT format"""
        lines = []
        lines.append("digraph ParseTree {")
        lines.append("  node [shape=box, style=rounded, fillcolor=lightblue];")
        lines.append("  rankdir=TB;")
        lines.append("")
        
        self.node_counter = 0
        self.node_ids = {}
        self._generate_dot(lines, parse_tree, None)
        
        lines.append("}")
        
        with open(output_file, 'w') as f:
            f.write('\n'.join(lines))
        
        print(f"DOT file saved to: {output_file}")
        print("To generate PNG, run: dot -Tpng {output_file} -o {output_file}.png")
    
    def _generate_dot(self, lines, node, parent_id):
        """Generate DOT format representation"""
        if node is None:
            return
        
        # Create node label
        label = node.node_type.replace('"', '\\"')
        if node.value:
            label += f"\\n{node.value.replace('"', '\\"')}"
        if node.data_type:
            label += f"\\n[type: {node.data_type}]"
        if node.symbol_ref:
            label += f"\\n[ref: {node.symbol_ref.replace('"', '\\"')}]"
        
        # Create unique node ID
        node_id = f"node_{self.node_counter}"
        self.node_counter += 1
        self.node_ids[id(node)] = node_id
        
        # Add node definition
        lines.append(f'  {node_id} [label="{label}"];')
        
        # Add edge to parent
        if parent_id:
            lines.append(f'  {parent_id} -> {node_id};')
        
        # Process children
        for child in node.children:
            self._generate_dot(lines, child, node_id)

