from mesa import Model, Agent
from entity import Entity, Miner, Exchange, Merchant
# from typing import Dict, ClassVar
from mesa.time import RandomActivation
import matplotlib.pyplot as plt
import random
from blockchain import Blockchain
from block import Block

RANDOM_SEED = 123
random.seed(RANDOM_SEED)

class MoneyModel(Model):
    num_agents: int
    schedule: RandomActivation
    habits_range: range
    MAX_HABITS: int
    MINER_PERCENTAGE: float
    blockchain: Blockchain

    def __init__(self, N: int, habits_range: range = range(1, 10), MAX_HABITS: int = 1000,
                 MINER_PERCENTAGE = 0.1, SELLER_PERCENTAGE = 0.2, EXCHANGE_PERCENTAGE = 0.02):
        super().__init__()
        self.MAX_HABITS = MAX_HABITS
        self.habits_range = habits_range
        self.num_agents = N
        self.schedule = RandomActivation(self)
        self.MINER_PERCENTAGE = MINER_PERCENTAGE
        self.SELLER_PERCENTAGE = SELLER_PERCENTAGE
        self.EXCHANGE_PERCENTAGE = EXCHANGE_PERCENTAGE
        self.BUYER_PERCENTAGE = 1-MINER_PERCENTAGE-SELLER_PERCENTAGE-EXCHANGE_PERCENTAGE
        self.blockchain = Blockchain(Block('0', []))
        agent_classes = random.choices(['miner', 'buyer', 'seller', 'exchange'],
                                       [MINER_PERCENTAGE, self.BUYER_PERCENTAGE, SELLER_PERCENTAGE, EXCHANGE_PERCENTAGE],
                                       k=N)
        # Create Agents
        for i in range(self.num_agents):
            is_miner_prob = random.random()
            # Create habits
            habits = [False]*MAX_HABITS
            for random_habit in random.choices(range(MAX_HABITS)):
                habits[random_habit] = True

            # Decide whether the Agent is also a miner
            if agent_classes[i] == 'miner':
                a = Miner(i, self, habits, random.random(), random.random())
            elif agent_classes[i] == 'buyer':
                a = Entity(i, self, habits, random.random())
            elif agent_classes[i] == 'seller':
                # TODO add seller agent class
                a = Merchant()
            else:
                # TODO add exchange agent class
                a = Exchange()
            self.schedule.add(a)

    def step(self):
        self.schedule.step()
        # Select Miners and Register pending transactions


class MoneyAgent(Agent):
    def __init__(self, uid: int, model: MoneyModel):
        super().__init__(uid, model)
        self.wealth = 1

    def step(self):
        if self.wealth == 0:
            return
        other_agent = self.random.choice(self.model.schedule.agents)
        other_agent.wealth += 1
        self.wealth -= 1


if __name__ == "__main__":
    m_model = MoneyModel(10)
    for i in range(10):
        m_model.step()

    agent_wealth = [a.wealth for a in m_model.schedule.agents]
    plt.hist(agent_wealth)
    plt.show()


