"""Attack scenarios. Each returns (events, ground_truth_label)."""
from datetime import datetime, timedelta

from .baseline import User, make_record, random_ip

EXTERNAL_UA = "python-requests/2.31"


def bulk_download(rng, user: User, when: datetime, n_files: int = 500,
                  minutes: int = 12, scenario_id: str = "S001"):
    """One user downloads many files from their dept site, off-hours, from a new IP."""
    site = user.sites[0]
    n_files = min(n_files, len(site.files))
    picks = rng.choice(len(site.files), size=n_files, replace=False)
    attacker_ip = random_ip(rng)
    events = []
    for i, idx in enumerate(picks):
        ts = when + timedelta(seconds=i * (minutes * 60 / n_files))
        events.append(make_record(rng, ts, "FileDownloaded", user, site,
                                  site.files[idx], ip=attacker_ip, user_agent=EXTERNAL_UA))
    label = {
        "scenario_id": scenario_id,
        "scenario": "bulk_download",
        "user": user.user_id,
        "start": events[0].CreationTime.isoformat(),
        "end": events[-1].CreationTime.isoformat(),
        "attacker_ip": attacker_ip,
        "event_ids": [e.Id for e in events],
    }
    return events, label
