from src.crypto.keys import KeyPair, address_from_public_pem
from src.crypto.signing import sign_hash_hex, verify_hash_hex
from src.crypto.hashing import sha256


def test_sign_verify():
    kp = KeyPair.generate()
    msg_hash = sha256(b"hello")
    sig = sign_hash_hex(kp.private_key, msg_hash)
    assert verify_hash_hex(kp.public_pem(), msg_hash, sig) is True


def test_address():
    kp = KeyPair.generate()
    addr = address_from_public_pem(kp.public_pem())
    assert addr.startswith("M")
    assert len(addr) == 41