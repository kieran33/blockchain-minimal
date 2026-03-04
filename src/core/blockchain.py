from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
import os
import json
import time

from .block import Block
from .transaction import Transaction
from .state import State
from .pow import ProofOfWork


@dataclass
class Blockchain:
    chain: List[Block] = field(default_factory=list)
    pendingTransactions: List[Transaction] = field(default_factory=list)
    state: State = field(default_factory=State)
    pow: ProofOfWork = field(default_factory=lambda: ProofOfWork(difficulty=3))
    mining_reward: int = 100

    def __post_init__(self) -> None:
        if not self.chain:
            self.chain = [Block.genesis()]

    def last_block(self) -> Block:
        return self.chain[-1]

    def addTransaction(self, tx: Transaction) -> bool:
        if not tx.verify():
            return False

        # Anti-rejeu minimal via nonce
        if tx.fromAddress != "COINBASE":
            last = self.state.last_nonce_by_sender.get(tx.fromAddress, -1)
            if tx.nonce <= last:
                return False

            # check funds
            if self.state.get_balance(tx.fromAddress) < tx.amount:
                return False

        self.pendingTransactions.append(tx)
        return True

    def apply_transaction_to_state(self, tx: Transaction) -> bool:
        if not tx.verify():
            return False

        if tx.fromAddress != "COINBASE":
            # nonce update
            self.state.last_nonce_by_sender[tx.fromAddress] = max(
                self.state.last_nonce_by_sender.get(tx.fromAddress, -1),
                tx.nonce
            )
            # debit/credit
            self.state.update_balance(tx.fromAddress, -tx.amount)

        self.state.update_balance(tx.toAddress, tx.amount)
        return True

    def addBlock(self, block: Block) -> bool:
        # validate links
        if block.previousHash != self.last_block().hash:
            return False
        if not block.validate():
            return False
        # validate pow
        if not block.hash.startswith("0" * self.pow.difficulty):
            return False

        # apply txs
        for tx in block.transactions:
            if not self.apply_transaction_to_state(tx):
                return False

        self.chain.append(block)
        return True

    def isValid(self) -> bool:
        if not self.chain or self.chain[0].hash != self.chain[0].compute_hash():
            return False
        for i in range(1, len(self.chain)):
            prev = self.chain[i - 1]
            cur = self.chain[i]
            if cur.previousHash != prev.hash:
                return False
            if not cur.validate():
                return False
            if not cur.hash.startswith("0" * self.pow.difficulty):
                return False
        return True

    def mine_pending(self, miner_address: str) -> Optional[Block]:
        # reward tx
        reward_tx = Transaction(
            fromAddress="COINBASE",
            toAddress=miner_address,
            amount=self.mining_reward,
            signature="",
            publicKeyPem="",
            nonce=0
        )
        txs = self.pendingTransactions[:]
        txs.append(reward_tx)

        block = Block(
            index=self.last_block().index + 1,
            timestamp=time.time(),
            previousHash=self.last_block().hash,
            transactions=txs,
            nonce=0
        )
        block = self.pow.mine(block)

        ok = self.addBlock(block)
        if not ok:
            return None

        self.pendingTransactions = []
        return block

    def to_dict(self) -> Dict[str, Any]:
        return {
            "chain": [b.to_dict() for b in self.chain],
            "pendingTransactions": [t.to_dict() for t in self.pendingTransactions],
            "state": self.state.to_dict(),
            "difficulty": self.pow.difficulty,
            "mining_reward": self.mining_reward,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Blockchain":
        bc = Blockchain()
        bc.chain = [Block.from_dict(x) for x in d.get("chain", [])] or [Block.genesis()]
        bc.pendingTransactions = [Transaction.from_dict(x) for x in d.get("pendingTransactions", [])]
        bc.state = State.from_dict(d.get("state", {}))
        bc.pow = ProofOfWork(difficulty=int(d.get("difficulty", 3)))
        bc.mining_reward = int(d.get("mining_reward", 100))
        return bc

    def save(self, path: str) -> None:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @staticmethod
    def load(path: str) -> "Blockchain":
        if not os.path.exists(path):
            return Blockchain()
        with open(path, "r", encoding="utf-8") as f:
            return Blockchain.from_dict(json.load(f))