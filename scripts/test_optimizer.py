import pandas as pd
from rendez import cpsat_optimizer
import json
import random


def test_small():
    edges = pd.read_csv("test_data/test_edges.csv")
    nodes = pd.read_csv("test_data/test_nodes.csv")
    start_nodes = {0}
    end_nodes = {5, 6}
    soln = cpsat_optimizer.optimize(
        nodes,
        edges,
        start_nodes,
        end_nodes,
        edge_objectives={"distance"},
        node_objectives={"rating_diff"},
    )
    print(json.dumps(soln, sort_keys=True, indent=4))
    assert_solution_valid(nodes, edges, soln["edges"], start_nodes, end_nodes)


def test_big():
    """
    Tests the solution on a larger graph to measure performance
    """
    ntypes = 3
    nbusinesses = 10
    edges, nodes = random_graph(
        ntypes=ntypes,
        nbusinesses=nbusinesses,
        edge_objectives={"distance"},
        node_objectives={"rating_diff"},
    )
    start_nodes = {0}
    end_nodes = set(nodes[nodes.type == ntypes - 1].id)
    soln = cpsat_optimizer.optimize(
        nodes,
        edges,
        start_nodes,
        end_nodes,
        edge_objectives={"distance"},
        node_objectives={"rating_diff"},
    )
    print(json.dumps(soln, sort_keys=True, indent=4))
    assert_solution_valid(nodes, edges, soln["edges"], start_nodes, end_nodes)


def get_dest_list(ntypes, nbusinesses):
    target_list = list(range(1, nbusinesses + 1))
    for i in range(1, ntypes):
        target_list += (
            list(range(nbusinesses * i + 1, nbusinesses * i + nbusinesses + 1))
            * nbusinesses
        )
    return target_list


def random_graph(ntypes, nbusinesses, edge_objectives=set, node_objectives=set):
    """
    creates a random graph of the same structure as the test data
    however the number of types and number of businesses at each type are variable
    """
    nodes = pd.DataFrame()
    nnodes = ntypes * nbusinesses + 1
    nodes["id"] = range(nnodes)
    nodes["type"] = ["start"] + sorted(list(range(ntypes)) * nbusinesses)
    for obj in node_objectives:
        nodes[obj] = [random.randint(0, 10) for i in range(nnodes)]

    nedges = nbusinesses**2 * (ntypes - 1) + nbusinesses
    edges = pd.DataFrame()
    edges["source"] = sorted(
        list(range(0, (ntypes - 1) * nbusinesses + 1)) * nbusinesses
    )
    edges["destination"] = get_dest_list(ntypes, nbusinesses)
    for obj in edge_objectives:
        edges[obj] = [random.randint(0, 10) for i in range(nedges)]

    return edges, nodes


def assert_solution_valid(nodes, edges, soln, start_nodes, end_nodes):
    sources = set([s[0] for s in soln])
    dests = set([s[1] for s in soln])
    # C1: Continuity Constraint
    assert len(soln) == len(nodes["type"].unique()) - 1, "Solution length incorrect"
    # C2: Starting Constraint
    assert (
        len(start_nodes.intersection(sources - dests)) == 1
    ), "Starting/Continuity constraint violated"
    # C3: Ending Constraint
    assert (
        len(end_nodes.intersection(dests - sources)) == 1
    ), "Ending/Continuity constraint violated"


if __name__ == "__main__":
    test_small()
    test_big()
