from typing import List, Dict
from wallet import Wallet
from mesa import Agent, Model
from MoneyModel import MoneyModel
import random


class Entity(Agent):
    wallets: List[Wallet]

    # TODO Agent constructor
    def __init__(self, uid: int, model: MoneyModel, h: List[bool], t: float, seller: int = -1):
        """
        :param h: A one-hot vector representing the habits of the user
        :param t: A temperature representing the frequency of transactions
        """
        super().__init__(uid, model)
        self.habits = h
        self.temperature = t
        self.wallets = []
        self.attributes = []
        self.seller = seller
        self.add_wallet()

    def add_wallet(self, amount=0, key=None) -> Wallet:
        w = Wallet(key, amount)
        self.wallets.append(w)
        return w

    def get_total_wealth(self) -> float:
        return sum([x.balance for x in self.wallets])

    def simulate_transactions(self):
        # See if the agent makes a transaction based on the temperature
        if self.temperature < self.random.random():
            return

        # Randomly select a habit to spend on
        habit = self.random.choice([i for i, x in enumerate(self.habits) if x])
        # Select a vendor for the habit
        # TODO vendor favorism
        merchants = [x for x in self.model.schedule.agents if isinstance(x, Merchant) and x.get_habit_index() == habit]
        if len(merchants) == 0:
            return

        transaction_amount = random.random() * self.get_total_wealth()
        merchant: Merchant = self.random.choice(merchants)
        # TODO select UTXO's
        # Select wallets where sum of balances > amount
        w = self.wallets.copy()
        self.random.shuffle(w)
        transaction_wallets = []
        total = 0
        i = 0
        while total < transaction_amount:
            transaction_wallets.append(w[i])
            total += w[i].balance

        # TODO select change address
        merchant.trade(transaction_amount, transaction_wallets)

    def step(self):
        self.simulate_transactions()


class Miner(Entity):
    def __init__(self, uid: int, model: MoneyModel, h: List[bool], t: float, mining_power: float):
        """
        Creates a Miner Agent
        :param h: The list of habits
        :param t: The temperature of operations
        :param mining_power: The mining power of the miner
        """
        super().__init__(uid, model, h, t)
        self.attributes.append('miner')
        self.mp = mining_power
        self.add_wallet()

    def mine(self):
        # TODO implement mining
        # Get wallet to mine to

        # register to model as an active miner

        # Register reward to wallet
        raise NotImplementedError('Mining not implemented')

    def sell(self):
        # TODO implement
        # Select an amount to sell
        # Select a Merchant based on popularity
        # Send amount to Merchant
        raise NotImplementedError('Miner selling not implemented')

    def step(self):
        self.mine()
        self.sell()


class Exchange(Entity):
    def __init__(self, uid: int, model: MoneyModel, popularity: float):
        # TODO
        raise NotImplementedError('Exchange Agent cannot be instantiated')
        pass

class Merchant(Entity):
    def __init__(self):
        # TODO
        raise NotImplementedError('Merchant cannot be instantiated')

    def get_habit_index(self) -> int:
        # TODO
        raise NotImplementedError('Merchant habit index')

    def trade(self, amount: float, wallets: List[Wallet]) -> bool:
        # TODO
        raise NotImplementedError('Merchant: Trade not implemented')



