# Introduction

![Simulation](https://media.giphy.com/media/ZBc7vTdGgPcuwULrZh/giphy.gif)

This is a system for creating an agent based simulation for the Blockchain network.
The key features of this system is to create a random simulation which is also reproduceable. 
This is achieved by letting the user decide on the seed for RNG. Another objective of this system
is to allow the user to define the behaviour of different types of nodes which participate in the blockchain.

Each node in the system inherits from the `Entity` class which defines the default behaviour of a random blockchain node.
The system can be extended by creating additional functions after extending an `Entity`. For example, the included 
`Miner` class extends entity by implementing functions which give the `Miner` a block reward and adds new blocks to the 
chain. A `Miner` can be further extended by extending the `Miner` class.

Each `Entity` has an embedding vector which represents the habits of the node. These habits can be used to decide on 
how the nodes interact with each other. For example, an `Entity` with a particular habit is more likely to interact 
with a specific `Merchant` with a similar habit embedding.

# Prerequisites
The following libraries were used while designing the simulator(they need to be installed before running the code):
```
numpy
matplotlib
networkx
bezier
fa2
```

# Usage
Creating the simulation files:
```bash
python3 simulation.py
``` 

Creating the visualization:
```bash
mkdir plots
python3 visualize.py simulation.pkl
```