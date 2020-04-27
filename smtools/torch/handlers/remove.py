from typing import List
from pathlib import Path

from ignite.engine import Engine


def remove(trainer: Engine, patterns: List[str]):
    for pattern in patterns:
        for path in Path("/").glob(pattern.lstrip("/")):
            path.unlink()
