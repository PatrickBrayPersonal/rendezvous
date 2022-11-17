from rendez.preprocessing import biz_lists_to_node_edge_dfs, priorities_to_objectives
from rendez.cpsat_optimizer import optimize
from rendez.postprocessing import reformat_for_frontend
from rendez.scaler import Scaler

import pandas as pd


def run(
    biz_lists: list,
    type_list: list,
    priority_1: str,
    priority_2: str,
    p_df: pd.DataFrame,
):
    """
    Args:
        biz_lists: list of lists of places api data
            the inner lists are businesses of the same type
            the lists are in the order in which you wish to visit the businesses
        type_list: list of string of business types

    """
    edge_obj, node_obj = priorities_to_objectives(priority_1, priority_2, p_df)
    nodes, edges = biz_lists_to_node_edge_dfs(biz_lists, type_list)
    scaler = Scaler()
    nodes, node_obj = scaler.scale(nodes, node_obj)
    edges, edge_obj = scaler.scale(edges, edge_obj)
    start_nodes = set(nodes[nodes["type_order"] == nodes["type_order"].min()]["id"])
    end_nodes = set(nodes[nodes["type_order"] == nodes["type_order"].max()]["id"])
    soln = optimize(nodes, edges, start_nodes, end_nodes, edge_obj, node_obj)
    print(soln)
    selected_nodes = reformat_for_frontend(soln, nodes, edges)
    return selected_nodes
