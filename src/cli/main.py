from __future__ import annotations
import os
import json
import requests

from src.crypto.keys import KeyPair, save_bytes, load_bytes, address_from_public_pem
from src.crypto.signing import sign_hash_hex
from src.core.transaction import Transaction
from src.crypto.hashing import hash_json


def input_int(prompt: str, default: int = 0) -> int:
    s = input(prompt).strip()
    return default if s == "" else int(s)


def make_wallet():
    kp = KeyPair.generate()
    passphrase = input("Passphrase pour chiffrer la clé privée: ").strip()
    if not passphrase:
        print("[ERR] passphrase vide")
        return
    out_dir = input("Dossier de sortie (ex: data/wallets): ").strip() or "data/wallets"
    os.makedirs(out_dir, exist_ok=True)

    priv_path = os.path.join(out_dir, "private.pem")
    pub_path = os.path.join(out_dir, "public.pem")

    save_bytes(priv_path, kp.private_pem(passphrase))
    save_bytes(pub_path, kp.public_pem())

    addr = address_from_public_pem(kp.public_pem())
    with open(os.path.join(out_dir, "address.txt"), "w", encoding="utf-8") as f:
        f.write(addr)

    print("[OK] Wallet créé")
    print("  address:", addr)
    print("  private:", priv_path)
    print("  public :", pub_path)


def load_wallet():
    wallet_dir = input("Dossier wallet (ex: data/wallets): ").strip() or "data/wallets"
    priv_path = os.path.join(wallet_dir, "private.pem")
    pub_path = os.path.join(wallet_dir, "public.pem")
    addr_path = os.path.join(wallet_dir, "address.txt")

    passphrase = input("Passphrase: ").strip()
    priv_pem = load_bytes(priv_path)
    kp = KeyPair.load_private_pem(priv_pem, passphrase)
    pub_pem = load_bytes(pub_path)
    address = open(addr_path, "r", encoding="utf-8").read().strip()

    return kp, pub_pem, address


def sign_and_send_tx():
    kp, pub_pem, from_addr = load_wallet()
    node_url = input("URL node (ex: http://127.0.0.1:5001): ").strip() or "http://127.0.0.1:5001"

    to_addr = input("toAddress: ").strip()
    amount = input_int("amount (int): ")
    nonce = input_int("nonce (ex: 1,2,3...): ")

    tx = Transaction(
        fromAddress=from_addr,
        toAddress=to_addr,
        amount=amount,
        signature="",
        publicKeyPem=pub_pem.decode("utf-8"),
        nonce=nonce,
    )
    sig = sign_hash_hex(kp.private_key, tx.tx_hash())
    tx.signature = sig

    payload = {"message_id": "", "tx": tx.to_dict()}
    r = requests.post(f"{node_url}/tx", json=payload, timeout=5)
    print(r.status_code, r.json())


def mine():
    node_url = input("URL node (ex: http://127.0.0.1:5001): ").strip() or "http://127.0.0.1:5001"
    miner_addr = input("Adresse du mineur: ").strip()
    r = requests.post(f"{node_url}/mine", json={"miner_address": miner_addr}, timeout=60)
    print(r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))


def add_peer():
    node_url = input("URL node (ex: http://127.0.0.1:5001): ").strip() or "http://127.0.0.1:5001"
    peer_url = input("URL peer (ex: http://127.0.0.1:5002): ").strip()
    r = requests.post(f"{node_url}/peer", json={"url": peer_url}, timeout=5)
    print(r.status_code, r.json())


def show_chain():
    node_url = input("URL node: ").strip() or "http://127.0.0.1:5001"
    r = requests.get(f"{node_url}/chain", timeout=5)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))


def show_state():
    node_url = input("URL node: ").strip() or "http://127.0.0.1:5001"
    r = requests.get(f"{node_url}/state", timeout=5)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))


def exec_contract():
    node_url = input("URL node: ").strip() or "http://127.0.0.1:5001"
    print("Types: CounterContract | TransferIfBalanceAtLeast")
    t = input("type: ").strip()

    if t == "CounterContract":
        key = input("key (default counter): ").strip() or "counter"
        step = input_int("step (default 1): ", 1)
        contract = {"type": "CounterContract", "key": key, "step": step}
    elif t == "TransferIfBalanceAtLeast":
        from_addr = input("from_addr: ").strip()
        to_addr = input("to_addr: ").strip()
        amount = input_int("amount: ")
        min_balance = input_int("min_balance: ")
        contract = {
            "type": "TransferIfBalanceAtLeast",
            "from_addr": from_addr,
            "to_addr": to_addr,
            "amount": amount,
            "min_balance": min_balance,
        }
    else:
        print("[ERR] type inconnu")
        return

    r = requests.post(f"{node_url}/contract/execute", json={"contract": contract}, timeout=5)
    print(r.status_code)
    print(json.dumps(r.json(), indent=2, ensure_ascii=False))


def main():
    while True:
        print("\n=== Blockchain Minimal CLI ===")
        print("1) Créer wallet")
        print("2) Signer + envoyer transaction")
        print("3) Miner (PoW)")
        print("4) Ajouter peer")
        print("5) Voir chain")
        print("6) Voir state")
        print("7) Exécuter smart contract")
        print("0) Quitter")
        c = input("> ").strip()

        if c == "1":
            make_wallet()
        elif c == "2":
            sign_and_send_tx()
        elif c == "3":
            mine()
        elif c == "4":
            add_peer()
        elif c == "5":
            show_chain()
        elif c == "6":
            show_state()
        elif c == "7":
            exec_contract()
        elif c == "0":
            break
        else:
            print("Choix invalide")


if __name__ == "__main__":
    main()