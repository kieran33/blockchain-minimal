from src.core.blockchain import Blockchain
from src.core.transaction import Transaction
from src.crypto.keys import KeyPair, address_from_public_pem
from src.crypto.signing import sign_hash_hex


def test_block_tampering_breaks_validation():
    bc = Blockchain()
    bc.pow.difficulty = 1  # accélère les tests

    miner_kp = KeyPair.generate()
    miner_addr = address_from_public_pem(miner_kp.public_pem())

    # 1er bloc coinbase pour avoir du solde
    b1 = bc.mine_pending(miner_addr)
    assert b1 is not None
    assert bc.isValid() is True

    recv_kp = KeyPair.generate()
    recv_addr = address_from_public_pem(recv_kp.public_pem())

    tx = Transaction(
        fromAddress=miner_addr,
        toAddress=recv_addr,
        amount=5,
        publicKeyPem=miner_kp.public_pem().decode("utf-8"),
        nonce=1,
    )
    tx.signature = sign_hash_hex(miner_kp.private_key, tx.tx_hash())
    assert bc.addTransaction(tx) is True

    b2 = bc.mine_pending(miner_addr)
    assert b2 is not None
    assert bc.isValid() is True

    # tamper : on modifie une tx déjà minée
    bc.chain[-1].transactions[0].amount = 999999
    # la validation du block doit échouer -> la chain aussi
    assert bc.chain[-1].validate() is False
    assert bc.isValid() is False