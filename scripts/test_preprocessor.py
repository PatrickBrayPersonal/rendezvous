import json
from rendez.preprocessing import biz_lists_to_node_edge_dfs
from rendez.cpsat_optimizer import optimize
from test_optimizer import assert_solution_valid
from rendez.postprocessing import reformat_for_frontend
from rendez.scaler import Scaler


def load_json(file):  # Loads Json file
    with open(file, errors="ignore") as jsonFile:
        jsonObject = json.load(jsonFile)
        jsonFile.close()
    return jsonObject


def test_preprocess_from_json():
    FILES = [
        "places_movie.json",
        "places_bar.json",
        "places_restaurants.json",
    ]  # test json files
    TYPES = ["start", "movie", "bar", "restaurant"]
    USER_NODE = [
        [
            {
                "geometry:location:lat": 38.919188013297024,
                "geometry:location:lng": -77.02494496019774,
            }
        ]
    ]  # the starting location
    node_objs = {"price_level": 2}
    edge_objs = {"distance": 3}

    file_contents = [load_json(f"test_data/{file}")["results"] for file in FILES]
    biz_lists = USER_NODE + file_contents

    nodes, edges = biz_lists_to_node_edge_dfs(biz_lists=biz_lists, types=TYPES)

    scaler = Scaler()
    nodes, node_objs = scaler.scale(nodes, node_objs)
    edges, edge_objs = scaler.scale(edges, edge_objs)

    start_nodes = {0}
    end_nodes = set(nodes[nodes["type_order"] == nodes["type_order"].max()]["id"])
    soln = optimize(
        nodes,
        edges,
        start_nodes,
        end_nodes,
        node_objectives=node_objs,
        edge_objectives=edge_objs,
    )
    assert_solution_valid(nodes, edges, soln["edges"], start_nodes, end_nodes)
    selected_nodes = reformat_for_frontend(soln, nodes, edges)
    print(selected_nodes)


if __name__ == "__main__":
    test_preprocess_from_json()
