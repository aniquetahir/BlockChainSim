from typing import List, Dict
from block import Block


class Blockchain:
    blocks: List[Block]

    def __init__(self, genesis: Block):
        self.blocks = [genesis]

    def get_tail(self) -> Block:
        return self.blocks[-1]

    def get_block(self, identifier: str) -> Block:
        for block in self.blocks:
            if block.id == identifier:
                return block
        raise BlockNotFoundException

    def add(self, block: Block):
        last_block = self.get_tail()
        block.prev = last_block.id
        self.blocks.append(block)


class BlockNotFoundException(Exception):
    def __init__(self, message: str):
        super(message)

