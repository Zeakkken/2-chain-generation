"""Graph generation and visualization from Appendix A of my USC thesis."""

import matplotlib.pyplot as plt
import networkx as nx


def initialize_base_graph():
    G = nx.Graph()
    G.add_node(1, pos=(1, 1))
    G.add_node(2, pos=(2, 1))
    G.add_node(3, pos=(1, 2))
    G.add_edges_from([(1, 3)])
    return G


def get_node_by_pos(graph, pos):
    for node, p in nx.get_node_attributes(graph, 'pos').items():
        if p == pos:
            return node
    return None


def get_node_directly_below(graph, a, k):
    node_of_interest = get_node_by_pos(graph, (a, k))
    if node_of_interest is None:
        return None

    for i in range(k - 1, 0, -1):
        node_below = get_node_by_pos(graph, (a, i))
        if node_below and graph.has_edge(node_of_interest, node_below):
            return node_below
    return None


def add_vertex_left_corrected(graph, k, j):
    G_new = graph.copy()
    n = max(G_new.nodes) + 1

    if k > j:
        G_new.add_node(n, pos=(1, k + 1))
        below_node = get_node_by_pos(G_new, (1, k))
        if below_node is not None:
            G_new.add_edge(n, below_node)
        k = k + 1
    elif k < j:
        G_new.add_node(n, pos=(1, j))
        below_node = get_node_by_pos(G_new, (1, k))
        if below_node is not None:
            G_new.add_edge(n, below_node)
        right_node = get_node_directly_below(G_new, 2, j)
        if right_node is not None:
            G_new.add_edge(n, right_node)
        k = j
    else:
        G_new.add_node(n, pos=(1, k + 1))
        below_node = get_node_by_pos(G_new, (1, k))
        if below_node is not None:
            G_new.add_edge(n, below_node)
        right_node = get_node_directly_below(G_new, 2, j)
        if right_node and not G_new.has_edge(below_node, right_node):
            G_new.add_edge(n, right_node)
        k = k + 1

    return G_new, k, j


def add_vertex_right_corrected(graph, k, j):
    G_new = graph.copy()
    n = max(G_new.nodes) + 1

    if k < j:
        G_new.add_node(n, pos=(2, j + 1))
        below_node = get_node_by_pos(G_new, (2, j))
        if below_node is not None:
            G_new.add_edge(n, below_node)
        j = j + 1
    elif k > j:
        G_new.add_node(n, pos=(2, k))
        below_node = get_node_by_pos(G_new, (2, j))
        if below_node is not None:
            G_new.add_edge(n, below_node)
        left_node = get_node_directly_below(G_new, 1, k)
        if left_node is not None:
            G_new.add_edge(n, left_node)
        j = k
    else:
        G_new.add_node(n, pos=(2, j + 1))
        below_node = get_node_by_pos(G_new, (2, j))
        if below_node is not None:
            G_new.add_edge(n, below_node)
        left_node = get_node_directly_below(G_new, 1, k)
        if left_node and not G_new.has_edge(below_node, left_node):
            G_new.add_edge(n, left_node)
        j = j + 1

    return G_new, k, j


def generate_graphs(n):
    base_graph = initialize_base_graph()
    graphs = {3: [(base_graph, 2, 1)]}
    for num_vertices in range(4, n + 1):
        graphs[num_vertices] = []
        for graph, k, j in graphs[num_vertices - 1]:
            graphs[num_vertices].append(add_vertex_left_corrected(graph, k, j))
            graphs[num_vertices].append(add_vertex_right_corrected(graph, k, j))
    return graphs


def draw_graphs_in_row(graphs, n):
    total_graphs = len(graphs[n])
    fig, axs = plt.subplots(1, total_graphs, figsize=(5 * total_graphs, 5))
    if total_graphs == 1:
        axs = [axs]

    for i, (graph, k, j) in enumerate(graphs[n]):
        ax = axs[i]
        pos = nx.get_node_attributes(graph, 'pos')
        nx.draw(
            graph, pos, ax=ax, with_labels=True, node_size=700,
            node_color='lightblue', font_weight='bold',
        )
        ax.set_title(f'Graph {i + 1}')

    plt.tight_layout()
    plt.show()

def generate_posets():
    from itertools import combinations, product

    left = ("L1", "L2", "L3")
    right = ("R1", "R2", "R3")
    cross_pairs = list(product(left, right))
    chain_relations = list(combinations(left, 2)) + list(combinations(right, 2))

    # Each cross pair is incomparable (0), L < R (1), or R < L (-1).
    for choices in product((0, 1, -1), repeat=len(cross_pairs)):
        order = nx.DiGraph(chain_relations)

        for (left_node, right_node), choice in zip(cross_pairs, choices):
            if choice == 1:
                order.add_edge(left_node, right_node)
            elif choice == -1:
                order.add_edge(right_node, left_node)

        if not nx.is_directed_acyclic_graph(order):
            continue

        closure = nx.transitive_closure_dag(order)
        if closure.number_of_edges() == order.number_of_edges():
            yield nx.transitive_reduction(order)

if __name__ == "__main__":
    from itertools import islice

    graphs = list(islice(generate_posets(), 5))
    fig, axes = plt.subplots(2, 3, figsize=(9, 6))

    for ax in axes.flat:
        ax.set_axis_off()

    for number, (ax, graph) in enumerate(zip(axes.flat, graphs), start=1):
        # Place larger elements higher and keep L and R in separate columns.
        heights = {
            node: level
            for level, nodes in enumerate(nx.topological_generations(graph))
            for node in nodes
        }
        positions = {
            node: (int(node.startswith("R")), heights[node])
            for node in graph
        }

        nx.draw_networkx(
            graph, positions, ax=ax, arrows=False,
            node_size=600, node_color="#bbe0f0",
        )
        ax.set_title(f"Graph {number}")
        ax.margins(0.25)

    fig.tight_layout()
    fig.savefig("first-five-2-chains.png", dpi=150, bbox_inches="tight")
    plt.show()