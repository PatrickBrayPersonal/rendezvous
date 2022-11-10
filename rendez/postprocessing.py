"""
Prepares the output for display from solution
"""

def reformat_for_frontend(soln, nodes, edges):
    selected_nodes = [tup[0] for tup in soln['edges']] + [soln['edges'][-1][1]]
    return nodes.iloc[selected_nodes]

