from src.p2p.node import P2PNode
from src.core.transaction import Transaction


def test_p2p_remember_prevents_loop(monkeypatch):
    node = P2PNode(host="127.0.0.1", port=9999, data_path="data/test_chain.json")
    node.peers = ["http://127.0.0.1:5002", "http://127.0.0.1:5003"]

    calls = []

    def fake_post(url, json=None, timeout=None):
        calls.append((url, json))
        class R:
            status_code = 200
        return R()

    monkeypatch.setattr("requests.post", fake_post)

    tx = Transaction(fromAddress="COINBASE", toAddress="X", amount=1)

    msg_id = "same-id"
    node.broadcastTransaction(tx, message_id=msg_id)
    assert len(calls) == 2  # 2 peers

    # re-broadcast avec le même message_id => doit être ignoré
    node.broadcastTransaction(tx, message_id=msg_id)
    assert len(calls) == 2