import networkx as nx
import matplotlib.pyplot as plt
from matplotlib import gridspec as gs
from random import random
import json


def visualize_net(net, figfile="business_net.pdf", cutoffs=None, maxcols=6, disp_dict=None):
    if disp_dict == None:
        disp_dict = {"node_size": 50}
    if cutoffs == None:
        cutoffs = [6, 2, 0]

    n_subplots = len(cutoffs)
    fig = plt.figure(figsize=[6.5, 9], tight_layout=True)

    subplots = gs.GridSpec(n_subplots, 1, figure=fig)

    connected_components = [net.subgraph(
        ccomp) for ccomp in nx.connected_components(net.to_undirected())]
    organized_components = arrange_components(
        connected_components, cutoffs, maxcols)

    layout = nx.drawing.nx_agraph.graphviz_layout(net)

    for subplot, (subrows, subcols, connected_components) in zip(subplots, organized_components):
        print(subrows, subcols, len(connected_components))
        subplot = subplot.subgridspec(subrows, subcols)
        print(subplot)
        for idx, ccomp in enumerate(connected_components):
            disp_dict["node_color"] = [
                (random(), random(), random())] * ccomp.order()
            fig.add_subplot(subplot[idx])
            nx.draw(ccomp, layout, **disp_dict)
    fig.savefig(figfile)


def arrange_components(connected_components, cutoffs, maxcols):
    connected_components.sort(reverse=True, key=lambda net: net.order())
    cutoffs.sort()

    organized = [subplot_info([], maxcols)]
    cur_cutoff = cutoffs.pop()
    for net in connected_components:
        order = net.order()
        if order > cur_cutoff:
            organized[-1][-1].append(net)
        else:
            organized[-1] = subplot_info(organized[-1][-1], maxcols)
            while cutoffs and order <= cur_cutoff:
                organized.append(subplot_info([], maxcols))
                cur_cutoff = cutoffs.pop()
            if order > cur_cutoff:
                organized[-1][-1].append(net)
            else:
                break
    organized[-1] = subplot_info(organized[-1][-1], maxcols)
    return organized


def subplot_info(cur_list, maxcols):
    n = len(cur_list)
    if n < 1:
        return (0, 0, [])
    ncols = min(maxcols, n)
    nrows = n // ncols + bool(n % ncols)
    return (nrows, ncols, cur_list)


def ND_lines_to_net(jl_filename="ND_businesses.jl", entity_attrs=None):
    if entity_attrs == None:
        entity_attrs = [
            "Owner Name", "Commercial Registered Agent", "Owners", "Registered Agent"]

    net = nx.DiGraph()
    with open(jl_filename, "rU") as jl_file:
        for ln in jl_file:
            biz_dict = json.loads(ln)
            name = biz_dict["Name"].lower()
            parents = set((biz_dict[attr].split("\n")[0].lower()
                           for attr in entity_attrs if attr in biz_dict)) - {''}
            if name not in net:
                net.add_node(name)
            for parent in parents:
                if parent not in net:
                    net.add_node(parent)
                net.add_edge(parent, name)
    return net

n = ND_lines_to_net()
visualize_net(n)
