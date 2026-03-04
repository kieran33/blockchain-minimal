# Blockchain Minimal (Python)

Objectif : Blockchain minimale avec :

- Wallets (clés + adresse)
- Transactions signées (ECDSA secp256k1)
- Blocks liés + merkle root simplifié + validation
- Consensus PoW simplifié (difficulty)
- Réseau P2P minimal (peers, diffusion tx/blocs, anti-boucle message_id)
- Smart contracts minimalistes (déterministes)
- Tests pytest

## Installation

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
