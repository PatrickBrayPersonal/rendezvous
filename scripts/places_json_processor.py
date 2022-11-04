import json
import flatdict
import pandas as pd
from haversine import haversine, Unit



def create_business(business, number):  # Maps business data to a dictionary
    biz = {}
    biz["placeId"] = number
    biz["name"] = business["name"]
    # biz['type'] = mapped to user input
    biz["rating"] = business["rating"]
    biz["location"] = business["geometry"]["location"]
    return biz


def create_nodes(business, number):  # Maps business data to a dictionary for node data
    node = {}
    # Define Node
    node["rating"] = business["rating"]
    node["placeId"] = number
    # type defined from user input
    return node


def create_edge(
    previous_nodes, business, edges, number
):  # creates edges using the previous node values, and a business. It will add the edge to the current list of edges
    edge = {}
    for node in previous_nodes:
        edge["sourceId"] = node["placeId"]
        edge["targetId"] = number
        edge["rating"] = 5 - float(business["rating"])
        edges.append(edge)
    return edges


def og(files):

    businesses = [
        {
            "placeId": 1,
            "type": "user_node",
            "rating": False,
            "distance": False,
            "location": {"lat": 38, "lng": -77},
        }
    ]  # format of business list-dict structure and User data
    nodes = [
        {"placeId": 1, "type": "user_node", "rating": False}
    ]  # format for nodes list-dict structure and User data
    edges = []  # empty list to hold edges, passed in edges function and appended to
    previous_nodes = [
        {"placeId": 1, "type": "user_node", "rating": False}
    ]  # list to hold the nodes from the previous API call

    number = 2  # ID for nodes

    for file in files:
        jsonObject = load_json(f"test_data/{file}")
        prev_nodes = (
            []
        )  # empty list that will be populated with nodes from this loops run
        for business in jsonObject["results"]:  # loop through json results
            if (
                business["business_status"] != "OPERATIONAL"
            ):  # Check that the business is operating
                continue
            businesses.append(
                create_business(business, number)
            )  # appends businesses created from json object to the businesses list in the paremeters
            nodes.append(
                create_nodes(business, number)
            )  # appends nodes created from the json object to the nodes list in the paremeters
            prev_nodes.append(
                create_nodes(business, number)
            )  # maps nodes from this json object to the nodes list in the parameters
            create_edge(
                previous_nodes, business, edges, number
            )  # appends edges from the
            number += 1
        previous_nodes = (
            prev_nodes.copy()
        )  # overwrites the previous_nodes variable with the nodes from this loop run


def create_type_df(biz_list: list, type_: str, type_order: int) -> pd.DataFrame:
    """
    Uses a businesses dictionary to create a dataframe that is usable by the optimizer
    """
    df = pd.DataFrame([flatdict.FlatDict(biz) for biz in biz_list])
    df["type"] = type_
    df["type_order"] = type_order
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
    nodes["id"] = nodes.index
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
            df["source"] = row['id']
            df['destination'] = df['id']
            source_coord = (row["geometry:location:lat"], row["geometry:location:lng"])
            df['distance'] = df.apply(apply_distance, axis=1)
            edges.append(df)
    return pd.concat(edges).reset_index(drop=True)[["source", "destination", "distance"]]
            
def load_json(file):  # Loads Json file
    with open(file, errors="ignore") as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    return jsonObject

def biz_lists_to_node_edge_dfs(biz_lists: list, types: list) -> dict:
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
    return {"nodes": nodes, "edges": edges}

if __name__ == "__main__":
    FILES = [
        "places_movie.json",
        "places_bar.json",
        "places_restaurants.json",
    ]  # test json files
    TYPES = ["start", "movie", "bar", "restaurant"]
    USER_NODE = [
        [{"geometry:location:lat": 38.919188013297024, "geometry:location:lng": -77.02494496019774}]
    ]  # the starting location

    file_contents = [load_json(f"test_data/{file}")["results"] for file in FILES]
    biz_lists = USER_NODE + file_contents

    res = biz_lists_to_node_edge_dfs(biz_lists=biz_lists, types=TYPES)



    print('complete')
