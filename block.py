from transaction import Transaction
from typing import List, Dict
from uuid import uuid4
from blockchain import Blockchain


class Block:
    def __init__(self, prev: str, transactions: List[Transaction]):
        self.prev = prev
        self.transactions = transactions
        self.reward = []
        self.id = str(uuid4())

    def add(self, chain: Blockchain, rewards: List[Dict]):
        """
        :param chain:
        :param rewards:
        :return:
        """
        self.reward = rewards
        chain.add(self)
        # TODO basic sanity check for block rewards


