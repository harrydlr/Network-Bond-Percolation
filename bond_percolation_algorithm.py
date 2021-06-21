import networkx as nx
import numpy as np
from collections import Counter
import random
import matplotlib.pyplot as plt
import multiprocessing


# Create/define Network:
ref_network = nx.erdos_renyi_graph(5000, 0.012)
# Set "CLuster" attribute
ref_list_nodes_clusters = {}
for node in list(ref_network.nodes):
    ref_list_nodes_clusters[node] = node
#
def edge_percolation(param):
    results_gcc = {}
    results_slcc = {}
    G, list_nodes_clusters = param
    edges_list_i = [e for e in G.edges]
    edges_list_f = []
    a = len(edges_list_f)
    for i in range(len(edges_list_i)):
        j = random.randint(i, len(edges_list_i)-1)
        if i != j:
            edges_list_f.append(edges_list_i[j])
            edges_list_i[j] = edges_list_i[i]
        else:
            edges_list_f.append(edges_list_i[i])

    bond_count = 0
    frac_slcc = None
    for bond in edges_list_f:
        if list_nodes_clusters[bond[0]] != list_nodes_clusters[bond[1]]:
            counts_node0 = sum(value == list_nodes_clusters[bond[0]] for value in list_nodes_clusters.values())
            counts_node1 = sum(value == list_nodes_clusters[bond[1]] for value in list_nodes_clusters.values())
            if counts_node0>counts_node1:
                clus_chosen = list_nodes_clusters[bond[0]]
                clus_replace = list_nodes_clusters[bond[1]]
                for key, value in list_nodes_clusters.items():
                    if list_nodes_clusters[key] == clus_replace:
                        list_nodes_clusters[key] = clus_chosen
            else:
                clus_chosen = list_nodes_clusters[bond[1]]
                clus_replace = list_nodes_clusters[bond[0]]
                for key, value in list_nodes_clusters.items():
                    if list_nodes_clusters[key] == clus_replace:
                        list_nodes_clusters[key] = clus_chosen

        n_cluster, count_n_cluster = Counter(list_nodes_clusters.values()).most_common(1)[0]
        try:
            n_cluster_slcc, count_n_cluster_slcc = Counter(list_nodes_clusters.values()).most_common(2)[1]
            frac_slcc = count_n_cluster_slcc / len(list_nodes_clusters)
        except:
            pass
        frac_gcc = count_n_cluster/len(list_nodes_clusters)
        bond_count += 1
        results_gcc[np.round((bond_count/len(edges_list_f)), 4)] = frac_gcc
        if frac_slcc is not None:
            results_slcc[np.round((bond_count/len(edges_list_f)),4)] = frac_slcc
    results = {"GCC": results_gcc, "SLCC": results_slcc}
    return results


inputs = [(ref_network, ref_list_nodes_clusters) for i in range(50)]
with multiprocessing.Pool(8) as p:
    partial_results = p.map(edge_percolation, inputs)

final_results = {}
final_results["GCC"] = {}
final_results["SLCC"] = {}
for l in range(len(partial_results)):
    for key in partial_results[l]["GCC"]:
        try:
            final_results["GCC"][key].append(partial_results[l]["GCC"][key])
        except:
            final_results["GCC"][key] = []
            final_results["GCC"][key].append(partial_results[l]["GCC"][key])

    for key2 in partial_results[l]["SLCC"]:
        try:
            final_results["SLCC"][key2].append(partial_results[l]["SLCC"][key2])
        except:
            final_results["SLCC"][key2] = []
            final_results["SLCC"][key2].append(partial_results[l]["SLCC"][key2])
for key in final_results:
    for key2 in final_results[key]:
        final_results[key][key2] = np.round(np.mean(final_results[key][key2]), 5)


lists = sorted(final_results["GCC"].items()) # sorted by key, return a list of tuples
x_gcc, y_gcc = zip(*lists) # unpack a list of pairs into two tuples
lists = sorted(final_results["SLCC"].items()) # sorted by key, return a list of tuples
x_slcc, y_slcc = zip(*lists) # unpack a list of pairs into two tuples
# create figure and axis objects with subplots()
fig,ax = plt.subplots()
# make a plot
ax.plot(x_gcc, y_gcc, color="red", marker="o", markersize=0.2)
# set x-axis label
ax.set_xlabel("p",fontsize=14)
# set y-axis label
ax.set_ylabel("GCC",color="red",fontsize=14)
#####################
#####################
# twin object for two different y-axis on the sample plot
ax2 = ax.twinx()
# make a plot with different y-axis using second axis object
ax2.plot(x_slcc, y_slcc, color="blue", marker="o", markersize=0.2)
ax2.set_ylabel("SLCC", color="blue", fontsize=14)
plt.show()
