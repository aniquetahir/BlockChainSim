import uuid


class Wallet:
    def __init__(self, key=None, balance=0):
        if key:
            self.key = key
        else:
            self.key = uuid.uuid4()
        self.balance = balance

    def add_balance(self, amount: int):
        """
        Add currency to the wallet
        :param amount: The amount to add
        :return:
        """
        self.balance += amount

    def remove_balance(self, amount: int) -> bool:
        """
        Remove currency from the account
        :param amount: The amount to remove
        :return bool: A true/false value representing whether the transaction succeeded
        """
        if self.balance >= amount:
            self.balance -= amount
            return True
        else:
            return False
