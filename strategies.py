import random 
from simulation import total_grey_parents,total_grey_children,not_coloured

def expected_value(G, V, pRed):
    return pRed * total_grey_parents(G, V) + (1.0 - pRed) * total_grey_children(G,V) + 1

def get_max_E(targets,fun):
    maximal = set()
    max_seen = 0.0
    for V in targets:
        if type(V) is not int: 
            V = V[0]
        r = fun(V)#expected_value(G, V, pRed)
        #print("Expected value of node " + str(V) + " is " + str(r))
        if r > max_seen:
            max_seen = r
            maximal = set([V])
        elif r == max_seen:
            maximal.add(V)
        else:
            continue
    #print("There are " + str(len(maximal)) + " nodes of maximal expected value " + str(max_seen))
    return maximal

def strat_rand(G,pRed):
    return random.choice(list(filter(not_coloured,G.nodes(data=True))))[0]

def strat_exp(G, pRed):
    #Pick any node with a maximal expected value
    fun = lambda x : expected_value(G,x,pRed)
    return random.choice(list(get_max_E(filter(not_coloured,G.nodes(data=True)),fun)))

def strat_safe(G,pRed):
    #Pick any node which safest (max min value), tie break on expected value
    targets = filter(not_coloured,G.nodes(data=True))
    fun = lambda x : min(total_grey_parents(G,x),total_grey_children(G,x))
    safe_targets = list(get_max_E(targets,fun))
    fun2 =  lambda x : expected_value(G,x,pRed)
    best_safe_targets = list(get_max_E(safe_targets,fun2))
    return random.choice(best_safe_targets)

def strat_risk(G,pRed):
    #Pick any node with the highest expected value, tie break on safest
    targets = filter(not_coloured,G.nodes(data=True))
    fun = lambda x : expected_value(G,x,pRed)
    best_targets = list(get_max_E(targets,fun))
    fun2 = lambda x : min(total_grey_parents(G,x),total_grey_children(G,x))
    safe_best_targets = list(get_max_E(best_targets,fun2))
    return random.choice(safe_best_targets)