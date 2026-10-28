"""One audit record, modeled loosely on the Microsoft 365 Unified Audit Log.

PLACEHOLDER FIELD LIST: compare against the SharePoint base schema in the
Office 365 Management Activity API docs and adjust. Record every change in
docs/schema_notes.md so your methods chapter writes itself.
"""
from datetime import datetime
from pydantic import BaseModel


class AuditRecord(BaseModel):
    Id: str
    CreationTime: datetime
    Operation: str           # e.g. "FileDownloaded"
    Workload: str            # "SharePoint" or "OneDrive"
    RecordType: int = 6      # 6 = SharePointFileOperation
    UserId: str
    ClientIP: str
    UserAgent: str
    SiteUrl: str
    SourceRelativeUrl: str
    SourceFileName: str
    ObjectId: str            # full URL of the file
    ItemType: str = "File"
