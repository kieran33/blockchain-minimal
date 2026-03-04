from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any
from src.core.state import State


class SmartContract:
    def execute(self, state: State) -> None:
        raise NotImplementedError


@dataclass
class CounterContract(SmartContract):
    key: str = "counter"
    step: int = 1

    def execute(self, state: State) -> None:
        cur = int(state.contract_storage.get(self.key, 0))
        state.contract_storage[self.key] = cur + int(self.step)


@dataclass
class TransferIfBalanceAtLeast(SmartContract):
    from_addr: str
    to_addr: str
    amount: int
    min_balance: int

    def execute(self, state: State) -> None:
        # déterministe: pas de time, pas d'aléatoire
        if state.get_balance(self.from_addr) >= self.min_balance and state.get_balance(self.from_addr) >= self.amount:
            state.update_balance(self.from_addr, -self.amount)
            state.update_balance(self.to_addr, self.amount)


def contract_from_dict(d: Dict[str, Any]) -> SmartContract:
    t = d.get("type")
    if t == "CounterContract":
        return CounterContract(key=d.get("key", "counter"), step=int(d.get("step", 1)))
    if t == "TransferIfBalanceAtLeast":
        return TransferIfBalanceAtLeast(
            from_addr=d["from_addr"],
            to_addr=d["to_addr"],
            amount=int(d["amount"]),
            min_balance=int(d["min_balance"]),
        )
    raise ValueError(f"Unknown contract type: {t}")