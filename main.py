#!/usr/bin/env python2 

import argparse
import strategies 
import networkx as nx
from simulation import run_experiment,get_starting_graph,play_game,draw_graph

parser = argparse.ArgumentParser(description="Evaluate strategies for lemmas in Tamarin")
parser.add_argument("command",choices=["experiment","visualise"],default="experiment")
parser.add_argument("--graphs","-g",nargs="*",default=["random"])
parser.add_argument("--nodes","-n",default=100,type=int)
parser.add_argument("--edges","-e",default=-1,type=int)
parser.add_argument("--samples","-s",default=100,type=int)
parser.add_argument("--distribution","-d",default=0.5,dest="pRed",type=float)
parser.add_argument("--strategies","-a",nargs="*",default=["exp"])
args = parser.parse_args()

if args.pRed < 0.0 or args.pRed > 1.0:
    print("Probability of being red must be between 0 and 1.0")
    exit(-1)

if args.nodes < 1:
    print("Number of nodes must be greater than 0")
    exit(-1)

if args.edges < 0: 
    args.edges = args.nodes + int(args.nodes * 0.1)

graphDict = {
    "random" : lambda: nx.gnm_random_graph(args.nodes,args.edges,directed=True),
    "tree" : lambda:  nx.generators.directed.gn_graph(args.nodes),
    "chain" : lambda: nx.generators.path_graph(args.nodes,create_using=nx.DiGraph()) 
}

for g in args.graphs:
    if g == "any" or g == "*" or g == "all":
        args.graphs = graphDict.keys() 
    elif  g not in graphDict.keys():
        print("Unknown graph type " + g)
        exit(-1)

stratDict = {
    "exp" : lambda x : strategies.strat_exp(x,args.pRed),
    "risk" :lambda x : strategies.strat_risk(x,args.pRed),
    "safe" : lambda x : strategies.strat_safe(x,args.pRed),
    "rand" : lambda x : strategies.strat_rand(x,args.pRed),
}

for s in args.strategies:
    if s == "any" or s == "*" or s == "all":
        args.strategies = stratDict.keys() 
    elif s not in stratDict.keys():
        print("Unknown strategy type " + s)
        exit(-1)
        
if args.command == "experiment":
    trials = []
    for g in args.graphs:
        for s in args.strategies:
            name = g + ":" + s
            t = (name,args.samples,args.pRed,graphDict[g],stratDict[s])
            trials.append(t)
    print("Running " + str(len(trials)) + " experiments with " + str(args.nodes) + " nodes, " + str(args.samples) + " samples" +            ", " + str(args.edges) + " edges and " + str(args.pRed) + " probability of a node being red.")
    run_experiment(trials)
elif args.command == "visualise":
    if len(args.graphs) != 1 or len(args.strategies) != 1:
        print("There must be exactly one graph and exactly one strategy.")
        exit(-1)
    else:
        #TODO Make this generate a pretty GIF?
        #Probably best to switch to using GraphViz!
        print("Generating a " + args.graphs[0] + " graph with " + str(args.nodes) +" nodes.")
        print("Each node has a " + str(args.pRed) + " probability of being red.")
        print("The strategy is " + args.strategies[0])
        G = get_starting_graph(graphDict[args.graphs[0]])
        calls = play_game(G,args.pRed,stratDict[args.strategies[0]])
        print("Total oracle calls: " + str(calls))
        draw_graph(G)
else:
    print("Unknown command " + args.command)
    exit(-1)

print("Finished Successfully.")
