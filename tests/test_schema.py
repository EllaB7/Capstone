import numpy as np
from datetime import datetime

from src.baseline import generate_baseline, make_users
from src.schema import AuditRecord


def test_hand_written_record_validates():
    AuditRecord(
        Id="1", CreationTime=datetime(2026, 9, 1, 9, 0), Operation="FileDownloaded",
        Workload="SharePoint", UserId="a@syneos.com", ClientIP="1.2.3.4",
        UserAgent="x", SiteUrl="https://syneos.sharepoint.com/sites/HR",
        SourceRelativeUrl="Shared Documents/a.docx", SourceFileName="a.docx",
        ObjectId="https://syneos.sharepoint.com/sites/HR/Shared Documents/a.docx",
    )


def test_baseline_is_reproducible():
    def run():
        rng = np.random.default_rng(7)
        users = make_users(5, rng)
        return [r.model_dump() for r in generate_baseline(users, datetime(2026, 9, 1), 3, rng)]
    a, b = run(), run()
    assert len(a) > 0 and a == b
