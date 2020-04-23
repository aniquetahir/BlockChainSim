from typing import List, Dict
from wallet import Wallet
from mesa import Agent, Model
from MoneyModel import MoneyModel
from block import Block
import random


class Entity(Agent):
    wallets: List[Wallet]
    model: MoneyModel

    # TODO Agent constructor
    def __init__(self, uid: int, model: MoneyModel, h: List[bool], t: float, seller: int = -1):
        """
        :param h: A one-hot vector representing the habits of the user
        :param t: A temperature representing the frequency of transactions
        """
        super().__init__(uid, model)
        self.model = model
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

    def mine(self) -> Block:
        # TODO implement mining
        # Get wallet to mine to
        self.random.choice(self.wallets)

        # register a Block to the model
        # Get all transactions
        all_transactions = self.model.pending_transactions.copy()
        self.random.shuffle(all_transactions)
        # Pick 500 transactions
        block_transactions = all_transactions[:500]

        blockchain = self.model.blockchain
        last_block_id = blockchain.get_tail().id
        block = Block(last_block_id, block_transactions)

        return block

    def sell(self):
        # TODO implement
        # Select an amount to sell
        sell_amount = self.get_total_wealth() * self.random.random()

        # Select a Exchange based on popularity
        exchanges = [x for x in self.model.schedule.agents if isinstance(x, Exchange)]
        exchange_to_sell: Exchange = self.random.choice(exchanges, [x.popularity for x in exchanges])[0]

        exchange_to_sell.sell(sell_amount)

    def step(self):
        self.mine()
        self.sell()


class Exchange(Entity):
    popularity: float

    def __init__(self, uid: int, model: MoneyModel, popularity: float):
        # TODO
        raise NotImplementedError('Exchange Agent cannot be instantiated')
        pass

    def buy(self, amount):
        raise NotImplementedError('Exchange: Buy not implemented')

    def sell(self, amount):
        raise NotImplementedError('Exchange: Sell not implemented')


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



