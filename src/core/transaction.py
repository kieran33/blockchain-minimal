from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Optional, Dict, Any

from src.crypto.hashing import hash_json
from src.crypto.signing import verify_hash_hex


@dataclass
class Transaction:
    fromAddress: str
    toAddress: str
    amount: int  # on évite float, on utilise int (unités)
    signature: str = ""
    publicKeyPem: str = ""  # PEM en string (utf-8)
    nonce: int = 0          # anti-rejeu minimal

    def payload(self) -> Dict[str, Any]:
        return {
            "fromAddress": self.fromAddress,
            "toAddress": self.toAddress,
            "amount": self.amount,
            "publicKeyPem": self.publicKeyPem,
            "nonce": self.nonce,
        }

    def tx_hash(self) -> str:
        return hash_json(self.payload())

    def verify(self) -> bool:
        # Transactions coinbase: fromAddress = "COINBASE" pas de signature requise
        if self.fromAddress == "COINBASE":
            return self.amount >= 0 and self.toAddress != ""
        if not self.signature or not self.publicKeyPem:
            return False
        return verify_hash_hex(self.publicKeyPem.encode("utf-8"), self.tx_hash(), self.signature)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "Transaction":
        return Transaction(
            fromAddress=d["fromAddress"],
            toAddress=d["toAddress"],
            amount=int(d["amount"]),
            signature=d.get("signature", ""),
            publicKeyPem=d.get("publicKeyPem", ""),
            nonce=int(d.get("nonce", 0)),
        )