#! /usr/bin/env python3
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from fa2 import ForceAtlas2
from curved_edges import curved_edges
from collections import defaultdict
import json
import networkx as nx
import sys
from tqdm import tqdm
import pickle


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


def visualize(sim_data):
    print("simulation steps: %d" % len(sim_data))
    for step in tqdm(sim_data[1:]):
        print('test')
        # NODE ATTRIBUTES
        # Get the chains(plus no. of chains, length of chains, master chain)
        active_chains = {}
        chain_counts = defaultdict(int)
        for agent in step:
            chain = agent['blockchain']
            active_chains[chain['hash']] = {'chain': chain, 'length': len(chain['blocks'])}
            chain_counts[chain['hash']] += 1
        frequent_chains = sorted(chain_counts.items(), key=lambda x:x[1])
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
            node_sizes.append(agent_wealth[a['id']])
        # node_sizes = [x*100 for x in node_sizes]

        edge_weights = []
        for n, w in node_node_transactions.items():
            G.add_edge(n[0], n[1], weight=w)

        # node_sizes = [v * 100 for v in nx.degree(G).values()]
        pos = nx.layout.fruchterman_reingold_layout(G, iterations=200)
        # pos = nx.layout.spring_layout(G)
        nodes = nx.draw_networkx_nodes(G, pos, node_size=node_sizes, node_color='blue')
        edges = nx.draw_networkx_edges(G, pos, arrowstyle='->', arrowsize=10, edge_cmap=plt.cm.Blues, width=2)

        # pc = mpl.collections.PatchCollection(edges, cmap=plt.cm.Blues)

        plt.show()
        # Create Blockchain visualization
        # Create Legend
        # Create Watermark
        # Merge Everything

        pass
    pass


if __name__ == "__main__":
    simulation_path = sys.argv[1]
    with open(simulation_path, 'rb') as sim_file:
        simulation_data = pickle.load(sim_file)

    visualize(simulation_data)

