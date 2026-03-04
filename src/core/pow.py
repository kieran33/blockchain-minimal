from __future__ import annotations
from dataclasses import dataclass
from .block import Block


@dataclass
class ProofOfWork:
    difficulty: int = 3  # simple

    def mine(self, block: Block) -> Block:
        prefix = "0" * self.difficulty
        block.seal()
        while not block.hash.startswith(prefix):
            block.nonce += 1
            block.seal()
        return block