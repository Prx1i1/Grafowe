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
    # dla każdego sąsiada z wierzchołka y dodaj wagę do x
    for z, w in list(edges[y].items()):
        if z == x:
            # krawędź między x i y zniknie po scałkowaniu (nie przenosimy jej)
            continue
        # dodajemy wagę y-z do x-z
        edges[x][z] = edges[x].get(z, 0) + w
        # aktualizujemy odwrotną krawędź z->x
        edges[z][x] = edges[z].get(x, 0) + w
        # usuwamy odniesienie z->y
        if y in edges[z]:
            del edges[z][y]

    # usuń wszystkie krawędzie wychodzące z y
    edges[y].clear()
    # usuń referencję x<->y jeśli istnieje
    if y in edges[x]:
        del edges[x][y]
    # y pozostaje jako "nieaktywny" (jego słownik jest pusty)
    return

def minimum_cut_phase(edges, active):

    n = len(edges) - 1
    in_a = [False] * (n + 1)      # czy w S
    weights = [0] * (n + 1)       # wagi połączeń do S
    order = []                    # kolejność dodawania do S

    # wybierz dowolny aktywny wierzchołek jako start
    # (wybieramy najmniejszy indeks aktywnego)
    start = None
    for i in range(1, n + 1):
        if active[i]:
            start = i
            break
    if start is None:
        return (0, None, None)  # brak aktywnych wierzchołków

    # zaczynamy od start
    in_a[start] = True
    order.append(start)

    # zainicjuj weights: dla każdego v != start, weight[v] = edges[v].get(start,0)
    for v in range(1, n + 1):
        if active[v] and not in_a[v]:
            weights[v] = edges[v].get(start, 0)

    # dodawaj kolejne wierzchołki aż S zawiera wszystkie aktywne
    active_count = sum(1 for i in range(1, n+1) if active[i])
    while len(order) < active_count:
        # wybierz wierzchołek v (aktywny i nie w S) o maksymalnej weights[v]
        max_w = -1
        sel = None
        for v in range(1, n + 1):
            if active[v] and not in_a[v]:
                if weights[v] > max_w:
                    max_w = weights[v]
                    sel = v
        if sel is None:
            # mamy rozłączony fragment - dodaj dowolny pozostały aktywny wierzchołek
            for v in range(1, n + 1):
                if active[v] and not in_a[v]:
                    sel = v
                    break
            if sel is None:
                break

        # dodaj sel do S
        in_a[sel] = True
        order.append(sel)

        # zaktualizuj weights dla pozostałych
        for v in range(1, n + 1):
            if active[v] and not in_a[v]:
                weights[v] += edges[v].get(sel, 0)

    # ostatni dodany = s, przedostatni = t
    if len(order) == 0:
        return (0, None, None)
    if len(order) == 1:
        return (0, order[-1], None)

    s = order[-1]
    t = order[-2]

    # cut_value = suma wag krawędzi wychodzących z s do reszty (czyli weights[s] bez s)
    # można policzyć jako weights[s] przed dodaniem s — ale mamy je aktualne w weights
    # jednak weights[s] nie jest aktualizowane gdy s było w S; wygodnie policzyć sumę:
    cut_value = 0
    for v, w in edges[s].items():
        if v != s:
            cut_value += w

    # alternatywnie: cut_value == weights[s] przed dodaniem s; ale prostsze wyliczenie wyżej.

    return (cut_value, s, t)

def stoer_wagner(V, L):
    """
    Główna funkcja.
    V: liczba wierzchołków
    L: lista krawędzi (u,v,c)
    Zwraca: wartość spójności krawędziowej (min cut value)
    """
    # zbuduj listę słowników wag
    edges = build_graph(V, L)

    # active[i] = True jeśli wierzchołek i jest jeszcze aktywny (nie został scalony)
    active = [False] * (V + 1)
    for i in range(1, V + 1):
        # aktywny jeśli ma jakiekolwiek krawędzie lub nawet jeśli izolowany — traktujemy go aktywnym
        active[i] = True

    best = None

    # dopóki jest więcej niż 1 aktywny wierzchołek
    while sum(1 for i in range(1, V+1) if active[i]) > 1:
        cut_value, s, t = minimum_cut_phase(edges, active)
        if s is None or t is None:
            # graf rozłączony (lub coś nietypowego) — wtedy cut_value może być 0
            if best is None:
                best = 0
            else:
                best = min(best, 0)
            # spróbuj dalej (scalenie nie będzie możliwe), przerwij pętlę
            break

        # aktualizuj najlepszy wynik
        if best is None or cut_value < best:
            best = cut_value

        # scal t do s (usuwamy t)
        merge_vertices(edges, s, t)
        active[t] = False
        # s pozostaje aktywny

    if best is None:
        return 0
    return best


root = "./graphs-lab3"

for i in os.listdir(root):
    filename = i

    V, L = loadWeightedGraph(root + "/" + filename)
    expected = readSolution(root + "/" + filename)
    # Zakładamy, że wagi początkowe są równe 1 (zgodnie z treścią zadania),
    # ale algorytm działa dla dowolnych wag >= 0.
    result = stoer_wagner(V, L)
    print(f"Graf: {filename}, Wynik: {result}, Oczekiwany: {expected}")
