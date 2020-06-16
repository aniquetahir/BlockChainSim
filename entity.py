from __future__ import annotations
from typing import List, Dict
from wallet import Wallet
from mesa import Agent, Model
# from MoneyModel import MoneyModel
from block import Block
from blockchain import Blockchain
import random
from transaction import Transaction
import typing
from copy import copy

if typing.TYPE_CHECKING:
    from MoneyModel import MoneyModel


class Entity(Agent):
    wallets: List[Wallet]

    # TODO Agent constructor
    def __init__(self, uid: int, model: 'MoneyModel', h: List[bool], t: float, seller=False):
        """
        :param h: A one-hot vector representing the habits of the user
        :param t: A temperature representing the frequency of transactions
        """
        super().__init__(uid, model)
        self.model = model
        self.habits = h
        self.blockchain = copy(self.model.blockchain)
        self.temperature = t
        self.wallets = [Wallet(model)]  # Give each agent at least one empty wallet
        self.attributes = []
        self.seller = seller
        self.add_wallet()

    def tx_from_wallets(self, amount: float,
                        from_wallets: List[Wallet], to_wallet: Wallet, change_wallet: Wallet) -> Transaction:
        """

        :rtype: Transaction
        """
        wallets = from_wallets.copy()
        self.random.shuffle(wallets)

        sending_wallets = []
        t_amount = 0
        i = 0

        while t_amount < amount:
            sending_wallets.append(wallets[i])
            t_amount += wallets[i].balance
            i += 1

        # Create a list of transactions
        transactions_from = []
        for i in sending_wallets[:-1]:
            one_from = [{'address': i.key, 'amount': x} for x in i.utxo]
            for j in one_from:
                transactions_from.append(j)

        running_total = sum([x.balance for x in sending_wallets[:-1]])

        final_utxo = sending_wallets[-1].utxo.copy()
        final_key = sending_wallets[-1].key
        self.random.shuffle(final_utxo)

        for i in final_utxo:
            transactions_from.append({'address': final_key, 'amount': i})
            running_total += i
            if running_total > amount:
                break

        change = running_total - amount

        # Create a change address
        # change_wallet = Wallet(self.model)

        transactions_to = [{'address': change_wallet.key, 'amount': change},
                           {'address': to_wallet.key, 'amount': amount}]

        transaction = Transaction(transactions_from, transactions_to)
        return transaction

    def add_wallet(self, amount=0, key=None) -> Wallet:
        w = Wallet(key, amount)
        self.wallets.append(w)
        return w

    def get_total_wealth(self) -> float:
        return sum([x.balance for x in self.wallets])

    def simulate_transactions(self):
        # Buy currency using exchange
        buy_decision = self.random.random()
        if buy_decision < 0.5:
            # Select an appropriate exchange
            exchanges = [x for x in self.model.schedule.agents if isinstance(x, Exchange)]
            if len(exchanges) > 0:
                exchange = self.random.choice(exchanges)

                # Select a wallet to send to
                buy_wallet = self.random.choice(self.wallets)

                # Select an amount to buy
                amount = max(self.random.gauss(self.model.AVG_TRANSACTION, self.model.WEALTH_SD), 0)

                exchange.buy(amount, buy_wallet)

        # See if the agent makes a transaction based on the temperature
        if self.temperature < self.random.random():
            return

        # Randomly select a habit to spend on
        habit = self.random.choice([i for i, x in enumerate(self.habits) if x])
        # Select a vendor for the habit
        # TODO vendor favorism
        merchants = [x for x in self.model.schedule.agents
                     if isinstance(x, Merchant) and habit in x.get_habit_indices()]
        if len(merchants) == 0:
            return

        transaction_amount = random.random() * self.get_total_wealth()
        merchants_available = self.random.choices(merchants, [x.popularity for x in merchants])
        if len(merchants_available) == 0:
            return

        merchant: Merchant = merchants_available[0]
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

        change_wallet = Wallet(self.model)

        if merchant.trade(transaction_amount, transaction_wallets, change_wallet):
            self.wallets.append(change_wallet)

    def common(self):
        # TODO accept or reject blocks
        cb = self.model.candidate_blocks

        # Filter out blocks which are inconsistent

        if len(self.model.candidate_blocks)>0:
            blockchain_options: List[Blockchain] = random.choices(cb, [len(x) for x in cb])
            while not blockchain_options[0].block_exists(self.blockchain.get_tail()):
                blockchain_options: List[Blockchain] = random.choices(cb, [len(x) for x in cb])

            self.blockchain = copy(blockchain_options[0])

        pass

    def step(self):
        self.common()
        self.substep()

    def substep(self):
        self.simulate_transactions()


class Miner(Entity):
    def __init__(self, uid: int, model: 'MoneyModel', h: List[bool], t: float, mining_power: float):
        """
        Creates a Miner Agent
        :param h: The list of habits
        :param t: The temperature of operations
        :param mining_power: The mining power of the miner
        """
        super(Miner, self).__init__(uid, model, h, t)
        self.attributes.append('miner')
        self.mp = mining_power
        self.add_wallet()

    def mine(self) -> Block:
        # TODO implement mining
        # Get wallet to mine to
        self.random.choice(self.wallets)

        # register a Block to the model
        # Get all transactions
        all_transactions = [x for x in self.model.pending_transactions if not self.blockchain.transaction_exists(x)]

        self.random.shuffle(all_transactions)
        # Pick 500 transactions
        block_transactions = all_transactions[:500]

        #blockchain = self.model.blockchain
        blockchain = self.blockchain
        last_block_id = blockchain.get_tail().id
        block = Block(last_block_id, block_transactions)

        return block

    def sell(self):
        # TODO implement
        # Select an amount to sell
        sell_amount = self.get_total_wealth() * self.random.random()

        # Select a Exchange based on popularity
        exchanges = [x for x in self.model.schedule.agents if isinstance(x, Exchange)]
        if len(exchanges) == 0:
            return
        exchange_to_sell: Exchange = self.random.choice(exchanges, [x.popularity for x in exchanges])[0]

        change_wallet = Wallet(self.model)
        if exchange_to_sell.sell(sell_amount, self.wallets, change_wallet):
            self.wallets.append(change_wallet)

    def substep(self):
        blocks = []
        while self.random.random() < self.mp:
            block = self.mine()
            blocks.append(block)
            self.blockchain.add(block)

        if len(blocks) > 0:
            self.model.candidate_blocks.append(self.blockchain)
            
        self.sell()


class Exchange(Entity):
    popularity: float

    def __init__(self, uid: int, model, popularity: float):
        super(Exchange, self).__init__(uid, model, [], 0)
        self.popularity = popularity

    def buy(self, amount: float, wallet: Wallet) -> bool:
        # Randomly select wallets till the amount>buy amount
        if self.get_total_wealth() < amount:
            return False

        change_wallet = Wallet(self.model)
        self.wallets.append(change_wallet)

        transaction = self.tx_from_wallets(amount, self.wallets, wallet, change_wallet)

        # Add to pending transactions
        self.model.pending_transactions.append(transaction)
        return True

    def sell(self, amount: float, wallets: List[Wallet], change_wallet: Wallet):
        total = sum([x.balance for x in wallets])
        if total < amount:
            return False

        # Randomly select a wallet
        if len(self.wallets) == 0:
            deposit_wallet = Wallet(self.model)
            self.wallets.append(deposit_wallet)
        else:
            deposit_wallet = self.random.choice(self.wallets)

        transactions = self.tx_from_wallets(amount, wallets, deposit_wallet, change_wallet)

        self.model.pending_transactions.append(transactions)
        return True

    def substep(self):
        # TODO For now exchange does not make any profits
        pass


class Merchant(Entity):
    def __init__(self, uid, model, h, popularity):
        super(Merchant, self).__init__(uid, model, h, popularity, True)
        self.popularity = popularity

    def get_habit_indices(self) -> List[int]:
        return [i for i, x in enumerate(self.habits) if x]

    # def get_habit_index(self) -> int:
    #     raise NotImplementedError('Merchant habit index')

    def trade(self, amount: float, wallets: List[Wallet], change_wallet: Wallet) -> bool:
        total = sum([x.balance for x in wallets])
        if total < amount:
            return False

        # Randomly select a wallet
        if len(self.wallets) == 0:
            deposit_wallet = Wallet(self.model)
            self.wallets.append(deposit_wallet)
        else:
            deposit_wallet = self.random.choice(self.wallets)

        transactions = self.tx_from_wallets(amount, wallets, deposit_wallet, change_wallet)

        self.model.pending_transactions.append(transactions)

        return True

    def substep(self):
        # TODO merchant doesn't do anything independently for now
        pass



