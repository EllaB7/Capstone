"""Entry point: python -m src.generate --seed 42 --users 50 --days 30"""
import argparse
import json
from datetime import datetime
from pathlib import Path

import numpy as np

from .baseline import generate_baseline, make_users
from .scenarios import bulk_download


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--users", type=int, default=50)
    p.add_argument("--days", type=int, default=30)
    p.add_argument("--out", default="data")
    args = p.parse_args()

    rng = np.random.default_rng(args.seed)
    start = datetime(2026, 9, 1)  # a Tuesday

    users = make_users(args.users, rng)
    records = generate_baseline(users, start, args.days, rng)

    # Inject scenarios (add more here as you build them)
    labels = []
    victim = users[int(rng.integers(len(users)))]
    attack_time = start.replace(day=19, hour=2, minute=14)  # 2:14 AM
    events, label = bulk_download(rng, victim, attack_time)
    records += events
    labels.append(label)

    records.sort(key=lambda r: r.CreationTime)

    out = Path(args.out)
    out.mkdir(exist_ok=True)
    with open(out / "audit_log.jsonl", "w") as f:
        for r in records:
            f.write(r.model_dump_json() + "\n")
    with open(out / "ground_truth.json", "w") as f:
        json.dump(labels, f, indent=2)

    print(f"{len(users)} users, {len(records)} events "
          f"({sum(len(l['event_ids']) for l in labels)} malicious) -> {out}/")


if __name__ == "__main__":
    main()
