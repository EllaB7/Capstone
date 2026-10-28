# Common schema: Record Type, Creation Time, User Type, and Action. 
# Also includes: User ID, IP Address, and Object ID.

from pydantic import BaseModel # defines record schema so every generated event is validated against the fields
from datetime import datetime

class AuditRecord(BaseModel):
    Id: str
    CreationTime: datetime
    Operation: str          # e.g. "FileDownloaded"
    UserId: str
    ClientIP: str
    Workload: str           # "SharePoint" or "OneDrive"
    SiteUrl: str
    ObjectId: str           # full path of the file
    SourceFileName: str



