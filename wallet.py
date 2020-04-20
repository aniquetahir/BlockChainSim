import uuid
from typing import List

class Wallet:
    key: str
    balance: float
    utxo: List[float]

    def __init__(self, key=None, balance=0):
        if key:
            self.key = key
        else:
            self.key = uuid.uuid4()
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

        # Else Bitcoin Core does 1000 rounds of randomly combining unspent transaction outputs until their
        # sum is greater than or equal to the Target.
        # If it happens to find an exact match, it stops early and uses that.

        # Otherwise it finally settles for the minimum of
        #     the smallest UTXO greater than the Target
        #     the smallest combination of UTXO it discovered in Step 4.

        if self.balance >= amount:
            self.balance -= amount
            return True
        else:
            return False
