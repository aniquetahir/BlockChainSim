from typing import List, Dict, TypeVar
from uuid import uuid4


class Transaction:
    def __init__(self, inputs: List[Dict[str, float]], outputs: List[Dict[str, float]]):
        """
        :param inputs: The inputs are a List of {address: amount}
        :param outputs: The outputs are a List of {address: amount}
        """
        self.id = str(uuid4())
        self.inputs = inputs
        self.outputs = outputs
        is_fine = self._verify()
        if not is_fine:
            raise Exception('Error in transaction')

    def to_dict(self):
        return {
            'hash': self.id,
            'inputs': self.inputs,
            'outputs': self.outputs
        }

    def _verify(self) -> bool:
        input_sum = sum([z for x in self.inputs for y, z in x.items()])
        output_sum = sum([z for x in self.inputs for y, z in x.items()])

        return input_sum == output_sum


