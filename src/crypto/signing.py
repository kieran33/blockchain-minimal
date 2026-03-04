from __future__ import annotations
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.exceptions import InvalidSignature


def sign_hash_hex(private_key: ec.EllipticCurvePrivateKey, message_hash_hex: str) -> str:
    sig = private_key.sign(bytes.fromhex(message_hash_hex), ec.ECDSA(hashes.SHA256()))
    return sig.hex()


def verify_hash_hex(public_pem: bytes, message_hash_hex: str, signature_hex: str) -> bool:
    pub = serialization.load_pem_public_key(public_pem)
    if not isinstance(pub, ec.EllipticCurvePublicKey):
        return False
    try:
        pub.verify(bytes.fromhex(signature_hex), bytes.fromhex(message_hash_hex), ec.ECDSA(hashes.SHA256()))
        return True
    except InvalidSignature:
        return False
    except Exception:
        return False