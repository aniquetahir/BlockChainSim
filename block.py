from transaction import Transaction
from typing import List

class Block:
    def __init__(self, prev: str, transactions: List[Transaction]):
        self.prev = prev
        self.transactions = transactions
        self.reward = []

    def addBlock(self, rewards):
        self.reward = rewards
        # TODO basic sanity check for block rewards
