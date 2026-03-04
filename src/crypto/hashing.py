from __future__ import annotations
import hashlib
import json
from typing import Any, List


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def hash_json(obj: Any) -> str:
    packed = json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return sha256(packed)


def merkle_root(tx_hashes: List[str]) -> str:
    """
    Merkle root simplifié : on pair hash par hash.
    Si impair, on duplique le dernier.
    """
    if not tx_hashes:
        return sha256(b"")
    layer = tx_hashes[:]
    while len(layer) > 1:
        if len(layer) % 2 == 1:
            layer.append(layer[-1])
        nxt = []
        for i in range(0, len(layer), 2):
            nxt.append(sha256((layer[i] + layer[i + 1]).encode("utf-8")))
        layer = nxt
    return layer[0]