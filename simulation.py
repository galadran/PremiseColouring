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
    if colour != GREY:
        targets = filter(lambda x : not_coloured_ref(G,x),targets)
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

def draw_graph(name,calls,G,red_green=False):
    pos = nx.drawing.nx_pydot.pydot_layout(G,prog='dot')
    colours = []
    if red_green:
        colours = [a[1]["colour"] for a in G.nodes(data=True)]
    else:
        colours = [a[1]["label"] for a in G.nodes(data=True)]
    bold_nodes = {}
    regular_nodes = {}
    for n in G.nodes():
        if "font_weight" in G.node[n].keys():
            bold_nodes[n] = G.node[n]["label"]
        else:
            regular_nodes[n] = G.node[n]["label"]
    plt.figure()
    nx.draw_networkx_nodes(G,pos,node_color=colours,node_size=800,cmap='Pastel1')
    nx.draw_networkx_edges(G,pos,arrows=True)
    nx.draw_networkx_labels(G,pos,labels=bold_nodes,font_size=18,font_weight='bold')
    nx.draw_networkx_labels(G,pos,labels=regular_nodes,font_size=18)   
    plt.title("Strategy Type: "+name + " Total Calls: " + str(calls))
    plt.show(block=False)

def play_game(DAG,pRed,strat,det=None):
    oracle_calls = 0
    while not finished_graph(DAG):
        oracle_calls += 1
        reveal_node(DAG,strat(DAG),pRed,oracle_calls,det)
    #print("Total Oracle Calls: " + str(oracle_calls))
    return oracle_calls

def play_multi_game(DAG,pRed,strats,visualise=False,alternate=False):
    GT = None
    if alternate:
        GT = DAG.copy()
        play_game(GT,pRed,lambda x: strategies.strat_rand(x,pRed))
        if visualise:
            draw_graph("Test Graph","NA",GT,red_green=True)
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

def countsToHist(name,counts):
    datasets = []
    labels = []
    for strat in counts.keys():
        labels.append(strat)
        datasets.append(counts[strat])
    plt.figure()
    plt.hist(datasets,label=labels,stacked=False,cumulative=True,normed=True)
    plt.title("Graph Type: "+name)
    plt.xlabel("Oracle Calls")
    plt.ylabel("P(Finished at or before _)")
    plt.legend()
    plt.show(block=False)

def run_experiment(trials,alternate=False):
    #TODO Make parallel?
    for (name,samples,pRed,generator,strats) in trials:
        raw_results = []
        for _ in tqdm(xrange(samples),leave=False,desc="Simulating "+name+" graphs"):
            DAG = get_starting_graph(generator)
            raw_results.append(play_multi_game(DAG,pRed,strats,alternate=alternate))
        counts = {}
        for r1 in raw_results:
            for a,b in r1:
                if a not in counts.keys():
                    counts[a] = []
                counts[a].append(b)
        for s in counts.keys():
            results = counts[s]
            print(name+":"+s+" avg="+str(sum(results)/len(results)) + " maxs="+str(max(results))+ " min="+str(min(results)))
        countsToHist(name,counts)
    plt.show()