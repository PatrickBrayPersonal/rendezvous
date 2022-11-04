"""
Optimizer uses OR-Tools CP-SAT solver for constraint programming
"""

import pandas as pd
from ortools.sat.python import cp_model
from collections import defaultdict


def optimize(
    nodes: pd.DataFrame,
    edges: pd.DataFrame,
    start_nodes: set,
    end_nodes: set,
    edge_objectives: dict = dict(),
    node_objectives: dict = dict(),
) -> dict:
    """
    Optimize for objectives
    NOTE: all objective values must be integers
    Args:
        nodes: Dataframe of nodes and attributes
        edges: Dataframe of edges, 'source' and 'destination'
        starting_nodes: set of eligble starting nodes
        ending_nodes: set of eligible ending nodes
        edge_objectives: dictionary of column names from nodes to minimize when selected, values are weights
        node_objectives: dictionary of column names from edges to minimize when selected, values are weights
    Return:
        solution dict
        {
            "objective" : solution cost
            "edges" : edges selected
            "time" : wall clock time to solution
        }

    """
    model = cp_model.CpModel()
    edge_vars = {}
    node_vars = {}
    edge_obj_vars = defaultdict(dict)
    node_obj_vars = defaultdict(dict)

    # Populate Boolean Edge Variables
    edges.apply(add_edge_vars, args=(model, edge_vars), axis=1)
    # Populate Objective Variables and Constants
    edges.apply(
        add_edge_objective_vars,
        args=(model, edge_vars, edge_objectives, edge_obj_vars),
        axis=1,
    )

    nodes[~nodes["id"].isin(start_nodes)].apply(
        add_node_objective_vars,
        args=(
            model,
            edge_vars,
            node_vars,
            node_objectives,
            node_obj_vars,
        ),
        axis=1,
    )

    # C1: Continuity Constraint
    for i in set(nodes["id"]) - start_nodes - end_nodes:
        model.Add(
            cp_model.LinearExpr.Sum(
                [edge for key, edge in edge_vars.items() if key[0] == i]
            )
            == cp_model.LinearExpr.Sum(
                [edge for key, edge in edge_vars.items() if key[1] == i]
            )
        )
    # C2: Starting Constraint
    model.Add(
        cp_model.LinearExpr.Sum(
            [edge for key, edge in edge_vars.items() if key[0] in start_nodes]
        )
        == 1
    )
    # C3: Ending Constraint
    model.Add(
        cp_model.LinearExpr.Sum(
            [edge for key, edge in edge_vars.items() if key[1] in end_nodes]
        )
        == 1
    )
    # Objective
    edge_loss = sum(
        [
            sum(edge_obj_vars[obj].values()) * weight
            for obj, weight in edge_objectives.items()
        ]
    )
    node_loss = sum(
        [
            sum(node_obj_vars[obj].values()) * weight
            for obj, weight in node_objectives.items()
        ]
    )
    model.Minimize(edge_loss + node_loss)
    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        print("Model sucessful")
        return get_soln_dict(solver, edge_vars)
    else:
        print(f"Model failed with error code {status}")
        return None


def add_edge_vars(row, model, edge_vars):
    """
    populates an edge_vars dict with the or-tools variables
    """
    name = str(row["source"]) + "_" + str(row["destination"])
    edge_var = model.NewBoolVar(name)
    edge_vars[row["source"], row["destination"]] = edge_var


def add_node_objective_vars(
    row,
    model,
    edge_vars: dict,
    node_vars: dict,
    node_objectives: set,
    node_obj_vars: dict,
):
    """
    Populates node_obj_vars dict with or-tools objective variables

    Args:
        node_objectives: List of column names from row
        node_obj_vars: dict of objective vars, 0 if node not visited (objective) if visited
    """
    node_var = model.NewBoolVar(f"{row['id']}_selected")
    node_vars[row["id"]] = node_var
    model.AddBoolOr(
        [var for key, var in edge_vars.items() if row["id"] in key]
    ).OnlyEnforceIf(node_var)
    model.AddBoolAnd(
        [var.Not() for key, var in edge_vars.items() if row["id"] in key]
    ).OnlyEnforceIf(node_var.Not())
    for node_obj in node_objectives:
        name = f"{row['id']}_{node_obj}"
        new_constant = model.NewConstant(row[node_obj])
        new_var = model.NewIntVar(-10000, 10000, name)
        node_obj_vars[node_obj][row["id"]] = new_var
        model.AddMultiplicationEquality(new_var, [node_var, new_constant])


def add_edge_objective_vars(
    row,
    model,
    edge_vars: dict,
    edge_objectives: set,
    edge_obj_vars: dict,
):
    """
    Creates a dictionary of objective_vars that contain the objective constants when the corresponding
    edge is selected and contain 0 when the edge is not selected
    """
    for edge_obj in edge_objectives:
        name = str(row["source"]) + "_" + str(row["destination"]) + "_" + edge_obj
        new_constant = model.NewConstant(row[edge_obj])
        new_var = model.NewIntVar(-10000, 10000, name)
        edge_obj_vars[edge_obj][row["source"], row["destination"]] = new_var
        model.AddMultiplicationEquality(
            new_var, [edge_vars[row["source"], row["destination"]], new_constant]
        )


def get_soln_dict(solver, edge_vars):
    """
    returns a result dictionary after solution
    """
    return {
        "objective": solver.ObjectiveValue(),
        "edges": get_selected_edges(solver, edge_vars),
        "time": solver.WallTime(),
    }


def get_selected_edges(solver: cp_model.CpSolver, edge_vars: dict):
    """
    Extracts a solution from the solver and its variables
    """
    return [
        (int(key[0]), int(key[1]))
        for key, val in edge_vars.items()
        if solver.Value(val)
    ]
