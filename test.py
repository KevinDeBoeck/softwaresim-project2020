import networkx as nx

G = nx.Graph()
G.add_edge(1,2)
G.add_edge(2,3)
G.add_edge(3,4)

#print(G.get_edge_data(1,4))
print(nx.shortest_path(G, source=1, target=4))




