from enum import Enum


class Role(str, Enum):
    APPLICANT = "applicant"
    TECHNICAL_REVIEWER = "technical_reviewer"
    ADMIN = "admin"
    AUDITOR = "auditor"
