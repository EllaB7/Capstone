"""Generate normal (benign) activity for a population of users."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta

import numpy as np # import to make random choices

from .schema import AuditRecord

TENANT = "Syneos"
DEPARTMENTS = {
    "Finance": ["Budget", "Payroll", "Invoice", "Forecast"],
    "HR": ["Policy", "Onboarding", "Review", "Benefits"],
    "Engineering": ["Design", "Spec", "Roadmap", "Postmortem"],
    "Sales": ["Pipeline", "Proposal", "Contract", "Quote"],
}
EXTENSIONS = ["docx", "xlsx", "pptx", "pdf"] # file extensions in generation
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_4) Safari/605.1",
    "Microsoft Office/16.0 (Windows NT 10.0)",
]
# (operation, weight) for normal behavior
OPS = [("FileAccessed", 0.65), ("FileModified", 0.15), ("FileDownloaded", 0.10), # sets understanding that any high download rate is not normal.
       ("FileUploaded", 0.08), ("FileDeleted", 0.02)]
       # Normally, FileAccessed is 65% of events


@dataclass # define site
class Site:
    workload: str # SharePoint or OneDrive
    url: str 
    files: list  # list of (relative_url, file_name). Maps to SiteUrl, SourceRelativeUrl, and SourceFileName


@dataclass
class User:
    user_id: str                # Who are they?
    dept: str                   # What department do they belong to?
    ip: str                     # Where are they located?
    user_agent: str             # What browswer/application did they use?
    start_hour: float           # When did they start working?
    end_hour: float             # When did they end working?
    mean_events: float          # average events per weekday
    sites: list = field(default_factory=list)   # List of sites per user from site class they used.


def new_id(rng) -> str: # randomly generates event ID's in 16 bytes.
    return str(uuid.UUID(bytes=rng.bytes(16), version=4))


def random_ip(rng) -> str: # randomly generates IPs inside parameters
    return f"{rng.integers(11, 223)}.{rng.integers(0, 256)}.{rng.integers(0, 256)}.{rng.integers(1, 255)}"


def _make_files(rng, topics, n, folder):
    files = []
    for i in range(n):
        name = f"{rng.choice(topics)}_{i:04d}.{rng.choice(EXTENSIONS)}"
        files.append((f"{folder}/{name}", name))
    return files


def make_users(n: int, rng) -> list:
    dept_names = list(DEPARTMENTS)
    dept_sites = {
        d: Site("SharePoint", f"https://{TENANT}.sharepoint.com/sites/{d}",
                _make_files(rng, DEPARTMENTS[d], 600, "Shared Documents"))
        for d in dept_names
    }
    users = []
    for i in range(n):
        dept = dept_names[i % len(dept_names)]
        uid = f"user{i:03d}@{TENANT}.com"
        start = float(rng.choice([7, 8, 9]))
        onedrive = Site("OneDrive",
                        f"https://{TENANT}-my.sharepoint.com/personal/user{i:03d}_{TENANT}_com",
                        _make_files(rng, DEPARTMENTS[dept], 40, "Documents"))
        users.append(User(
            user_id=uid, dept=dept, ip=random_ip(rng),
            user_agent=str(rng.choice(USER_AGENTS)),
            start_hour=start, end_hour=start + 8,
            mean_events=float(rng.uniform(15, 60)),
            sites=[dept_sites[dept], onedrive],
        ))
    return users


def make_record(rng, ts, op, user, site, file, ip=None, user_agent=None) -> AuditRecord:
    rel, name = file
    return AuditRecord(
        Id=new_id(rng), CreationTime=ts, Operation=op, Workload=site.workload,
        UserId=user.user_id, ClientIP=ip or user.ip,
        UserAgent=user_agent or user.user_agent,
        SiteUrl=site.url, SourceRelativeUrl=rel, SourceFileName=name,
        ObjectId=f"{site.url}/{rel}",
    )


def generate_baseline(users, start: datetime, days: int, rng) -> list:
    ops, weights = zip(*OPS)
    records = []
    for d in range(days):
        day = start + timedelta(days=d)
        weekend = day.weekday() >= 5
        for u in users:
            mean = u.mean_events * (0.1 if weekend else 1.0)
            if rng.random() < 0.02:      # benign outlier: a legitimately busy day
                mean *= 4
            for _ in range(rng.poisson(mean)):
                mid = (u.start_hour + u.end_hour) / 2
                hour = float(np.clip(rng.normal(mid, (u.end_hour - u.start_hour) / 4),
                                     u.start_hour, u.end_hour))
                ts = day.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=hour)
                site = u.sites[0] if rng.random() < 0.7 else u.sites[1]
                file = site.files[rng.integers(len(site.files))]
                records.append(make_record(rng, ts, str(rng.choice(ops, p=weights)), u, site, file))
    return records
