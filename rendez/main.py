from rendez.preprocessing import biz_lists_to_node_edge_dfs
from rendez.cpsat_optimizer import optimize
from rendez.postprocessing import reformat_for_frontend


def run(
    biz_lists: list,
    type_list: list,
    edge_objectives: dict = dict(),
    node_objectives: dict = dict(),
):
    """
    Args:
        biz_lists: list of lists of places api data
            the inner lists are businesses of the same type
            the lists are in the order in which you wish to visit the businesses
        type_list: list of string of business types
        edge_objectives: dictionary of column names from nodes to minimize when selected, values are weights
        node_objectives: dictionary of column names from edges to minimize when selected, values are weights

    """
    nodes, edges = biz_lists_to_node_edge_dfs(biz_lists, type_list)
    """
    TODO: Do Scaling Here
    """
    start_nodes = {0}
    end_nodes = set(nodes[nodes["type_order"] == nodes["type_order"].max()]["id"])
    soln = optimize(
        nodes, edges, start_nodes, end_nodes, edge_objectives, node_objectives
    )
    selected_nodes = reformat_for_frontend(soln, nodes, edges)
    return selected_nodes
