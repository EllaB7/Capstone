# Audit log exfiltration capstone

Synthetic M365 audit-log generator + (later) detection and LLM report pipeline.

    python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    python -m src.generate --seed 42 --users 50 --days 30
    python -m pytest

Outputs: `data/audit_log.jsonl` (detector input) and `data/ground_truth.json` (never shown to the detector).
