import networkx as nx
import random
from tqdm import tqdm
import matplotlib.pyplot as plt
import strategies

import pdb

GREEN = "g"
RED = "r"
GREY = "b"

def update_nodes(G, targets, colour,label):
    #print("Setting colours of " + str(len(targets)) + " nodes to " + str(colour))
    for v in targets:
        G.add_node(v, colour=colour,label=str(label))

def not_coloured(V):
    return V[1]["colour"] == GREY

def not_coloured_ref(G,V):
    return G.nodes[V]["colour"] == GREY

def grey_nodes(G):
    return filter(not_coloured, G.nodes(data=True))

def finished_graph(G):
    return len(grey_nodes(G)) == 0

def reveal_node(G, V, pRed,oracle_call,det=None):
    #TODO - Generalise the probability distribution?
    #print("Revealing node " + str(V))
    G.add_node(V,font_weight='bold')
    isRed = False
    if det is None:
        r = random.random()
        if r < pRed:
            isRed = True
    else:
        #pdb.set_trace()
        isRed = det.nodes[V]['colour'] == RED
    if not isRed:
        #print("Node is green!")
        to_colour = list(nx.algorithms.dag.descendants(G, V))
        to_colour.append(V)
        update_nodes(G, to_colour, GREEN,oracle_call)
    else:
        #print("Node is red!")
        to_colour = list(nx.algorithms.dag.ancestors(G, V))
        to_colour.append(V)
        update_nodes(G, to_colour, RED,oracle_call)

def total_grey_parents(G, V):
    return len(filter(lambda x: not_coloured_ref(G,x), nx.algorithms.dag.ancestors(G, V)))

def total_grey_children(G, V):
    return len(filter(lambda x: not_coloured_ref(G,x), nx.algorithms.dag.descendants(G, V)))

def draw_graph(G):
    pos = nx.drawing.nx_pydot.pydot_layout(G,prog='dot')
    colours = [a[1]["label"] for a in G.nodes(data=True)]
    #colours = [a[1]["colour"] for a in G.nodes(data=True)]
    bold_nodes = {}
    regular_nodes = {}
    for n in G.nodes():
        if "font_weight" in G.node[n].keys():
            bold_nodes[n] = G.node[n]["label"]
        else:
            regular_nodes[n] = G.node[n]["label"]
    nx.draw_networkx_nodes(G,pos,node_color=colours)
    nx.draw_networkx_edges(G,pos)
    nx.draw_networkx_labels(G,pos,labels=bold_nodes,font_size=18,font_weight='bold')
    nx.draw_networkx_labels(G,pos,labels=regular_nodes,font_size=18)   
    plt.show()

def play_game(DAG,pRed,strat,det=None):
    oracle_calls = 0
    while not finished_graph(DAG):
        oracle_calls += 1
        reveal_node(DAG,strat(DAG),pRed,oracle_calls,det)
    #print("Total Oracle Calls: " + str(oracle_calls))
    return oracle_calls

def play_multi_game(DAG,pRed,strats,visualise=False):
    GT = DAG.copy()
    play_game(GT,pRed,lambda x: strategies.strat_rand(x,pRed))
    results = []
    for name,s in strats:
        H = DAG.copy()
        oracle_calls = play_game(H,pRed,s,det=GT)
        if visualise:
            results.append((name,oracle_calls,H))
        else:
            results.append((name,oracle_calls))
    return results
    
def get_starting_graph(generator):
    G = generator() #Tree
    DAG = nx.condensation(G)
    update_nodes(DAG,DAG.nodes(),GREY,"?")
    return DAG

def countsToHist(counts):
    f, subplots = plt.subplots(1,len(counts.keys()),sharey=True)
    for strat,plot in zip(counts.keys(),subplots):
        plot.hist(counts[strat],label=strat)        
        plot.legend()
    plt.show()

def run_experiment(trials):
    #TODO Make parallel?
    for (name,samples,pRed,generator,strats) in trials:
        raw_results = []
        for _ in tqdm(xrange(samples),leave=False):
            DAG = get_starting_graph(generator)
            raw_results.append(play_multi_game(DAG,pRed,strats))
        counts = {}
        for r1 in raw_results:
            for a,b in r1:
                if a not in counts.keys():
                    counts[a] = []
                counts[a].append(b)
        for s in counts.keys():
            results = counts[s]
            print(name+":"+s+" avg="+str(sum(results)/len(results)) + " maxs="+str(max(results))+ " min="+str(min(results)))
        countsToHist(counts)