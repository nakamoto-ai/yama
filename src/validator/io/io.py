"""
Author: Eddie
"""

import os 
import json
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


class IO(IOInterface):

    def path_exists(self, path: str) -> bool:
        return os.path.exists(path)

    def make_dir(self, path: str, mode: int = 511, exist_ok: bool = False):
        os.makedirs(path)

    def write_json_file(self, path: str, body: Any):
        with open(path, 'w') as file:
            json.dump(body, file, indent=4)

    def read_json_file(self, path: str) -> Any | None:
        with open(path, 'r') as file:
            data = json.load(file)

        return data
