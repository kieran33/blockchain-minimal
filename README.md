# Minimal Blockchain (Python)

A minimal blockchain implementation written in Python demonstrating the
core mechanisms behind blockchain systems.

## Features

- Wallet generation with cryptographic keys
- Signed transactions
- Proof-of-Work mining
- Block validation and chain integrity
- Peer-to-peer networking
- Deterministic smart contracts
- Interactive CLI
- Automated tests with pytest

---

## Architecture

Place the architecture image in:

    archi.png

Then reference it in the README:

    ![Architecture](docs/archi.png)

Modules:

- **Crypto**
  - SHA256 hashing
  - ECDSA key generation
  - Signature verification
- **Core**
  - Transactions
  - Blocks
  - Blockchain state
  - Proof-of-Work consensus
- **P2P**
  - Node communication
  - Peer discovery
  - Transaction propagation
  - Block propagation
- **Smart Contracts**
  - Deterministic execution
  - State storage
- **CLI**
  - Wallet creation
  - Mining
  - Transaction management

---

## Project Structure

```text
blockchain-minimal
│
├─ src
│   ├─ crypto
│   ├─ core
│   ├─ p2p
│   ├─ contracts
│   └─ cli
│
├─ tests
├─ docs
│   └─ architecture.png
├─ requirements.txt
└─ README.md
```

---

## Installation

### 1 Clone repository

```bash
git clone https://github.com/YOUR_USERNAME/blockchain-minimal.git
cd blockchain-minimal
```

### 2 Python version

Python **3.11 -- 3.13 recommended**

```bash
python --version
```

### 3 Create virtual environment

```bash
python -m venv .venv
```

### 4 Activate environment

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
```

### 5 Install dependencies

```bash
pip install -r requirements.txt
```

### 6 Verify installation

```bash
python -m pytest -v
```

Expected:

    8 passed

---

## Running the Blockchain Network

Start 3 nodes in separate terminals.

### Node 1

```bash
python -m src.p2p.server_run --port 5001
```

### Node 2

```bash
python -m src.p2p.server_run --port 5002
```

### Node 3

```bash
python -m src.p2p.server_run --port 5003
```

Verify nodes:

```bash
curl http://127.0.0.1:5001/health
curl http://127.0.0.1:5002/health
curl http://127.0.0.1:5003/health
```

---

## Demo

### 1 Start CLI

```bash
python -m src.cli.main
```

### 2 Create wallets

Use option:

    1 Create wallet

Create two wallets (A and B).

### 3 Mine first block

    3 Mine block

Wallet A receives the mining reward.

### 4 Send transaction

    2 Send signed transaction

Example:

    amount = 10
    nonce = 1

### 5 Mine another block

    3 Mine block

Transaction becomes part of the blockchain.

### 6 Verify state

    6 View state

Balances update across nodes via P2P synchronization.

---

## Testing

Run tests:

```bash
python -m pytest -v
```

Example output:

    tests/test_crypto.py PASSED
    tests/test_chain.py PASSED
    tests/test_integrity.py PASSED
    tests/test_nonce_replay.py PASSED
    tests/test_contracts.py PASSED
    tests/test_p2p_anti_loop.py PASSED

---

## Educational Purpose

This project demonstrates:

- distributed ledgers
- cryptographic security
- consensus algorithms
- peer-to-peer networking
- deterministic smart contracts

The implementation prioritizes **clarity and learning** rather than
production scalability.

---

## License

MIT License
