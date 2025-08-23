from pydantic import BaseModel, Field, HttpUrl
from typing import List, Optional, Literal, Dict, Any

class DiagnoseRequest(BaseModel):
    target: str = Field(..., description="URL or domain to diagnose")

IssueCategory = Literal["DNS","TLS","HTTP","Network","Content"]

class Issue(BaseModel):
    id: str | int  # Allow both string and int for id
    category: IssueCategory
    severity: Literal["info","low","medium","high"]
    evidence: str | Dict[str, Any]  # Allow both string and dict for evidence
    recommended_fix: str

class Artifact(BaseModel):
    screenshots: List[str] = []
    raw_samples: Dict[str, Any] = {}

class DiagnosticReport(BaseModel):
    summary: str
    issues: List[Issue] = []
    artifacts: Artifact = Artifact()

# New user-friendly schemas
class UserFriendlyIssue(BaseModel):
    """A simplified issue description for non-technical users"""
    title: str
    description: str
    impact: str
    solution: str
    urgency: Literal["critical", "important", "minor"]
    technical_details: Optional[str] = None

class UserFriendlyReport(BaseModel):
    """A simplified diagnostic report for non-technical users"""
    is_broken: bool
    primary_issue: Optional[UserFriendlyIssue] = None
    user_message: str
    quick_fix: Optional[str] = None
    all_issues_count: int = 0
