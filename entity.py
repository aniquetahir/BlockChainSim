from typing import List
from wallet import Wallet


class Entity:
    def __init__(self, h: List[bool], t: float):
        """
        :param h: A one-hot vector representing the habits of the user
        :param t: A temperature representing the frequency of transactions
        """
        self.habits = h
        self.temperature = t
        self.wallets = []
        pass

    def add_wallet(self, key) -> Wallet:
        w = Wallet(key)
        self.wallets.append(w)
        return w

    def simulate_transactions(self):
        # TODO
        pass


class Miner(Entity):
    def __init__(self, h: List[bool], t: float):
        super().__init__(h, t)

    def mine(self):
        # TODO implement mining
        pass


