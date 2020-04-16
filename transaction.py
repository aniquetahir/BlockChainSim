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

    def _verify(self) -> bool:
        input_sum = sum([y for x, y in self.inputs])
        output_sum = sum([y for x, y in self.inputs])

        return input_sum == output_sum
