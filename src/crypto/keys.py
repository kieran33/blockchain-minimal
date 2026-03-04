from __future__ import annotations
import os
from dataclasses import dataclass
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend

from .hashing import sha256


@dataclass
class KeyPair:
    private_key: ec.EllipticCurvePrivateKey
    public_key: ec.EllipticCurvePublicKey

    @staticmethod
    def generate() -> "KeyPair":
        priv = ec.generate_private_key(ec.SECP256K1(), backend=default_backend())
        return KeyPair(private_key=priv, public_key=priv.public_key())

    def public_pem(self) -> bytes:
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def private_pem(self, passphrase: str) -> bytes:
        enc = serialization.BestAvailableEncryption(passphrase.encode("utf-8"))
        return self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=enc,
        )

    @staticmethod
    def load_private_pem(pem: bytes, passphrase: str) -> "KeyPair":
        priv = serialization.load_pem_private_key(
            pem,
            password=passphrase.encode("utf-8"),
            backend=default_backend(),
        )
        if not isinstance(priv, ec.EllipticCurvePrivateKey):
            raise ValueError("Not an EC private key")
        return KeyPair(private_key=priv, public_key=priv.public_key())


def address_from_public_pem(pub_pem: bytes, prefix: str = "M") -> str:
    """
    Adresse simple : prefix + 40 hex chars (20 bytes) de hash(pubkey_pem).
    """
    h = sha256(pub_pem)
    return f"{prefix}{h[:40]}"


def save_bytes(path: str, data: bytes) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(data)


def load_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()