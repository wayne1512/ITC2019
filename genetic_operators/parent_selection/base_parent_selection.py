from abc import ABC, abstractmethod


class BaseParentSelection(ABC):
    @abstractmethod
    def select(self, costs, count):
        pass
