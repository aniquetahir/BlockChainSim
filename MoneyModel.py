from tqdm import tqdm
from collections import defaultdict
from mesa import Model, Agent
from entity import Entity, Miner, Exchange, Merchant
# from typing import Dict, ClassVar
from mesa.time import RandomActivation
import matplotlib.pyplot as plt
import random
from blockchain import Blockchain
from block import Block
from transaction import Transaction
from typing import List
import json

RANDOM_SEED = 123
random.seed(RANDOM_SEED)


class MoneyModel(Model):
    num_agents: int
    schedule: RandomActivation
    habits_range: range
    MAX_HABITS: int
    MINER_PERCENTAGE: float
    blockchain: Blockchain
    pending_transactions: List[Transaction]
    candidate_blocks: List[Blockchain]

    def __init__(self, N: int, habits_range: range = range(1, 10), MAX_HABITS: int = 10,
                 MINER_PERCENTAGE = 0.1, SELLER_PERCENTAGE = 0.2, EXCHANGE_PERCENTAGE = 0.02):
        super().__init__()
        self.MAX_HABITS = MAX_HABITS
        self.habits_range = habits_range
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.TRANSACTIONS_PER_BLOCK = 500
        self.pending_transactions = []
        self.transaction_age = defaultdict(int)
        self.candidate_blocks = []
        self.MINER_PERCENTAGE = MINER_PERCENTAGE
        self.SELLER_PERCENTAGE = SELLER_PERCENTAGE
        self.EXCHANGE_PERCENTAGE = EXCHANGE_PERCENTAGE
        self.BUYER_PERCENTAGE = 1-MINER_PERCENTAGE-SELLER_PERCENTAGE-EXCHANGE_PERCENTAGE
        self.blockchain = Blockchain(Block('0', []))
        self.AVG_TRANSACTION = 0.5
        self.WEALTH_SD = 0.2
        self.BLOCK_MINING_REWARD = 50
        self.TRANSACTION_EXPIRY = 3

        agent_classes = random.choices(['miner', 'buyer', 'seller', 'exchange'],
                                       [MINER_PERCENTAGE, self.BUYER_PERCENTAGE, SELLER_PERCENTAGE, EXCHANGE_PERCENTAGE],
                                       k=N)
        # Create Agents
        for i in range(self.num_agents):
            is_miner_prob = self.random.random()
            # Create habits
            habits = [False]*MAX_HABITS
            for random_habit in range(self.random.choice(range(1, MAX_HABITS))):
                habit_index = self.random.choice(range(MAX_HABITS))
                habits[habit_index] = True

            # Decide whether the Agent is also a miner
            if agent_classes[i] == 'miner':
                a = Miner(i, self, habits, self.random.random(), self.random.random())
            elif agent_classes[i] == 'buyer':
                a = Entity(i, self, habits, random.random())
            elif agent_classes[i] == 'seller':
                # TODO add seller agent class
                a = Merchant(i, self, habits, self.random.random())
            else:
                # TODO add exchange agent class
                a = Exchange(i, self, self.random.random())

            self.schedule.add(a)

    def step(self):
        self.schedule.step()
        # for pending transactions. increase transaction age
        for tr in self.pending_transactions:
            self.transaction_age[tr.id] += 1
        # remove transactions which are old
        t_pending_transactions = []
        for tr in self.pending_transactions:
            if self.transaction_age[tr.id] <= self.TRANSACTION_EXPIRY:
                t_pending_transactions.append(tr)
        self.pending_transactions = t_pending_transactions
        # Select Miners and Register pending transactions


# class MoneyAgent(Agent):
#     def __init__(self, uid: int, model: MoneyModel):
#         super().__init__(uid, model)
#         self.wealth = 1
#
#     def step(self):
#         if self.wealth == 0:
#             return
#         other_agent = self.random.choice(self.model.schedule.agents)
#         other_agent.wealth += 1
#         self.wealth -= 1


if __name__ == "__main__":
    m_model = MoneyModel(100)

    # Print out the different types of Agents
    buyers = [x for x in m_model.schedule.agents if type(x) == Entity]
    merchants = [x for x in m_model.schedule.agents if type(x) == Merchant]
    exchanges = [x for x in m_model.schedule.agents if type(x) == Exchange]
    miners = [x for x in m_model.schedule.agents if type(x) == Miner]

    print("Buyers: %d" % len(buyers))
    print("Merchants: %d" % len(merchants))
    print("Exchanges: %d" % len(exchanges))
    print("Miners: %d" % len(miners))

    simulation = []
    for i in tqdm(range(100)):
        m_model.step()
        step_data = [x.to_dict() for x in m_model.schedule.agents]
        simulation.append(step_data)

    with open('simulation.json', 'w') as sim_file:
        json.dump(simulation, sim_file)

    # agent_wealth = [a.wealth for a in m_model.schedule.agents]
    # plt.hist(agent_wealth)
    # plt.show()


