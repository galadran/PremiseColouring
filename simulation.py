import networkx as nx
import random
from tqdm import tqdm
import matplotlib.pyplot as plt

GREEN = "g"
RED = "r"
GREY = "b"

def set_colour(G, targets, colour):
    #print("Setting colours of " + str(len(targets)) + " nodes to " + str(colour))
    for v in targets:
        G.add_node(v, colour=colour)

def not_coloured(V):
    return V[1]["colour"] == GREY

def not_coloured_ref(G,V):
    return G.nodes[V]["colour"] == GREY

def grey_nodes(G):
    return filter(not_coloured, G.nodes(data=True))

def finished_graph(G):
    return len(grey_nodes(G)) == 0

def reveal_node(G, V, pRed):
    #TODO - Generalise the probability distribution?
    #print("Revealing node " + str(V))
    r = random.random()
    if r >= pRed:
        #print("Node is green!")
        to_colour = list(nx.algorithms.dag.descendants(G, V))
        to_colour.append(V)
        set_colour(G, to_colour, GREEN)
    else:
        #print("Node is red!")
        to_colour = list(nx.algorithms.dag.ancestors(G, V))
        to_colour.append(V)
        set_colour(G, to_colour, RED)

def total_grey_parents(G, V):
    return len(filter(lambda x: not_coloured_ref(G,x), nx.algorithms.dag.ancestors(G, V)))

def total_grey_children(G, V):
    return len(filter(lambda x: not_coloured_ref(G,x), nx.algorithms.dag.descendants(G, V)))

def draw_graph(G):
    values = [a[1]["colour"] for a in G.nodes(data=True)]
    nx.draw(G,node_color=values)
    plt.show()

def play_game(DAG,pRed,strat):
    oracle_calls = 0
    while not finished_graph(DAG):
        oracle_calls += 1
        reveal_node(DAG,strat(DAG),pRed)
        #draw_graph(DAG)
    #draw_graph(DAG)
    #print("Total Oracle Calls: " + str(oracle_calls))
    return oracle_calls

def get_starting_graph(generator):
    G = generator() #Tree
    DAG = nx.condensation(G)
    set_colour(DAG,DAG.nodes(),GREY)
    return DAG
    
def run_experiment(trials):
    #TODO Run each strategy over the same randomly generated graphs
    #TODO Make parallel?
    for (name,samples,pRed,generator,strat) in trials:
        results = []
        for _ in tqdm(xrange(samples),leave=False):
            DAG = get_starting_graph(generator)
            results.append(play_game(DAG,pRed,strat))
        print(name +" avg="+str(sum(results)/len(results)) + " maxs="+str(max(results))+ " min="+str(min(results)))