"""Official AICPA Description Criteria (DC Section 200) — 2018, rev. 2022.

Provenance: AICPA *Description Criteria for a Description of the System* (DC Section 200)
in "Reporting on an Examination of Controls at a Service Organization Relevant to
Security, Availability, Processing Integrity, Confidentiality, or Privacy" (SOC 2 Guide).
The 16 criteria below (DC-1.1 through DC-7.1) are the full set. Criterion titles are
standard AICPA short titles (used here as titles); requirement descriptions are faithful
paraphrases — AICPA text is copyrighted and the Apache-2.0 catalog carries paraphrase +
a documented license footing note instead of verbatim reprints (ACCURACY_BACKLOG SKU 1).

`required` records whether the criterion is mandatory for a complete System Description
or recommended (DC-1.7 / DC-5.1 / DC-6.1 / DC-7.1 are supplementary).
"""

from __future__ import annotations

# id -> official title (short, used as title) + faithful paraphrase of the requirement
# + whether the criterion is required for a complete system description.
DC_CRITERIA: dict[str, dict[str, object]] = {
    "DC-1.1": {
        "title": "Types of Services Provided",
        "description": (
            "The description covers the nature of the services provided, including the "
            "types of services the system produces and the products the entity offers."
        ),
        "required": True,
    },
    "DC-1.2": {
        "title": "Infrastructure",
        "description": (
            "The description identifies the types of infrastructure used to develop and "
            "support the system, including physical and logical components."
        ),
        "required": True,
    },
    "DC-1.3": {
        "title": "Software",
        "description": (
            "The description identifies the key software used to process and maintain data, "
            "including system, application, and infrastructure software."
        ),
        "required": True,
    },
    "DC-1.4": {
        "title": "People",
        "description": (
            "The description identifies key personnel responsible for the system's "
            "development, operation, and oversight, and their roles."
        ),
        "required": True,
    },
    "DC-1.5": {
        "title": "Data",
        "description": (
            "The description describes the types of data processed and stored by the system "
            "and the flows of that data within and across the boundary."
        ),
        "required": True,
    },
    "DC-1.6": {
        "title": "Processes and Procedures",
        "description": (
            "The description covers key processes and procedures used to operate and control "
            "the system, including those supporting the services supplied."
        ),
        "required": True,
    },
    "DC-1.7": {
        "title": "Monitoring",
        "description": (
            "The description addresses how the system is monitored, how incidents are "
            "detected and reported, and how monitoring results are communicated."
        ),
        "required": False,
    },
    "DC-2.1": {
        "title": "System Boundaries",
        "description": (
            "The description specifies the boundaries of the system, clarifying what is "
            "included in and excluded from the described environment."
        ),
        "required": True,
    },
    "DC-2.2": {
        "title": "Products and Services",
        "description": (
            "The description explains the products and services delivered by the system "
            "to its user entities."
        ),
        "required": True,
    },
    "DC-3.1": {
        "title": "Subservice Organizations",
        "description": (
            "The description identifies subservice organizations whose services affect the "
            "system and states whether the carve-out or inclusive method was used."
        ),
        "required": True,
    },
    "DC-3.2": {
        "title": "Complementary User Entity Controls (CUEC)",
        "description": (
            "The description identifies controls the user entities are expected to implement "
            "for the system to meet its services and objectives."
        ),
        "required": True,
    },
    "DC-4.1": {
        "title": "Service Commitments",
        "description": (
            "The description covers the service commitments made to user entities and the "
            "basis for those commitments."
        ),
        "required": True,
    },
    "DC-4.2": {
        "title": "System Requirements",
        "description": (
            "The description covers the system requirements, including relevant criteria, "
            "necessary to achieve the entity's service commitments."
        ),
        "required": True,
    },
    "DC-5.1": {
        "title": "Control Objectives and Related Controls",
        "description": (
            "The description identifies the control objectives and the controls designed to "
            "achieve them when the engagement addresses the controls placed in operation."
        ),
        "required": False,
    },
    "DC-6.1": {
        "title": "Changes to the System",
        "description": (
            "The description identifies changes to the system during the period covered and "
            "their effect on the reliability of the description."
        ),
        "required": False,
    },
    "DC-7.1": {
        "title": "Criteria Met and Not Met",
        "description": (
            "The description identifies which of the description criteria were met and any "
            "areas not addressed, where relevant."
        ),
        "required": False,
    },
}


def dc_title(cid: str) -> str:
    return str(DC_CRITERIA[cid]["title"])


def dc_description(cid: str) -> str:
    return str(DC_CRITERIA[cid]["description"])


def dc_required(cid: str) -> bool:
    return bool(DC_CRITERIA[cid]["required"])


def dc_criteria_ids() -> list[str]:
    return list(DC_CRITERIA)
