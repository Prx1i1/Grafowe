import os
from dimacs import loadWeightedGraph, readSolution

def build_graph(V, L):

    edges = [dict() for _ in range(V + 1)]
    for (u, v, c) in L:
        if u == v:
            continue
        # Dodaj wagę (jeśli wiele krawędzi, sumujemy)
        edges[u][v] = edges[u].get(v, 0) + c
        edges[v][u] = edges[v].get(u, 0) + c
    return edges

def merge_vertices(edges, x, y):

    if x == y:
        return
    for z, w in list(edges[y].items()):
        if z == x:
            continue
        edges[x][z] = edges[x].get(z, 0) + w
        edges[z][x] = edges[z].get(x, 0) + w
        if y in edges[z]:
            del edges[z][y]

    edges[y].clear()
    if y in edges[x]:
        del edges[x][y]
    return

def minimum_cut_phase(edges, active):

    n = len(edges) - 1
    in_a = [False] * (n + 1)      
    weights = [0] * (n + 1)       
    order = []                    

    start = None
    for i in range(1, n + 1):
        if active[i]:
            start = i
            break
    if start is None:
        return (0, None, None) 

    in_a[start] = True
    order.append(start)

    for v in range(1, n + 1):
        if active[v] and not in_a[v]:
            weights[v] = edges[v].get(start, 0)

    active_count = sum(1 for i in range(1, n+1) if active[i])
    while len(order) < active_count:
        max_w = -1
        sel = None
        for v in range(1, n + 1):
            if active[v] and not in_a[v]:
                if weights[v] > max_w:
                    max_w = weights[v]
                    sel = v
        if sel is None:
            for v in range(1, n + 1):
                if active[v] and not in_a[v]:
                    sel = v
                    break
            if sel is None:
                break

        in_a[sel] = True
        order.append(sel)

        for v in range(1, n + 1):
            if active[v] and not in_a[v]:
                weights[v] += edges[v].get(sel, 0)

    if len(order) == 0:
        return (0, None, None)
    if len(order) == 1:
        return (0, order[-1], None)

    s = order[-1]
    t = order[-2]

    cut_value = 0
    for v, w in edges[s].items():
        if v != s:
            cut_value += w

    return (cut_value, s, t)

def stoer_wagner(V, L):

    edges = build_graph(V, L)

    active = [False] * (V + 1)
    for i in range(1, V + 1):
        active[i] = True

    best = None


    while sum(1 for i in range(1, V+1) if active[i]) > 1:
        cut_value, s, t = minimum_cut_phase(edges, active)
        if s is None or t is None:
            if best is None:
                best = 0
            else:
                best = min(best, 0)
            break

        if best is None or cut_value < best:
            best = cut_value

        merge_vertices(edges, s, t)
        active[t] = False

    if best is None:
        return 0
    return best


root = "./graphs-lab3"

for i in os.listdir(root):
    filename = i
    print(filename)

    V, L = loadWeightedGraph(root + "/" + filename)
    expected = readSolution(root + "/" + filename)
    result = stoer_wagner(V, L)
    print(f"Graf: {filename}, Wynik: {result}, Oczekiwany: {expected}")
