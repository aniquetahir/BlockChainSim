from typing import List
from wallet import Wallet
from mesa import Agent


class Entity(Agent):
    # TODO Agent constructor
    def __init__(self, h: List[bool], t: float):
        """
        :param h: A one-hot vector representing the habits of the user
        :param t: A temperature representing the frequency of transactions
        """
        self.habits = h
        self.temperature = t
        self.wallets = []
        self.attributes = []
        pass

    def add_wallet(self, key) -> Wallet:
        w = Wallet(key)
        self.wallets.append(w)
        return w

    def simulate_transactions(self):
        # TODO
        pass


class Miner(Entity):
    def __init__(self, h: List[bool], t: float, mining_power: float):
        """

        :param h:
        :param t:
        :param mining_power:
        """
        super().__init__(h, t)
        self.attributes.append('miner')
        self.mp = mining_power

    def mine(self):
        # TODO implement mining
        pass


