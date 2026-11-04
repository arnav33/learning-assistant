class GraphDict:
    def __init__(self, name, state, nodes, edges, conditional_edges):
        self.name = name
        self.state = state
        self.nodes = nodes
        self.edges = edges
        self.conditional_edges = conditional_edges