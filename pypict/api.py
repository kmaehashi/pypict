from typing import Iterable, Iterator, List, Optional, Tuple

from pypict import capi


class Task:
    def __init__(self, seed: Optional[int] = None):
        self.handle = capi.createTask()
        self._model = _Model(seed)
        capi.setRootModel(self.handle, self._model.handle)

    def __del__(self) -> None:
        if self.handle != 0:
            capi.deleteTask(self.handle)

    @property
    def model(self) -> '_Model':
        return self._model

    def add_exclusion(self, items: Iterable[Tuple[int, int]]) -> None:
        capi.addExclusion(self.handle, tuple(items))

    def add_seed(self, items: Iterable[Tuple[int, int]]) -> None:
        capi.addSeed(self.handle, tuple(items))

    def generate(self) -> '_ResultSet':
        capi.generate(self.handle)
        return _ResultSet(self)

    def get_total_parameter_count(self) -> int:
        return capi.getTotalParameterCount(self.handle)


class _Model:
    def __init__(self, seed: Optional[int] = None):
        if seed is None:
            seed = capi.DEFAULT_RANDOM_SEED
        self.handle = capi.createModel(seed)
        self._owned = True

    def __del__(self) -> None:
        if self.handle != 0 and self._owned:
            capi.deleteModel(self.handle)

    def add_parameter(
            self,
            count: int,
            order: int = capi.PAIRWISE_GENERATION,
            weights: Optional[Iterable[int]] = None) -> int:
        if weights is not None:
            weights = tuple(weights)
        return capi.addParameter(self.handle, count, order, weights)

    def attach_child_model(self, order: int, seed: Optional[int] = None) -> '_Model':
        if seed is None:
            seed = capi.DEFAULT_RANDOM_SEED
        childModel = _Model(seed)
        capi.attachChildModel(self.handle, childModel.handle, order)
        childModel._owned = False
        return childModel


class _ResultSet:
    def __init__(self, task: Task):
        self._task = task

    def __iter__(self) -> Iterator[List[int]]:
        capi.resetResultFetching(self._task.handle)
        buf = capi.allocateResultBuffer(self._task.handle)
        try:
            while True:
                remaining = capi.getNextResultRow(self._task.handle, buf)
                if remaining == 0:
                    break
                yield list(buf)
        finally:
            capi.freeResultBuffer(buf)
