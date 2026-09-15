"""Official EU AI Act (Regulation 2024/1689) article titles.

Source: apps/aigovernance/docs/EU_AI_Act_Regulation_2024_1689.pdf (full
regulation, 144 pages), article headings extracted via pdftotext on
2026-08-12.

This module is the canonical reference for article wording. The app catalog
(ai_controls_catalog.py) keeps short display titles and carries the official
wording in `official_title`; tests assert they match these tables.

Coverage: the 40 articles modeled by the platform (catalog + conformity).
The regulation has 113 articles; the rest are not modeled.
"""

EU_AI_ACT_ARTICLE_TITLES: dict[str, str] = {
    "5": "Prohibited AI practices",
    "6": "Classification rules for high-risk AI systems",
    "8": "Compliance with the requirements",
    "9": "Risk management system",
    "10": "Data and data governance",
    "11": "Technical documentation",
    "12": "Record-keeping",
    "13": "Transparency and provision of information to deployers",
    "14": "Human oversight",
    "15": "Accuracy, robustness and cybersecurity",
    "16": "Obligations of providers of high-risk AI systems",
    "17": "Quality management system",
    "18": "Documentation keeping",
    "19": "Automatically generated logs",
    "20": "Corrective actions and duty of information",
    "21": "Cooperation with competent authorities",
    "22": "Authorised representatives of providers of high-risk AI systems",
    "23": "Obligations of importers",
    "24": "Obligations of distributors",
    "25": "Responsibilities along the AI value chain",
    "26": "Obligations of deployers of high-risk AI systems",
    "27": "Fundamental rights impact assessment for high-risk AI systems",
    "43": "Conformity assessment",
    "46": "Derogation from conformity assessment procedure",
    "47": "EU declaration of conformity",
    "48": "CE marking",
    "49": "Registration",
    "50": "Transparency obligations for providers and deployers of certain AI systems",
    "51": "Classification of general-purpose AI models as general-purpose AI models with systemic risk",
    "52": "Procedure",
    "53": "Obligations for providers of general-purpose AI models",
    "54": "Authorised representatives of providers of general-purpose AI models",
    "55": "Obligations of providers of general-purpose AI models with systemic risk",
    "56": "Codes of practice",
    "57": "AI regulatory sandboxes",
    "60": "Testing of high-risk AI systems in real world conditions outside AI regulatory sandboxes",
    "61": "Informed consent to participate in testing in real world conditions outside AI regulatory sandboxes",
    "71": "EU database for high-risk AI systems listed in Annex III",
    "72": "Post-market monitoring by providers and post-market monitoring plan for high-risk AI systems",
    "73": "Reporting of serious incidents",
}
