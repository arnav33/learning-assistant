from graph.common.node_name import node_name


def add_nodes(graph, nodes):
    for fn in nodes:
        graph.add_node(node_name(fn), fn)
