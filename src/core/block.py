from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import List, Dict, Any
import time

from src.crypto.hashing import hash_json, merkle_root
from .transaction import Transaction


@dataclass
class Block:
    index: int
    timestamp: float
    previousHash: str
    transactions: List[Transaction]
    nonce: int = 0
    merkleRoot: str = ""
    hash: str = ""

    def compute_merkle(self) -> str:
        tx_hashes = [tx.tx_hash() for tx in self.transactions]
        return merkle_root(tx_hashes)

    def compute_hash(self) -> str:
        data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "previousHash": self.previousHash,
            "nonce": self.nonce,
            "merkleRoot": self.merkleRoot,
            "txHashes": [tx.tx_hash() for tx in self.transactions],
        }
        return hash_json(data)

    def seal(self) -> None:
        self.merkleRoot = self.compute_merkle()
        self.hash = self.compute_hash()

    def validate(self) -> bool:
        # vérifie merkle root, hash, et tx signatures
        if self.merkleRoot != self.compute_merkle():
            return False
        if self.hash != self.compute_hash():
            return False
        for tx in self.transactions:
            if not tx.verify():
                return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "previousHash": self.previousHash,
            "transactions": [t.to_dict() for t in self.transactions],
            "nonce": self.nonce,
            "merkleRoot": self.merkleRoot,
            "hash": self.hash,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Block":
        txs = [Transaction.from_dict(x) for x in d["transactions"]]
        return Block(
            index=int(d["index"]),
            timestamp=float(d["timestamp"]),
            previousHash=d["previousHash"],
            transactions=txs,
            nonce=int(d.get("nonce", 0)),
            merkleRoot=d.get("merkleRoot", ""),
            hash=d.get("hash", ""),
        )

    @staticmethod
    def genesis() -> "Block":
        b = Block(index=0, timestamp=time.time(), previousHash="0"*64, transactions=[], nonce=0)
        b.seal()
        return b