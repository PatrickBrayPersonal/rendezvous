import json
import flatdict
import pandas as pd
from haversine import haversine, Unit


def priorities_to_objectives(priority_1, priority_2, p_df):
    p1_list = p_df[p_df["options"] == priority_1]["objective"].iloc[0]
    p2_list = p_df[p_df["options"] == priority_2]["objective"].iloc[0]

    objs = {p: 1 for p in p2_list if p[0] != "-"}
    objs.update({p[1:]: -1 for p in p2_list if p[0] == "-"})
    objs.update({p: 2 for p in p1_list if p[0] != "-"})
    objs.update({p[1:]: -2 for p in p1_list if p[0] == "-"})

    edge_obj = {"distance": 0}  # distance as a tiebreak
    if "distance" in objs:  # RN distance is the only edge objective
        edge_obj["distance"] = objs["distance"]
        del objs["distance"]
    print(edge_obj, objs)
    return edge_obj, objs


def create_type_df(biz_list: list, type_: str, type_order: int) -> pd.DataFrame:
    """
    Uses a businesses dictionary to create a dataframe that is usable by the optimizer
    """
    df = pd.DataFrame([flatdict.FlatDict(biz) for biz in biz_list])
    df.loc[:, "type"] = type_
    df.loc[:, "type_order"] = type_order
    return df


def create_nodes_df(biz_lists: list, types: list) -> pd.DataFrame:
    """
    Creates a single node dictionary of all businesses with specifed order

    biz_lists is a list of lists of dictionaries ordered by the business type order
    """
    nodes = [
        create_type_df(tup[0], tup[1], i) for i, tup in enumerate(zip(biz_lists, types))
    ]
    nodes = pd.concat(nodes).reset_index(drop=True)
    nodes.loc[:, "id"] = nodes.index
    return nodes


def create_edges_df(nodes: pd.DataFrame) -> pd.DataFrame:
    """
    Creates the links that can happen between businesses
    going in the specified type_order from the nodes dataframe
    """

    def apply_distance(x):
        dest_coord = (x["geometry:location:lat"], x["geometry:location:lng"])
        return haversine(source_coord, dest_coord, unit=Unit.MILES)

    edges = []
    for idx, row in nodes.iterrows():
        if row["type_order"] < nodes["type_order"].max():
            df = nodes[nodes["type_order"] == row["type_order"] + 1]
            df.loc[:, "source"] = row["id"]
            df.loc[:, "destination"] = df["id"]
            source_coord = (row["geometry:location:lat"], row["geometry:location:lng"])
            df.loc[:, "distance"] = df.apply(apply_distance, axis=1)
            df = remove_business_repeats(df, row)
            edges.append(df)
    df = pd.concat(edges).reset_index(drop=True)
    return df[["source", "destination", "distance"]]


def remove_business_repeats(df, row):
    return df[df["name"] != row["name"]]


def biz_lists_to_node_edge_dfs(biz_lists: list, types: list) -> pd.DataFrame:
    """
    generates the edge and node dataframes to be used by the CPSAT Solver
    Args:
        biz_lists: list of lists of places api data
            the inner lists are businesses of the same type
            the lists are in the order in which you wish to visit the businesses
        types: list of string of business types
    """
    nodes = create_nodes_df(biz_lists, types)
    edges = create_edges_df(nodes)
    return nodes, edges


def validate_inputs(biz_lists, types):
    missing_types = []
    n_types = []
    n_biz_lists = []
    for b, t in zip(biz_lists, types):
        if len(b) == 0:
            missing_types.append(t)
        else:
            n_types.append(t)
            n_biz_lists.append(b)
    if len(missing_types) > 0:
        message = f"{', '.join(missing_types)} not found in the area"
    else:
        message = "Optimization successful!"
    return n_biz_lists, n_types, message
