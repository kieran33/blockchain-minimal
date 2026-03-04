from src.core.state import State
from src.contracts.contracts import CounterContract, TransferIfBalanceAtLeast


def test_counter_contract_deterministic():
    s = State()
    c = CounterContract(key="counter", step=2)

    c.execute(s)
    c.execute(s)
    assert s.contract_storage["counter"] == 4  # 0 +2 +2


def test_transfer_if_balance_at_least():
    s = State()
    s.balances["A"] = 50
    s.balances["B"] = 0

    c = TransferIfBalanceAtLeast(from_addr="A", to_addr="B", amount=10, min_balance=40)
    c.execute(s)

    assert s.balances["A"] == 40
    assert s.balances["B"] == 10