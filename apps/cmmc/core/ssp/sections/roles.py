from ssp.utils import create_table


def add_roles_responsibilities(doc, org_profile: dict | None = None) -> None:
    profile = org_profile or {}
    doc.add_heading("3. Roles and Responsibilities", level=1)
    doc.add_paragraph(
        "Organizational roles responsible for implementing and maintaining security controls."
    )

    def contact(field: str, fallback: str) -> str:
        value = (profile.get(field) or "").strip()
        return value if value else fallback

    role_data = [
        ("Information System Owner", "Overall system security responsibility", contact("system_owner", "[System Owner Name]")),
        ("Information Security Officer", "Security policy implementation and oversight", contact("iso_name", "[ISO Name]")),
        ("System Administrator", "Day-to-day system administration and maintenance", contact("sysadmin_name", "[SysAdmin Name]")),
        ("Network Administrator", "Network security and connectivity management", contact("network_admin_name", "[Network Admin Name]")),
        ("Auditor/Assessor", "Independent security assessment and compliance verification", contact("auditor_name", "[Auditor Name]")),
    ]
    create_table(doc, ["Role", "Responsibilities", "Primary Contact"], role_data)
    doc.add_page_break()
