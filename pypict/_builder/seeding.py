from typing import Dict


class SeedGenerator:
    def __init__(self, model):
        self._model = model
        self._seeds = []

    def seed(self, case: Dict):
        self._seeds.append(
            (case[x] if x in case else None for x in self._model._parameters))

    def to_string(self):
        pass
