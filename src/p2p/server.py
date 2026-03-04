from __future__ import annotations
from flask import Flask, request, jsonify
from typing import Any, Dict

from src.p2p.node import P2PNode
from src.core.transaction import Transaction
from src.core.block import Block


def create_app(node: P2PNode) -> Flask:
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return jsonify({"ok": True, "node": node.base_url(), "peers": node.peers})

    @app.get("/chain")
    def chain():
        return jsonify(node.blockchain.to_dict())

    @app.get("/state")
    def state():
        return jsonify(node.blockchain.state.to_dict())

    @app.post("/peer")
    def peer():
        data = request.get_json(force=True)
        url = data.get("url", "")
        if url:
            node.add_peer(url)
            node.save()
        return jsonify({"ok": True, "peers": node.peers})

    @app.post("/tx")
    def tx():
        data = request.get_json(force=True)
        msg_id = data.get("message_id", "")
        txd = data.get("tx", {})
        if msg_id and not node.remember(msg_id):
            return jsonify({"ok": True, "ignored": True})

        tx_obj = Transaction.from_dict(txd)
        ok = node.blockchain.addTransaction(tx_obj)
        node.save()

        if ok:
            node.broadcastTransaction(tx_obj, message_id=msg_id)

        return jsonify({"ok": ok})

    @app.post("/block")
    def block():
        data = request.get_json(force=True)
        msg_id = data.get("message_id", "")
        bd = data.get("block", {})
        if msg_id and not node.remember(msg_id):
            return jsonify({"ok": True, "ignored": True})

        b = Block.from_dict(bd)
        ok = node.blockchain.addBlock(b)
        if ok:
            # pending clear basique: si un bloc arrive, on vide (minimaliste)
            node.blockchain.pendingTransactions = []
            node.save()
            node.broadcastBlock(b, message_id=msg_id)
        else:
            node.save()
        return jsonify({"ok": ok})

    @app.post("/mine")
    def mine():
        data = request.get_json(force=True)
        miner = data.get("miner_address", "")
        if not miner:
            return jsonify({"ok": False, "error": "miner_address required"}), 400

        b = node.blockchain.mine_pending(miner)
        if b is None:
            node.save()
            return jsonify({"ok": False})
        node.save()
        node.broadcastBlock(b)
        return jsonify({"ok": True, "block": b.to_dict()})

    @app.post("/contract/execute")
    def contract_execute():
        data = request.get_json(force=True)
        contract = data.get("contract")
        if not isinstance(contract, dict):
            return jsonify({"ok": False, "error": "contract dict required"}), 400
        node.execute_contract(contract)
        return jsonify({"ok": True, "state": node.blockchain.state.to_dict()})

    return app