from graph.common.node_name import node_name


def add_conditional_edges(graph, edges):
    for source, path, path_map in edges:
        if isinstance(path_map, dict):
            items = path_map.items()
        else:
            items = path_map
        resolved = {node_name(key): node_name(target) for key, target in items}
        graph.add_conditional_edges(node_name(source), path, resolved)
