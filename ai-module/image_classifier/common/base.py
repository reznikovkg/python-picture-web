from typing import Any, List, Tuple
from enum import Enum
import numpy as np


class Applier:

    def apply(self, value: Any) -> Any:
        pass


class SkinLesion(Enum):
    AK = 0
    BCC = 1
    BKL = 2
    DF = 3
    MEL = 4
    NV = 5
    SCC = 6
    VASC = 7

    @staticmethod
    def value_of(probabilities: np.ndarray) -> (str, float):
        max_index = np.argmax(probabilities)
        # max_probability = probabilities[max_index]
        for lesion in SkinLesion:
            if lesion.value == max_index:
                return lesion.name, probabilities
        return "UNK", probabilities


class ImageClassifierBySkinLesion(Applier):

    def apply(self, image_data: bytes) -> Tuple[List[SkinLesion], SkinLesion]:
        pass
