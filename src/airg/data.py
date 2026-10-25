"""Synthetic client records for the simulated copilot (FR-13). No real data."""
from __future__ import annotations

import json
import random
from dataclasses import asdict, dataclass
from itertools import product
from pathlib import Path

FIRST_NAMES = [
    "Avery", "Blake", "Casey", "Dana", "Elliot", "Finley", "Gray", "Harper", "Indy", "Jordan",
    "Kai", "Logan", "Morgan", "Noel", "Oakley", "Parker", "Quinn", "Reese", "Sage", "Taylor",
]
LAST_NAMES = [
    "Ashford", "Brennan", "Calloway", "Delacroix", "Everly", "Fairbanks", "Galloway", "Hollister",
    "Ingram", "Jessup", "Kensington", "Lockhart", "Merriweather", "Northcott", "Ostrander",
    "Pemberton", "Quill", "Radcliffe", "Sterling", "Thorne",
]
PRODUCTS = [
    "Managed Portfolio", "Municipal Bond Ladder", "Trust Account",
    "Private Credit Line", "Cash Management", "Charitable Remainder Trust",
]
NOTES = [
    "Prefers quarterly reviews in person.",
    "Considering a gift to a family foundation.",
    "Asked about tax-loss harvesting before year end.",
    "Planning a business sale in the next two years.",
    "Wants lower exposure to equities.",
    "Recently added a spouse as co-trustee.",
]


@dataclass(frozen=True)
class ClientRecord:
    client_id: str
    name: str
    rm_id: str
    account_number: str
    balance: int
    products: tuple[str, ...]
    note: str


def generate_clients(seed: int = 42, n_clients: int = 60, n_rms: int = 12) -> list[ClientRecord]:
    rng = random.Random(seed)
    names = rng.sample([f"{f} {l}" for f, l in product(FIRST_NAMES, LAST_NAMES)], n_clients)
    accounts = rng.sample(range(10**7, 10**8), n_clients)
    records = []
    for i in range(n_clients):
        records.append(ClientRecord(
            client_id=f"C-{1001 + i}",
            name=names[i],
            rm_id=f"RM-{(i % n_rms) + 1:02d}",
            account_number=f"BMT-{accounts[i]}",
            balance=rng.randrange(250_000, 25_000_000, 1_000),
            products=tuple(sorted(rng.sample(PRODUCTS, rng.randint(1, 3)))),
            note=rng.choice(NOTES),
        ))
    return records


def write_clients(records: list[ClientRecord], path: Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps([asdict(r) for r in records], indent=2) + "\n")


def load_clients(path: Path) -> list[ClientRecord]:
    raw = json.loads(Path(path).read_text())
    return [ClientRecord(**{**d, "products": tuple(d["products"])}) for d in raw]


def main() -> None:
    write_clients(generate_clients(), Path("data/clients.json"))


if __name__ == "__main__":
    main()
