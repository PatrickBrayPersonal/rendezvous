"""
Runs an experiment on the runtimes with different node and edge counts
mlflow tutorial: https://mlflow.org/docs/latest/tutorials-and-examples/tutorial.html#training-the-model
"""
import mlflow as ml
from test_optimizer import random_graph
from rendez.cpsat_optimizer import optimize
import json

if __name__ == "__main__":
    ml.set_experiment(experiment_name="performance")
    for businesses in range(20, 90, 10):
        for types in range(2, 5):
            with ml.start_run():
                edges, nodes = random_graph(
                    ntypes=types,
                    nbusinesses=businesses,
                    edge_objectives={"distance"},
                    node_objectives={"rat_diff"},
                )
                ml.log_params(
                    {
                        "nodes": len(nodes),
                        "edges": len(edges),
                        "businesses": businesses,
                        "stops": types,
                    }
                )
                start_nodes = {0}
                end_nodes = set(nodes[nodes.type == types - 1].id)
                soln = optimize(
                    nodes,
                    edges,
                    start_nodes,
                    end_nodes,
                    edge_objectives={"distance": 1},
                    node_objectives={"rat_diff": 1},
                )
                print(json.dumps(soln, sort_keys=True, indent=4))
                del soln["edges"]
                ml.log_metrics(soln)
