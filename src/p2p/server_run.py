from __future__ import annotations
import argparse
import os

from src.p2p.node import P2PNode
from src.p2p.server import create_app


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=5001)
    p.add_argument("--data", default="")
    args = p.parse_args()

    data_path = args.data or f"data/node_{args.port}/chain.json"
    os.makedirs(os.path.dirname(data_path), exist_ok=True)

    node = P2PNode(host=args.host, port=args.port, data_path=data_path)
    node.load()

    app = create_app(node)
    app.run(host=args.host, port=args.port, debug=False, threaded=True)


if __name__ == "__main__":
    main()