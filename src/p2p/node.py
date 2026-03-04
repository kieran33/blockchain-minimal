from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict, Any
import time
import uuid
import requests

from src.core.blockchain import Blockchain
from src.core.transaction import Transaction
from src.core.block import Block
from src.contracts.contracts import contract_from_dict


@dataclass
class P2PNode:
    host: str
    port: int
    data_path: str
    peers: List[str] = field(default_factory=list)
    blockchain: Blockchain = field(default_factory=Blockchain)

    seen_message_ids: Set[str] = field(default_factory=set)
    seen_max: int = 5000

    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    def load(self) -> None:
        self.blockchain = Blockchain.load(self.data_path)

    def save(self) -> None:
        self.blockchain.save(self.data_path)

    def remember(self, msg_id: str) -> bool:
        if msg_id in self.seen_message_ids:
            return False
        self.seen_message_ids.add(msg_id)
        if len(self.seen_message_ids) > self.seen_max:
            # purge grossier
            self.seen_message_ids = set(list(self.seen_message_ids)[-self.seen_max:])
        return True

    def add_peer(self, peer_url: str) -> None:
        if peer_url == self.base_url():
            return
        if peer_url not in self.peers:
            self.peers.append(peer_url)

    def broadcastTransaction(self, tx: Transaction, message_id: Optional[str] = None) -> None:
        msg_id = message_id or str(uuid.uuid4())
        if not self.remember(msg_id):
            return
        payload = {"message_id": msg_id, "tx": tx.to_dict()}
        for p in list(self.peers):
            try:
                requests.post(f"{p}/tx", json=payload, timeout=2)
            except Exception:
                pass

    def broadcastBlock(self, block: Block, message_id: Optional[str] = None) -> None:
        msg_id = message_id or str(uuid.uuid4())
        if not self.remember(msg_id):
            return
        payload = {"message_id": msg_id, "block": block.to_dict()}
        for p in list(self.peers):
            try:
                requests.post(f"{p}/block", json=payload, timeout=2)
            except Exception:
                pass

    def execute_contract(self, contract_dict: Dict[str, Any]) -> None:
        c = contract_from_dict(contract_dict)
        c.execute(self.blockchain.state)
        self.save()