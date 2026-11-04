def node_name(node):
    return node if isinstance(node, str) else node.__name__