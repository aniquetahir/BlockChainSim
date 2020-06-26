from __future__ import annotations
from collections import defaultdict
from typing import List, Dict, Union
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

    def to_dict(self):
        return {
            'id': self.unique_id,
            'habits': self.habits,
            'blockchain': self.blockchain.to_dict(),
            'temperature': self.temperature,
            'wallets': [x.to_dict() for x in self.wallets],
            'attributes': self.attributes,
            'type': 'Entity'
        }

    def tx_from_wallets(self, amount: float,
                        from_wallets: List[Wallet], to_wallet: Wallet, change_wallet: Wallet,
                        context=None) -> Transaction:
        """

        :rtype: Transaction
        """
        if not context:
            context = self.blockchain

        wallets = from_wallets.copy()
        for w in wallets:
            w.context = context

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
            # if sum(i.utxo) > i.balance:
            #     print('wtf')
            #     print(i.utxo)
            #     print(i.balance)
            one_from = [{'address': i.key, 'amount': x} for x in i.utxo]
            for j in one_from:
                transactions_from.append(j)

        running_total = sum([x.balance for x in sending_wallets[:-1]])

        final_utxo, final_change = sending_wallets[-1].get_utxo(amount - running_total)
        final_key = sending_wallets[-1].key
        self.random.shuffle(final_utxo)

        for i in final_utxo:
            transactions_from.append({'address': final_key, 'amount': i})

        # for i in final_utxo:
        #     transactions_from.append({'address': final_key, 'amount': i})
        #     running_total += i
        #     if running_total > amount:
        #         break

        change = final_change

        # Create a change address
        # change_wallet = Wallet(self.model)

        transactions_to = [{'address': change_wallet.key, 'amount': change},
                           {'address': to_wallet.key, 'amount': amount}]

        transaction = Transaction(transactions_from, transactions_to)
        return transaction

    def add_wallet(self, key=None) -> Wallet:
        w = Wallet(self.model, key, self.blockchain)
        self.wallets.append(w)
        return w

    def get_total_wealth(self, context=None) -> float:
        if not context:
            context = self.blockchain
        wallets = self.wallets.copy()
        for w in wallets:
            w.context = context
        return sum([x.balance for x in wallets])

    def simulate_transactions(self):
        self.refresh_wallet_context()
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
                amount = max(round(self.random.gauss(self.model.AVG_TRANSACTION, self.model.WEALTH_SD), 4), 0)

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

        transaction_amount = round(self.random.random() * self.get_total_wealth(), 5)
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
            i += 1

        change_wallet = Wallet(self.model, context=self.blockchain)

        if transaction_amount > 0 and merchant.trade(transaction_amount, transaction_wallets, change_wallet):
            self.wallets.append(change_wallet)

    def refresh_wallet_context(self, context=None):
        if not context:
            context = self.blockchain
        for w in self.wallets:
            w.context = context

    def common(self):
        # TODO Get blocks from the agents themselves
        agents = self.model.schedule.agents
        cb = [a.blockchain for a in agents]
        # cb = self.model.candidate_blocks

        # Filter out blocks which are inconsistent

        if len(cb) > 0:
            # TODO Get the blocks as a longest chain from a random subset
            blockchain_options: List[Blockchain] = self.random.choices(cb, [len(x) for x in cb])
            # while not blockchain_options[0].block_exists(self.blockchain.get_tail()):
            #     blockchain_options: List[Blockchain] = self.random.choices(cb, [len(x) for x in cb])
            if len(self.blockchain) < len(blockchain_options[0]):
                self.blockchain = copy(blockchain_options[0])

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

    def to_dict(self):
        m_dict = super(Miner, self).to_dict()
        m_dict['type'] = 'Miner'
        m_dict['mp'] = self.mp
        return m_dict

    def validate_transactions(self, txs: List[Transaction]) -> bool:
        # Get all wallets
        wallets: Dict[str, float] = {}
        for agent in self.model.schedule.agents:
            agent: Entity
            t_wallets = agent.wallets
            for w in t_wallets:
                w.context = self.blockchain
                wallets[w.key] = w.balance
        # Update the balance of wallets according to the current chain

        # for each transaction, see how the balance changes in order
        for tx in txs:
            for i in tx.inputs:
                wallets[i['address']] -= i['amount']
                if wallets[i['address']] < 0:
                    return False
            for o in tx.outputs:
                wallets[o['address']] += o['amount']
        #   if there is negative balance for a wallet at a particular transaction return False
        # Otherwise return True
        return True

    def get_valid_tx_subset(self, txs: List[Transaction]) -> List[Transaction]:
        wallets: Dict[str, List[float]] = {}
        for agent in self.model.schedule.agents:
            agent: Entity
            t_wallets = agent.wallets
            for w in t_wallets:
                w.context = self.blockchain
                wallets[w.key] = w.utxo
        # Update the balance of wallets according to the current chain
        valid_subset = []
        for tx in txs:
            tx_valid = True
            for i in tx.inputs:
                if i['amount'] in wallets[i['address']]:
                    wallets[i['address']].remove(i['amount'])
                else:
                    tx_valid = False
                    break
            if not tx_valid:
                continue
            for o in tx.outputs:
                wallets[o['address']].append(o['amount'])
            valid_subset.append(tx)
        return valid_subset

    def mine(self) -> Union[Block, None]:
        # TODO implement mining
        # Get wallet to mine to
        mine_wallet: Wallet = self.random.choice(self.wallets)

        # register a Block to the model
        # Get all transactions
        all_transactions = [x for x in self.model.pending_transactions if not self.blockchain.transaction_exists(x)]

        self.random.shuffle(all_transactions)
        # Pick 500 transactions
        block_transactions = all_transactions[:500]

        block_transactions = self.get_valid_tx_subset(block_transactions)
        # TODO check that the transactions are valid i.e. the wallets are spending the amount that they have
        if not self.validate_transactions(block_transactions):
            return None

        # add mining reward to the block
        reward_transaction = Transaction([{'address': 'reward', 'amount': self.model.BLOCK_MINING_REWARD}],
                                         [{'address': mine_wallet.key, 'amount': self.model.BLOCK_MINING_REWARD}],
                                         'reward')

        block_transactions.append(reward_transaction)

        # blockchain = self.model.blockchain
        blockchain = self.blockchain
        last_block_id = blockchain.get_tail().id
        block = Block(last_block_id, block_transactions)

        return block

    def sell(self):
        self.refresh_wallet_context()
        # Select an amount to sell
        sell_amount = round(self.get_total_wealth() * self.random.random(), 4)

        # Select a Exchange based on popularity
        exchanges = [x for x in self.model.schedule.agents if isinstance(x, Exchange)]
        if len(exchanges) == 0:
            return

        # Randomly select exchanges based on their popularity
        # TODO exchange preferences based on agents can be implemented
        exchange_to_sell: Exchange = self.random.choices(exchanges, [x.popularity for x in exchanges])[0]

        change_wallet = Wallet(self.model, context=self.blockchain)
        if exchange_to_sell.sell(sell_amount, self.wallets, change_wallet):
            self.wallets.append(change_wallet)

    def substep(self):
        blocks = []
        while self.random.random() < self.mp:
            block = self.mine()
            if block:
                blocks.append(block)
                self.blockchain.add(block)

        # if len(blocks) > 0:
        #     self.model.candidate_blocks.append(self.blockchain)

        self.sell()


class Exchange(Entity):
    popularity: float

    def __init__(self, uid: int, model, popularity: float):
        super(Exchange, self).__init__(uid, model, [], 0)
        self.popularity = popularity

    def to_dict(self):
        m_dict = super(Exchange, self).to_dict()
        m_dict['popularity'] = self.popularity
        return m_dict

    def buy(self, amount: float, wallet: Wallet) -> bool:
        self.refresh_wallet_context()
        # Randomly select wallets till the amount>buy amount
        if self.get_total_wealth() < amount or amount == 0:
            return False

        change_wallet = Wallet(self.model, context=self.blockchain)
        self.wallets.append(change_wallet)

        transaction = self.tx_from_wallets(amount, self.wallets, wallet, change_wallet)
        transaction.memo = "buying from exchange"

        # Add to pending transactions
        self.model.pending_transactions.append(transaction)
        return True

    def sell(self, amount: float, wallets: List[Wallet], change_wallet: Wallet):
        # self.refresh_wallet_context()
        # TODO decide on which context to use. presently using the sellers context
        total = sum([x.balance for x in wallets])
        if total < amount or amount == 0:
            return False

        # Randomly select a wallet
        if len(self.wallets) == 0:
            deposit_wallet = Wallet(self.model, context=wallets[0].context)
            self.wallets.append(deposit_wallet)
        else:
            deposit_wallet = self.random.choice(self.wallets)

        transactions = self.tx_from_wallets(amount, wallets, deposit_wallet, change_wallet, context=wallets[0].context)
        transactions.memo = 'selling to exchange'

        self.model.pending_transactions.append(transactions)
        return True

    def substep(self):
        # TODO For now exchange does not make any profits or perform independent operations other than buying or selling
        pass


class Merchant(Entity):
    def __init__(self, uid, model, h, popularity):
        super(Merchant, self).__init__(uid, model, h, popularity, True)
        # TODO Distribution for merchant items prices can be used
        self.popularity = popularity

    def to_dict(self):
        m_dict = super(Merchant, self).to_dict()
        m_dict['popularity'] = self.popularity
        return m_dict

    def get_habit_indices(self) -> List[int]:
        return [i for i, x in enumerate(self.habits) if x]

    # def get_habit_index(self) -> int:
    #     raise NotImplementedError('Merchant habit index')

    def trade(self, amount: float, wallets: List[Wallet], change_wallet: Wallet) -> bool:
        # self.refresh_wallet_context()
        # TODO decide on the context to use. presently using the callers context
        total = sum([x.balance for x in wallets])
        if total < amount:
            return False

        # Randomly select a wallet
        if len(self.wallets) == 0:
            deposit_wallet = Wallet(self.model, context=wallets[0].context)
            self.wallets.append(deposit_wallet)
        else:
            deposit_wallet = self.random.choice(self.wallets)

        transactions = self.tx_from_wallets(amount, wallets, deposit_wallet, change_wallet, context=wallets[0].context)
        transactions.memo = "trading with a merchant"

        self.model.pending_transactions.append(transactions)

        return True

    def substep(self):
        # TODO merchant doesn't do anything independently for now
        pass
