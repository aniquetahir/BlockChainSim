from typing import List, Dict, TypeVar, Union
from uuid import uuid4


class Transaction:
    def __init__(self, inputs: List[Dict[str, Union[str, float]]], outputs: List[Dict[str, Union[str, float]]],
                 memo: str = None):
        """
        :param inputs: The inputs are a List of {address: amount}
        :param outputs: The outputs are a List of {address: amount}
        """
        self.id = str(uuid4())
        self.inputs = inputs
        self.outputs = outputs
        self.memo = memo
        is_fine = self._verify()
        if not is_fine:
            print(self.inputs)
            print(self.outputs)
            raise Exception('Error in transaction')

    def to_dict(self):
        return {
            'hash': self.id,
            'inputs': self.inputs,
            'outputs': self.outputs
        }

    def _verify(self) -> bool:
        input_sum = sum([abs(x['amount']) for x in self.inputs])
        output_sum = sum([abs(x['amount']) for x in self.outputs])

        return abs(input_sum - output_sum) < 0.0000001


