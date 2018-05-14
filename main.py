#!/usr/bin/env python2 

import argparse
import strategies 
import networkx as nx
import inspect
from simulation import run_experiment,get_starting_graph,play_multi_game,draw_graph
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Evaluate strategies for testing premises in a system of related premises.")
parser.add_argument("command",choices=["experiment","visualise"],default="experiment",help="Experiment mode will run a benchmark on the different strategies and report on the distribution of results. Visualise will evaluate each strategy on the same graph and show which nodes were selected.")
parser.add_argument("--graphs","-g",nargs="*",default=["random"],help="The types of graphs that can be benchmarked against. In visualise mode, one of chain, tree or random must be provided. In benchmark mode, a space seperated list of classes can be provided or the keyword all. (Chain graphs are linear lists)")
parser.add_argument("--nodes","-n",default=100,type=int,help="The number of nodes in each graph")
parser.add_argument("--edges","-e",default=-1,type=int,help="The number of edges in each graph, only used in random mode. A good figure is the number of nodes * 1.1  as too many will produce cycles which lead to equivalences and the graph size collapsing")
parser.add_argument("--samples","-s",default=100,type=int,help="Only impacts experiment mode, how many graphs of each family to generate and evaluate. Each strategy is tested on each graph.")
parser.add_argument("--distribution","-d",default=0.5,dest="pRed",type=float,help="The split between red and green nodes")
parser.add_argument("--strategies","-a",nargs="*",default=["exp"],help="The types of strategies to evaluate. Options are rand,exp,risk,safe or all. rand will simply pick nodes totally at random. exp will calculate the expected value and select the highest. risk will consider the nodes with the highest expected value and select the one with highest minimum payoff. Safe calculates the node with the highest minimum payoff and then tie breaks on the highest expected value")
parser.add_argument("--alternate",action='store_true',help="In alternate mode, the graphs are generated and filled in by a random algorithm which changes the distribution significally.")
args = parser.parse_args()

#TODO Add a "enumerate colourings" mode where we generate one graph and test every possible colouring?


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
#print(stratDict)
#TODO get this to work 
#stratDict = {}
#strat_prefix = "strat_"
#strats = filter(lambda x: x[0].startswith(strat_prefix),inspect.getmembers(strategies, inspect.isfunction))
#for (name,fun) in strats:
#    short_name = name.replace(strat_prefix,"")
#    stratDict[short_name] = lambda x : fun(x,args.pRed)
#print(stratDict)

for s in args.strategies:
    if s == "any" or s == "*" or s == "all":
        args.strategies = stratDict.keys() 
    elif s not in stratDict.keys():
        print("Unknown strategy type " + s)
        exit(-1)
        
if args.command == "experiment":
    trials = []
    for g in args.graphs:
            t = (g,args.samples,args.pRed,graphDict[g],map(lambda x: (x,stratDict[x]),args.strategies))
            trials.append(t)
    print("Running " + str(len(trials)) + " experiments with " + str(args.nodes) + " nodes, " + str(args.samples) + " samples" +            ", " + str(args.edges) + " edges and " + str(args.pRed) + " probability of a node being red.")
    run_experiment(trials,alternate=args.alternate)
elif args.command == "visualise":
    if len(args.graphs) != 1 :
        print("There must be exactly one graph family.")
        exit(-1)
    else:
        print("Generating a " + args.graphs[0] + " graph with " + str(args.nodes) +" nodes.")
        print("Each node has a " + str(args.pRed) + " probability of being red.")
        G = get_starting_graph(graphDict[args.graphs[0]])
        #TODO Make subplots for this!
        results = play_multi_game(G,args.pRed,map(lambda x: (x,stratDict[x]),args.strategies),visualise=True,alternate=True)
        for name,calls,H in results:
            print("Strategy " + name + " finished after " + str(calls) + ".")
            draw_graph(name,calls,H)
        plt.show()
else:
    print("Unknown command " + args.command)
    exit(-1)

print("Finished Successfully.")