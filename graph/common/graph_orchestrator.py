from langgraph.graph import StateGraph

from graph.common.add_conditional_edges import add_conditional_edges
from graph.common.add_edges import add_edges
from graph.common.add_nodes import add_nodes


graphs = {}


class GraphBuilder:
    def __init__(self, name: str | None = None):
        self._name = name
        self._state = None
        self._nodes = []
        self._edges = []
        self._conditional_edges = []

    @classmethod
    def builder(cls, name: str | None = None):
        return cls(name)

    def name(self, name: str):
        self._name = name
        return self

    def state(self, state):
        self._state = state
        return self

    def nodes(self, nodes):
        self._nodes = nodes
        return self

    def edges(self, edges):
        self._edges = edges
        return self

    def conditional_edges(self, conditional_edges):
        self._conditional_edges = conditional_edges
        return self

    def build(self):
        if not self._name:
            raise ValueError("Graph is missing name")
        if self._state is None:
            raise ValueError(f"Graph '{self._name}' is missing state")
        if self._name in graphs:
            return graphs[self._name]

        graph = StateGraph(self._state)
        add_nodes(graph, self._nodes)
        add_edges(graph, self._edges)
        add_conditional_edges(graph, self._conditional_edges)
        compiled_graph = graph.compile()
        graphs[self._name] = compiled_graph
        return compiled_graph


# Backwards-compatible alias
GraphOrchestrator = GraphBuilder
