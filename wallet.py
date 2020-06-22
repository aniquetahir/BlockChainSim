import uuid
from typing import List, Optional
import typing

if typing.TYPE_CHECKING:
    from blockchain import Block, Blockchain
    from transaction import Transaction

class Wallet:
    context: 'Blockchain'
    key: str
    balance: float
    utxo: List[float]

    def __init__(self, model, key=None, context: 'Blockchain' = None):
        if key:
            self.key = key
        else:
            self.key = uuid.uuid4()
        self.model = model
        # self.balance = balance
        # self.utxo = []
        self.context = context

    @property
    def utxo(self) -> List[float]:
        if not self.context:
            return []
        utxo = []
        inputs = []
        for block in self.context.blocks:
            running_utxo = [y[self.key] for x in block.transactions for y in x.outputs if self.key in y.keys()]
            for x in running_utxo:
                utxo.append(x)
        # get inputs which have the wallet key and remove them from utxo
        # TODO: Note: There is currently no id associated with a specific utxo, I am just randomly picking one which is
        # the same
        for block in self.context.blocks:
            running_inputs = [y[self.key] for x in block.transactions for y in x.inputs if self.key in y.keys()]
            for x in running_inputs:
                inputs.append(x)

        for i in inputs:
            utxo.remove(i)

        return utxo

    @property
    def balance(self) -> float:
        # Base case: no context return zero
        if not self.context:
            return 0
        # Get amount recieved and sent
        amount_received = 0
        amount_sent = 0
        for block in self.context.blocks:
            transactions: List['Transaction'] = block.transactions
            amount_received += sum([y[self.key] for x in transactions for y in x.outputs if self.key in y.keys()])
            amount_sent += sum([y[self.key] for x in transactions for y in x.inputs if self.key in y.keys()])

        # Return difference
        return amount_received - amount_sent

    def to_dict(self):
        # TODO
        return {
            'hash': self.key,
            'balance': self.balance,
            'utxo': self.utxo
        }

    def update_attributes(self, blockchain):
        raise NotImplementedError('update not implemented')

    def add_balance(self, amount: float) -> float:
        """
        Add currency to the wallet
        :param amount: The amount to add
        :return:
        """
        raise DeprecationWarning('Cannot add balance to a wallet. Add balance to a blockchain')
        # self.balance += amount
        # self.utxo.append(amount)
        # return self.balance

    def get_utxo(self, amount) -> (List[float], float):
        if self.balance < amount:
            return None

        t_utxo = self.utxo.copy()
        r_utxo = []
        # https://github.com/bitcoin/bitcoin/blob/3015e0bca6bc2cb8beb747873fdf7b80e74d679f/src/wallet.cpp#L1276
        # Coin Selection Algorithm
        # If any of your UTXO² matches the Target¹ it will be used.
        matching_amount_utxo = [x for x in t_utxo if x == amount]
        if len(matching_amount_utxo) > 0:
            r_utxo.append(amount)

        # If the "sum of all your UTXO smaller than the Target" happens to match the Target, they will be used.
        # (This is the case if you sweep a complete wallet.)
        elif sum([x for x in t_utxo if x < amount]) == amount:
            r_utxo = [x for x in t_utxo if x < amount]

        # If the "sum of all your UTXO smaller than the Target" doesn't surpass the target,
        # the smallest UTXO greater than your Target will be used.
        # TODO Transaction Fee simulation
        elif sum([x for x in t_utxo if x < amount]) < amount:
            min_greater = min([x for x in t_utxo if x > amount])
            t_utxo.append(min_greater)

        # Else Bitcoin Core does 1000 rounds of randomly combining unspent transaction outputs until their
        # sum is greater than or equal to the Target.
        # If it happens to find an exact match, it stops early and uses that.
        # https://github.com/bitcoin/bitcoin/blob/3015e0bca6bc2cb8beb747873fdf7b80e74d679f/src/wallet.cpp#L1129
        else:
            vfBest = [True] * len(t_utxo)
            nBest = self.balance
            nRep = 0
            while nRep < 1000 and nBest != amount:
                vIncluded = [False] * len(t_utxo)
                nTotal = 0
                fReachedTarget = False
                nPass = 0
                while nPass < 2 and not fReachedTarget:
                    for i in range(len(t_utxo)):
                        if nPass == 0 and self.model.random.choice([True, False]) or not vIncluded[i]:
                            nTotal += self.utxo[i]
                            vIncluded[i] = True
                            if nTotal >= amount:
                                fReachedTarget = True
                                if nTotal<nBest:
                                    nBest = nTotal
                                    vfBest = vIncluded
                                nTotal -= t_utxo[i]
                                vIncluded[i] = False
                    nPass+=1
                nRep+=1
            if nBest == amount:
                new_utxo = []
                for i, b in enumerate(vfBest):
                    if b:
                        new_utxo.append(t_utxo[i])
                r_utxo = new_utxo
            else:
                # Otherwise it finally settles for the minimum of
                #     the smallest UTXO greater than the Target
                #     the smallest combination of UTXO it discovered in Step 4.
                greater_utxo = [x for x in t_utxo if x > amount]
                add_best_combo = False
                if len(greater_utxo) > 0:
                    min_greater = min(greater_utxo)
                    if nBest < min_greater:
                        add_best_combo=True
                    else:
                        r_utxo.append(min_greater)

                else:
                    add_best_combo = True

                if add_best_combo:
                    new_utxo = []
                    for i, b in enumerate(vfBest):
                        if b:
                            r_utxo.append(t_utxo[i])

        return r_utxo, sum(r_utxo) - amount

    def remove_balance(self, amount: float) -> bool:
        """
        Remove currency from the account
        :param amount: The amount to remove
        :return bool: A true/false value representing whether the transaction succeeded
        """
        raise DeprecationWarning('Cannot remove balance directly from wallet. Please add corresponding transactions'
                                 'in the blockchain')

        # if self.balance < amount:
        #     return False

        # # https://github.com/bitcoin/bitcoin/blob/3015e0bca6bc2cb8beb747873fdf7b80e74d679f/src/wallet.cpp#L1276
        # # Coin Selection Algorithm
        # # If any of your UTXO² matches the Target¹ it will be used.
        # matching_amount_utxo = [x for x in self.utxo if x == amount]
        # if len(matching_amount_utxo) > 0:
        #     self.utxo.remove(amount)

        # # If the "sum of all your UTXO smaller than the Target" happens to match the Target, they will be used.
        # # (This is the case if you sweep a complete wallet.)
        # elif sum([x for x in self.utxo if x < amount])==amount:
        #     for y in [x for x in self.utxo if x < amount]:
        #         if y < amount:
        #             self.utxo.remove(y)

        # # If the "sum of all your UTXO smaller than the Target" doesn't surpass the target,
        # # the smallest UTXO greater than your Target will be used.
        # # TODO Transaction Fee simulation
        # elif sum([x for x in self.utxo if x < amount]) < amount:
        #     min_greater = min([x for x in self.utxo if x > amount])
        #     self.utxo.remove(min_greater)
        #     self.utxo.append(min_greater-amount)

        # # Else Bitcoin Core does 1000 rounds of randomly combining unspent transaction outputs until their
        # # sum is greater than or equal to the Target.
        # # If it happens to find an exact match, it stops early and uses that.
        # # https://github.com/bitcoin/bitcoin/blob/3015e0bca6bc2cb8beb747873fdf7b80e74d679f/src/wallet.cpp#L1129
        # else:
        #     vfBest = [True] * len(self.utxo)
        #     nBest = self.balance
        #     nRep = 0
        #     while nRep<1000 and nBest != amount:
        #         vIncluded = [False] * len(self.utxo)
        #         nTotal = 0
        #         fReachedTarget = False
        #         nPass = 0
        #         while nPass<2 and not fReachedTarget:
        #             for i in range(len(self.utxo)):
        #                 if nPass == 0 and self.model.random.choice([True, False]) or not vIncluded[i]:
        #                     nTotal += self.utxo[i]
        #                     vIncluded[i] = True
        #                     if nTotal >= amount:
        #                         fReachedTarget = True
        #                         if nTotal<nBest:
        #                             nBest = nTotal
        #                             vfBest = vIncluded
        #                         nTotal -= self.utxo[i]
        #                         vIncluded[i] = False
        #             nPass+=1
        #         nRep+=1
        #     if nBest == amount:
        #         new_utxo = []
        #         for i, b in enumerate(vfBest):
        #             if not b:
        #                 new_utxo.append(self.utxo[i])
        #         self.utxo = new_utxo
        #     else:
        #         # Otherwise it finally settles for the minimum of
        #         #     the smallest UTXO greater than the Target
        #         #     the smallest combination of UTXO it discovered in Step 4.
        #         greater_utxo = [x for x in self.utxo if x > amount]
        #         add_best_combo = False
        #         if len(greater_utxo) > 0:
        #             min_greater = min(greater_utxo)
        #             if nBest < min_greater:
        #                 add_best_combo=True
        #             else:
        #                 self.utxo.remove(min_greater)
        #                 self.utxo.append(amount-min_greater)

        #         else:
        #             add_best_combo=True

        #         if add_best_combo:
        #             new_utxo = []
        #             for i, b in enumerate(vfBest):
        #                 if not b:
        #                     new_utxo.append(self.utxo[i])
        #             self.utxo = new_utxo
        #             self.utxo.append(nBest-amount)

        # self.balance -= amount
        # return True


