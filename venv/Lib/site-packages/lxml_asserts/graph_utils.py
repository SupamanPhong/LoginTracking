# coding=utf-8

from collections import defaultdict, deque


def find_max_matching(graph):
    """
    Returns a maximum matching of a bipartite graph.
    :param graph: dict of sets, representing a bipartite graph structure
    :return: maximum matching (represented as a dict)
    """
    left = list(graph)
    pair = defaultdict(lambda: None)
    dist = defaultdict(lambda: None)
    q = deque()

    full_graph = graph.copy()
    for v in left:
        for n in graph[v]:
            full_graph[n].add(v)

    def bfs():
        for v in left:
            if pair[v] is None:
                dist[v] = 0
                q.append(v)
            else:
                dist[v] = None

        dist[None] = None

        while q:
            v = q.popleft()
            if v is not None:
                for u in full_graph[v]:
                    if dist[pair[u]] is None:
                        dist[pair[u]] = dist[v] + 1
                        q.append(pair[u])

        return dist[None] is not None

    def dfs(v):
        if v is not None:
            for u in full_graph[v]:
                if dist[pair[u]] == dist[v] + 1 and dfs(pair[u]):
                    pair[u] = v
                    pair[v] = u
                    return True

            dist[v] = None
            return False

        return True

    matching = 0

    while bfs():
        for v in left:
            if pair[v] is None and dfs(v):
                matching += 1
                if matching == len(graph):
                    break

    return {v: pair[v] for v in pair if pair[v] is not None}
