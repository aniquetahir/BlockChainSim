#! /usr/bin/env python3
import numpy as np
import os
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import matplotlib.patches as mpatches
from fa2 import ForceAtlas2
from curved_edges import curved_edges
from collections import defaultdict
import json
import networkx as nx
import sys
from tqdm import tqdm
import pickle
from matplotlib.axes._subplots import Axes

forceatlas2 = ForceAtlas2(gravity=5)


def get_wallet_balances(blockchain):
    balances = defaultdict(float)
    for block in blockchain['blocks']:
        for transaction in block['transactions']:
            for i in transaction['inputs']:
                balances[i['address']] -= i['amount']
            for o in transaction['outputs']:
                balances[o['address']] += o['amount']

    return balances


def get_user_user_transactions(blockchain, wallet_agent_map):
    transactions = defaultdict(int)
    for block in blockchain['blocks']:
        for transaction in block['transactions']:
            input_users = []
            output_users = []
            for i in transaction['inputs']:
                if i['address'] != 'reward':
                    input_users.append(wallet_agent_map[i['address']])
            for o in transaction['outputs']:
                output_users.append(wallet_agent_map[o['address']])
            for i in set(input_users):
                for o in set(output_users):
                    if i != o:
                        transactions[(i, o)] += 1
    return transactions


def create_frame(G, pos, node_sizes, node_colors, legend_handles, step, stats, limits, filename):
    # curves = curved_edges(G, pos)
    # lc = LineCollection(curves, color='black', alpha=0.15, linewidths=1)
    # pos = nx.layout.fruchterman_reingold_layout(G, iterations=200)
    # pos = nx.layout.spring_layout(G)
    ax: Axes = plt.gca()
    # fig = plt.figure()
    # fig.set_facecolor('black')
    # ax.add_collection(lc)
    ax.text(0, 0, 'Step: %d' % step, verticalalignment='bottom',
            horizontalalignment='left', transform=ax.transAxes)
    ax.text(0, 0, stats, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)
    # ax.set_facecolor('black')
    nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.2)
    nx.draw_networkx_edges(G, pos, edge_color='black', node_size=node_sizes, connectionstyle='arc3,rad=0.2', alpha=0.15, arrowsize=5)
    plt.legend(handles=legend_handles)
    plt.xlim(limits[0]-20, limits[1]+20)
    plt.ylim(limits[2]-20, limits[3]+20)
    # plt.show()
    plt.savefig(os.path.join('plots', filename), dpi=500)
    plt.clf()


def normalize_pos(pos, limits):
    pos_arr = np.array([x[1] for x in pos.items()])
    pos_min = np.min(pos_arr, 0)
    pos_diff = np.max(pos_arr, 0) - pos_min
    normalized = (pos_arr - pos_min) * [limits[1]-limits[0], limits[3]-limits[2]] / pos_diff
    normalized = normalized + [limits[0], limits[2]]
    return dict(enumerate(normalized.tolist()))


def create_visualization(keyframe_data, node_colors, legend_handles, num_intermediate=10):
    # animation_keyframe_data.append({
    #     'G': G,
    #     'pos': pos,
    #     'node_sizes': node_sizes,
    #     'step': i,
    #     'stats': chain_stats
    # })
    prev_pos = None
    positions = [x['pos'] for x in keyframe_data]
    positions = np.array([x[1] for p in positions for x in p.items()])
    xmin = np.min(positions[:, 0])
    xmax = np.max(positions[:, 0])
    ymin = np.min(positions[:, 1])
    ymax = np.max(positions[:, 1])
    limits = [xmin, xmax, ymin, ymax]

    # for each keyframe
    # Generate previous intermediate frames
    # Create this frame
    # save to folder
    # convert frames to video
    frame_num = 1
    for i, kf in tqdm(enumerate(keyframe_data), total=len(keyframe_data)):
        G = kf['G']
        pos = kf['pos']
        node_sizes = kf['node_sizes']
        step = kf['step']
        stats = kf['stats']
        pos = normalize_pos(pos, limits)
        if prev_pos:
            # prev_pos = normalize_pos(prev_pos, limits)
            # Generate intermediate frames
            for j in range(num_intermediate):
                ratio = j / num_intermediate
                prev_vals = np.array([x[1] for x in prev_pos.items()])
                pos_vals = np.array([x[1] for x in pos.items()])
                intermediate_vals = (1-ratio) * prev_vals + ratio * pos_vals
                intermediate_pos = dict(enumerate(intermediate_vals.tolist()))
                create_frame(G, intermediate_pos, node_sizes, node_colors, legend_handles,
                             step, stats, limits, '%04d.png' % frame_num)
                frame_num += 1
        prev_pos = pos
        create_frame(G, pos, node_sizes, node_colors,
                     legend_handles, step, stats, limits, '%04d.png' % frame_num)


def visualize(sim_data):
    print("simulation steps: %d" % len(sim_data))
    prev_pos = None
    node_colors = []
    color_map = {
        'Entity': '#ff1111',
        'Miner': '#00ff00',
        'Exchange': '#1111ff',
        'Merchant': '#274652'
    }
    legend_handles = [mpatches.Patch(color=x[1], label=x[0]) for x in color_map.items()]
    for a in sim_data[0]:
        node_colors.append(color_map[a['type']])

    animation_keyframe_data = []

    for i, step in enumerate(sim_data[1:]):
        print('test')
        # NODE ATTRIBUTES
        # Get the chains(plus no. of chains, length of chains, master chain)
        active_chains = {}
        chain_counts = defaultdict(int)
        for agent in step:
            chain = agent['blockchain']
            active_chains[chain['hash']] = {'chain': chain, 'length': len(chain['blocks'])}
            chain_counts[chain['hash']] += 1
        frequent_chains = sorted(chain_counts.items(), key=lambda x: x[1])
        master_chain = active_chains[frequent_chains[-1][0]]['chain']
        # Get the value of wallets according to the longest chain
        balances = get_wallet_balances(master_chain)
        # Get wallet -> node mapping
        # Get the value of nodes by accumulating the wallet wealth
        wallet_agent = {}
        agent_wealth = defaultdict(float)
        for agent in step:
            wallets = agent['wallets']
            for w in wallets:
                wallet_agent[w['hash']] = agent['id']
                agent_wealth[agent['id']] += balances[w['hash']]

        # EDGE ATTRIBUTES
        # Get wallet -> wallet transaction numbers
        # Get node -> node transactions from wallet -> wallet transactions
        node_node_transactions = get_user_user_transactions(master_chain, wallet_agent)
        # Assign edges based on node -> node transactions

        # Create Network visualization
        G = nx.DiGraph()
        node_sizes = []
        for a in step:
            G.add_node(a['id'], weight=agent_wealth[a['id']])
            node_sizes.append((50 + agent_wealth[a['id']]) * 0.1)
        # node_sizes = [x*100 for x in node_sizes]

        edge_weights = []
        for n, w in node_node_transactions.items():
            G.add_edge(n[0], n[1], weight=w)

        if len(G.edges()) == 0:
            continue

        # node_sizes = [v * 100 for v in nx.degree(G).values()]
        pos = forceatlas2.forceatlas2_networkx_layout(G, pos=prev_pos)
        prev_pos = pos
        chain_stats = 'Chains: Master(%d blocks), Active(%d)' % (len(master_chain['blocks']),
                                                                 len(active_chains.keys()))
        animation_keyframe_data.append({
            'G': G,
            'pos': pos,
            'node_sizes': node_sizes,
            'step': i,
            'stats': chain_stats
        })

        # curves = curved_edges(G, pos)
        # lc = LineCollection(curves, color='black', alpha=0.15, linewidths=1)
        # # pos = nx.layout.fruchterman_reingold_layout(G, iterations=200)
        # # pos = nx.layout.spring_layout(G)
        # ax: Axes = plt.gca()
        # # fig = plt.figure()
        # # fig.set_facecolor('black')
        # ax.add_collection(lc)
        # ax.text(0, 0, 'Step: %d' % i, verticalalignment='bottom',
        #         horizontalalignment='left', transform=ax.transAxes)
        # ax.text(0, 0, chain_stats, verticalalignment='top', horizontalalignment='left', transform=ax.transAxes)
        # # ax.set_facecolor('black')
        # nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color=node_colors, alpha=0.2)
        # # edges = nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=10, edge_cmap=plt.cm.Blues, width=2)
        # # pc = mpl.collections.PatchCollection(edges, cmap=plt.cm.Blues)
        # # plt.savefig(os.path.join('plots', '%04d.png' % i), dpi=300)
        # plt.legend(handles=legend_handles)
        # plt.show()
        # plt.clf()
        # # plt.show()
        # # Create Blockchain visualization
        # # Create Legend
        # # Create Watermark
        # # Merge Everything
    create_visualization(animation_keyframe_data, node_colors, legend_handles)


if __name__ == "__main__":
    simulation_path = sys.argv[1]
    with open(simulation_path, 'rb') as sim_file:
        simulation_data = pickle.load(sim_file)

    visualize(simulation_data)
