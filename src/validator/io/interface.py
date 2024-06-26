from typing import Any

from abc import ABC, abstractmethod

class IOInterface(ABC):
    
    @abstractmethod
    def path_exists(self, path: str) -> bool:
        pass

    @abstractmethod
    def make_dir(self, path: str, mode: int = 511, exist_ok: bool = False):
        pass

    @abstractmethod
    def write_json_file(self, path: str, body: Any):
        pass

    @abstractmethod
    def read_json_file(self, path: str) -> Any | None:
        pass