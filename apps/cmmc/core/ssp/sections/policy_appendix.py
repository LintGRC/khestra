from ssp.utils import create_table


_FAMILY_POLICIES = [
    ("Access Control Policy",                     "AC", "3.1",  "Access Control"),
    ("Awareness and Training Policy",              "AT", "3.2",  "Awareness and Training"),
    ("Audit and Accountability Policy",            "AU", "3.3",  "Audit and Accountability"),
    ("Configuration Management Policy",            "CM", "3.4",  "Configuration Management"),
    ("Identification and Authentication Policy",   "IA", "3.5",  "Identification and Authentication"),
    ("Incident Response Policy",                   "IR", "3.6",  "Incident Response"),
    ("Maintenance Policy",                         "MA", "3.7",  "Maintenance"),
    ("Media Protection Policy",                    "MP", "3.8",  "Media Protection"),
    ("Personnel Security Policy",                  "PS", "3.9",  "Personnel Security"),
    ("Physical and Environmental Security Policy", "PE", "3.10", "Physical Protection"),
    ("Risk Assessment Policy",                     "RA", "3.11", "Risk Assessment"),
    ("Security Assessment Policy",                 "CA", "3.12", "Security Assessment"),
    ("System and Communications Protection Policy","SC", "3.13", "System and Communications Protection"),
    ("System and Information Integrity Policy",    "SI", "3.14", "System and Information Integrity"),
]


def add_policy_appendix(doc, scoped_controls: list, *, section_number: int = 7) -> None:
    doc.add_heading(f"{section_number}. Policy Appendix", level=1)
    doc.add_paragraph(
        "The following policy documents govern the security controls described in this SSP. "
        "Each policy corresponds to a NIST SP 800-171 Rev 2 control family. "
        "Policies are reviewed and updated at least annually."
    )

    rows = []
    for name, code, nist_ref, family in _FAMILY_POLICIES:
        family_controls = [c for c in scoped_controls if c.startswith(f"{code}.")]
        count = len(family_controls)
        rows.append([
            name,
            f"{nist_ref} ({code})",
            family,
            str(count),
        ])

    create_table(
        doc,
        ["Policy", "NIST Ref", "Family", "Controls"],
        rows,
    )
