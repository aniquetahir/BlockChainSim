from typing import List, Dict
from block import Block
from transaction import Transaction
from copy import copy


class Blockchain:
    blocks: List[Block]
    hash: str

    # TODO Model constructor
    def __init__(self, genesis: Block):
        self.blocks = [genesis]

    def hash(self) -> str:
        return self.get_tail().id

    def to_dict(self):
        return {
            'blocks': [x.to_dict() for x in self.blocks],
            'hash': self.get_tail().id
        }

    def get_tail(self) -> Block:
        return self.blocks[-1]

    def get_block(self, identifier: str) -> Block:
        for block in self.blocks:
            if block.id == identifier:
                return block
        raise BlockNotFoundException

    def transaction_exists(self, tr: Transaction) -> bool:
        for block in self.blocks:
            if block.transaction_exists(tr):
                return True
        return False

    def block_exists(self, b: Block) -> bool:
        for block in self.blocks:
            if block.id == b.id:
                return True
        return False

    def __len__(self):
        return len(self.blocks)

    def add(self, block: Block):
        # TODO resolve conflicts
        last_block = self.get_tail()
        block.prev = last_block.id
        self.blocks.append(block)

    def __copy__(self) -> 'Blockchain':
        # TODO implement this
        bc_copy = Blockchain(self.blocks[0])
        bc_copy.blocks = copy(self.blocks)
        return bc_copy

    def queue_transaction(self):
        raise NotImplementedError("Blockchain: Transaction queuing not implemented")


class BlockNotFoundException(Exception):
    def __init__(self, message: str):
        super(message)

