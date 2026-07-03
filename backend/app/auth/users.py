from dataclasses import dataclass

from app.auth.roles import Role


@dataclass(frozen=True)
class DemoUser:
    username: str
    password: str
    role: Role
    display_name: str
    organization: str


# Synthetic demo credentials — not production secrets.
DEMO_USERS: dict[str, DemoUser] = {
    "applicant": DemoUser(
        username="applicant",
        password="applicant123",
        role=Role.APPLICANT,
        display_name="Demo Applicant",
        organization="Synthetic Pharma Ltd",
    ),
    "reviewer": DemoUser(
        username="reviewer",
        password="reviewer123",
        role=Role.TECHNICAL_REVIEWER,
        display_name="Demo Technical Reviewer",
        organization="Regulatory Affairs Unit",
    ),
    "admin": DemoUser(
        username="admin",
        password="admin123",
        role=Role.ADMIN,
        display_name="Demo System Admin",
        organization="Modernization Lab",
    ),
    "auditor": DemoUser(
        username="auditor",
        password="auditor123",
        role=Role.AUDITOR,
        display_name="Demo Auditor",
        organization="Compliance Office",
    ),
}


def authenticate(username: str, password: str) -> DemoUser | None:
    user = DEMO_USERS.get(username)
    if user is None or user.password != password:
        return None
    return user
