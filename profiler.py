def onSetupParameters(scriptOp):
    page = scriptOp.appendCustomPage('Profiler')
    p = page.appendOP('Targetcomp', label='Target COMP')
    p.default = '../project1'
    return


def onCook(scriptOp):
    """
    Called every frame or when Script CHOP cooks.
    Writes dataflow-sorted full traversal into scriptOp.text (viewer panel).
    """
    try:
        root_path = scriptOp.par['Targetcomp'].eval()
        root = op(root_path)
    except:
        scriptOp.text = "Error: Could not resolve 'Targetcomp' path."
        return

    if not root:
        scriptOp.text = f"Target COMP not found: '{root_path}'"
        return

    # Build dataflow graph and sort topologically
    graph, all_nodes = build_dataflow_graph(root)
    sorted_nodes = topo_sort(graph)

    # Traverse in sorted order
    result = ''
    for node in sorted_nodes:
        result += describe_node(node)

    scriptOp.text = result


def build_dataflow_graph(root):
    """
    Returns:
        graph: {node: [outputs]}
        all_nodes: [flat list of nodes]
    """
    graph = {}
    all_nodes = []

    def collect(op):
        for child in op.children:
            if child.name.startswith('_') or child.name.startswith('sys'):
                continue
            graph[child] = list(child.outputs)
            all_nodes.append(child)
            if hasattr(child, 'children') and child.children:
                collect(child)

    collect(root)
    return graph, all_nodes


def topo_sort(graph):
    """
    Topological sort for acyclic graph of nodes by dataflow.
    If cycles exist (e.g. feedback), they'll be skipped deterministically.
    """
    from collections import deque

    indegree = {node: 0 for node in graph}
    for node in graph:
        for out in graph[node]:
            if out in indegree:
                indegree[out] += 1

    queue = deque([n for n in graph if indegree[n] == 0])
    sorted_nodes = []

    visited = set()
    while queue:
        node = queue.popleft()
        if node in visited:
            continue
        visited.add(node)
        sorted_nodes.append(node)
        for out in graph.get(node, []):
            if out in indegree:
                indegree[out] -= 1
                if indegree[out] == 0:
                    queue.append(out)

    # Fallback: append unvisited nodes (e.g. in cycles)
    for node in graph:
        if node not in visited:
            sorted_nodes.append(node)

    return sorted_nodes


def describe_node(child, indent=0):
    """
    Describes a single node (type, parameters, connections).
    """
    output = ""
    tab = "    " * indent

    output += f"{tab}{child.name} (Type: {child.type}, Family: {child.family})\n"

    # First 5 lines of DAT content
    if child.family == 'DAT':
        lines = child.text.split('\n')
        for line in lines[:5]:
            output += f"{tab}    Content: {line}\n"
        if len(lines) > 5:
            output += f"{tab}    ... and more ...\n"

    # Parameters (skip COMP)
    if child.family != 'COMP':
        for par in child.pars():
            try:
                val = par.eval()
            except:
                val = "<error>"
            output += f"{tab}    {par.name}: {val}\n"

    # Input connections
    for inp in child.inputs:
        if inp:
            output += f"{tab}    ← Receives from: {inp.name} ({inp.family})\n"

    # Output connections
    for out in child.outputs:
        output += f"{tab}    → Feeds into: {out.name} ({out.family})\n"

    return output
