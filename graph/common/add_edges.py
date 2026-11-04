from graph.common.node_name import node_name


def add_edges(graph, edges):
    for source, target in edges:
        graph.add_edge(node_name(source), node_name(target))
