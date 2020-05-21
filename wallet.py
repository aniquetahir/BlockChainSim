import uuid
from typing import List

class Wallet:
    key: str
    balance: float
    utxo: List[float]

    def __init__(self, model, key=None, balance=0):
        if key:
            self.key = key
        else:
            self.key = uuid.uuid4()
        self.model = model
        self.balance = balance
        self.utxo = [balance]

    def add_balance(self, amount: float) -> float:
        """
        Add currency to the wallet
        :param amount: The amount to add
        :return:
        """
        self.balance += amount
        self.utxo.append(amount)
        return self.balance

    def remove_balance(self, amount: float) -> bool:
        """
        Remove currency from the account
        :param amount: The amount to remove
        :return bool: A true/false value representing whether the transaction succeeded
        """
        if self.balance < amount:
            return False

        # https://github.com/bitcoin/bitcoin/blob/3015e0bca6bc2cb8beb747873fdf7b80e74d679f/src/wallet.cpp#L1276
        # Coin Selection Algorithm
        # If any of your UTXO² matches the Target¹ it will be used.
        matching_amount_utxo = [x for x in self.utxo if x == amount]
        if len(matching_amount_utxo) > 0:
            self.utxo.remove(amount)

        # If the "sum of all your UTXO smaller than the Target" happens to match the Target, they will be used.
        # (This is the case if you sweep a complete wallet.)
        elif sum([x for x in self.utxo if x < amount])==amount:
            for y in [x for x in self.utxo if x < amount]:
                if y < amount:
                    self.utxo.remove(y)

        # If the "sum of all your UTXO smaller than the Target" doesn't surpass the target,
        # the smallest UTXO greater than your Target will be used.
        # TODO Transaction Fee simulation
        elif sum([x for x in self.utxo if x < amount]) < amount:
            min_greater = min([x for x in self.utxo if x > amount])
            self.utxo.remove(min_greater)
            self.utxo.append(min_greater-amount)

        # Else Bitcoin Core does 1000 rounds of randomly combining unspent transaction outputs until their
        # sum is greater than or equal to the Target.
        # If it happens to find an exact match, it stops early and uses that.
        # https://github.com/bitcoin/bitcoin/blob/3015e0bca6bc2cb8beb747873fdf7b80e74d679f/src/wallet.cpp#L1129
        else:
            vfBest = [True] * len(self.utxo)
            nBest = self.balance
            nRep = 0
            while nRep<1000 and nBest != amount:
                vIncluded = [False] * len(self.utxo)
                nTotal = 0
                fReachedTarget = False
                nPass = 0
                while nPass<2 and not fReachedTarget:
                    for i in range(len(self.utxo)):
                        if nPass == 0 and self.model.random.choice([True, False]) or not vIncluded[i]:
                            nTotal += self.utxo[i]
                            vIncluded[i] = True
                            if nTotal >= amount:
                                fReachedTarget = True
                                if nTotal<nBest:
                                    nBest = nTotal
                                    vfBest = vIncluded
                                nTotal -= self.utxo[i]
                                vIncluded[i] = False
                    nPass+=1
                nRep+=1
            if nBest == amount:
                new_utxo = []
                for i, b in enumerate(vfBest):
                    if not b:
                        new_utxo.append(self.utxo[i])
                self.utxo = new_utxo
            else:
                # Otherwise it finally settles for the minimum of
                #     the smallest UTXO greater than the Target
                #     the smallest combination of UTXO it discovered in Step 4.
                greater_utxo = [x for x in self.utxo if x > amount]
                add_best_combo = False
                if len(greater_utxo) > 0:
                    min_greater = min(greater_utxo)
                    if nBest < min_greater:
                        add_best_combo=True
                    else:
                        self.utxo.remove(min_greater)
                        self.utxo.append(amount-min_greater)

                else:
                    add_best_combo=True

                if add_best_combo:
                    new_utxo = []
                    for i, b in enumerate(vfBest):
                        if not b:
                            new_utxo.append(self.utxo[i])
                    self.utxo = new_utxo
                    self.utxo.append(nBest-amount)

        self.balance -= amount
        return True
