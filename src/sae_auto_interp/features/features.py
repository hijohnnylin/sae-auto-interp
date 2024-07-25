from dataclasses import dataclass
from typing import List, Tuple
import torch
from tqdm import tqdm
import orjson
import blobfile as bf
from collections import defaultdict
from typing import List, Callable
from ..logger import logger
from torch import Tensor
from torchtyping import TensorType

@dataclass
class Example:
    tokens: TensorType["seq"]
    activations: TensorType["seq"]
    
    def __hash__(self) -> int:
        return hash(tuple(self.tokens.tolist()))

    def __eq__(self, other: 'Example') -> bool:
        return self.tokens == other.tokens
    
    @property
    def max_activation(self):
        return max(self.activations)

    @staticmethod
    def prepare_examples(tokens, activations):
        return [
            Example(
                tokens=toks,
                activations=acts,
            )
            for toks, acts in zip(
                tokens, 
                activations
            )
        ]

@dataclass
class Feature:
    module_name: int
    feature_index: int
    
    def __repr__(self) -> str:
        return f"{self.module_name}_feature{self.feature_index}"
    
class FeatureRecord:

    def __init__(
        self,
        feature: Feature,
    ):
        self.feature = feature

    @property
    def max_activation(self):
        return self.examples[0].max_activation
    
    def load_processed(self, directory: str):
        path = f"{directory}/{self.feature}.json"

        with bf.BlobFile(path, "rb") as f:
            processed_data = orjson.loads(f.read())
            self.__dict__.update(processed_data)
    
    def save(self, directory: str, save_examples=False):
        path = f"{directory}/{self.feature}.json"
        serializable = self.__dict__

        if not save_examples:
            serializable.pop("examples")
            serializable.pop("train")
            serializable.pop("test")

        serializable.pop("feature")
        with bf.BlobFile(path, "wb") as f:
            f.write(orjson.dumps(serializable))


