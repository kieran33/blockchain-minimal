from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class State:
    balances: Dict[str, int] = field(default_factory=dict)
    contract_storage: Dict[str, Any] = field(default_factory=dict)
    last_nonce_by_sender: Dict[str, int] = field(default_factory=dict)

    def get_balance(self, address: str) -> int:
        return int(self.balances.get(address, 0))

    def update_balance(self, address: str, amount_delta: int) -> None:
        self.balances[address] = self.get_balance(address) + int(amount_delta)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "balances": self.balances,
            "contract_storage": self.contract_storage,
            "last_nonce_by_sender": self.last_nonce_by_sender,
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "State":
        s = State()
        s.balances = {k: int(v) for k, v in d.get("balances", {}).items()}
        s.contract_storage = d.get("contract_storage", {})
        s.last_nonce_by_sender = {k: int(v) for k, v in d.get("last_nonce_by_sender", {}).items()}
        return s