from src.core.blockchain import Blockchain
from src.core.transaction import Transaction
from src.crypto.keys import KeyPair, address_from_public_pem
from src.crypto.signing import sign_hash_hex


def test_nonce_replay_prevented():
    bc = Blockchain()
    bc.pow.difficulty = 1

    miner_kp = KeyPair.generate()
    miner_addr = address_from_public_pem(miner_kp.public_pem())
    bc.mine_pending(miner_addr)

    recv_kp = KeyPair.generate()
    recv_addr = address_from_public_pem(recv_kp.public_pem())

    # nonce=1 OK
    tx1 = Transaction(
        fromAddress=miner_addr,
        toAddress=recv_addr,
        amount=1,
        publicKeyPem=miner_kp.public_pem().decode("utf-8"),
        nonce=1,
    )
    tx1.signature = sign_hash_hex(miner_kp.private_key, tx1.tx_hash())
    assert bc.addTransaction(tx1) is True
    bc.mine_pending(miner_addr)

    # nonce=1 REPLAY -> doit être refusé
    tx_replay = Transaction(
        fromAddress=miner_addr,
        toAddress=recv_addr,
        amount=1,
        publicKeyPem=miner_kp.public_pem().decode("utf-8"),
        nonce=1,
    )
    tx_replay.signature = sign_hash_hex(miner_kp.private_key, tx_replay.tx_hash())
    assert bc.addTransaction(tx_replay) is False

    # nonce=2 OK
    tx2 = Transaction(
        fromAddress=miner_addr,
        toAddress=recv_addr,
        amount=1,
        publicKeyPem=miner_kp.public_pem().decode("utf-8"),
        nonce=2,
    )
    tx2.signature = sign_hash_hex(miner_kp.private_key, tx2.tx_hash())
    assert bc.addTransaction(tx2) is True