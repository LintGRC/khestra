SCENARIOS = [
    {
        "id": "ai_prompt_injection",
        "type": "ai_incident",
        "title": "Prompt Injection — System Instructions Leaked",
        "description": "Your customer-facing RAG chatbot exposed internal system prompts and retrieved confidential policy documents after a jailbreak attempt. EU AI Act Art. 73 serious-incident clocks may apply if the system is high-risk.",
        "difficulty": "intermediate",
        "estimatedTime": "30-40 min",
        "triggers": ["EU AI Act Art. 73", "NIST AI RMF GOVERN 1.2", "ISO 42001 8.4"],
        "steps": [
            {
                "step": 1,
                "title": "Detection & Triage (first 30 min)",
                "prompt": "Support reports a user pasted a screenshot showing the chatbot revealing internal HR policy text and API routing instructions. Social media mentions are starting.",
                "context": "The model is a fine-tuned GPT-4 class model behind a RAG pipeline used by 40k monthly active users in the EU.",
                "questions": [
                    "What is your immediate containment plan?",
                    "Who must be notified internally within the first hour?",
                    "Do you treat this as a serious incident under EU AI Act Art. 73 — why or why not?"
                ],
                "expertGuidance": "Disable or rate-limit affected endpoints. Preserve prompts, retrieval logs, and session IDs. Notify AI governance lead, CISO, DPO, and legal. Assess high-risk classification and whether harm to fundamental rights is plausible. Document timeline for regulator notification if Art. 73 applies.",
                "scoringCriteria": [
                    "Containment of the affected model endpoint",
                    "Log preservation for prompts and retrievals",
                    "Cross-functional notification (security, legal, AI owner)",
                    "Art. 73 applicability considered"
                ],
                "frameworkRefs": ["EU AI Act Art. 73", "NIST AI RMF MAP 1.5", "ISO 42001 8.4"],
                "timeAllocation": 15
            },
            {
                "step": 2,
                "title": "Root Cause & Model Registry Link",
                "prompt": "Forensics shows retrieval filters were bypassed via indirect injection in uploaded PDF metadata. The model ID in registry is marked 'limited-risk' but serves HR policy answers.",
                "context": "Model card lacks jailbreak test results. Exception exists for delayed red-team testing.",
                "questions": [
                    "How do you update risk classification and registry records?",
                    "What compensating controls deploy before re-enabling service?",
                    "How do you communicate to users and regulators?"
                ],
                "expertGuidance": "Reclassify model tier if use case expanded. Update model registry with incident link, mitigation plan, and revised testing evidence. Add input sanitization, retrieval ACLs, output filters, and human review for sensitive intents. Prepare Art. 73 notification package if thresholds met.",
                "scoringCriteria": [
                    "Registry / inventory updated",
                    "Technical mitigations specified",
                    "User/regulator communication plan",
                    "Testing gap remediation"
                ],
                "frameworkRefs": ["EU AI Act Art. 9", "NIST AI RMF MEASURE 2.6", "ISO 42001 8.3"],
                "timeAllocation": 15
            }
        ]
    },
    {
        "id": "ai_model_drift",
        "type": "ai_incident",
        "title": "Model Drift — Wrong Eligibility Decisions",
        "description": "Monitoring alerts show a 14% spike in adverse decisions for a credit-eligibility model after a silent vendor update. Fairness metrics crossed internal thresholds overnight.",
        "difficulty": "advanced",
        "estimatedTime": "40-50 min",
        "triggers": ["EU AI Act Art. 73", "NIST AI RMF MANAGE 2.3", "ISO 42001 9.1"],
        "steps": [
            {
                "step": 1,
                "title": "Impact Assessment",
                "prompt": "Fairness dashboard shows disparate impact ratio dropped below 0.8 for one protected class. ~2,300 decisions in the last 72 hours may be affected.",
                "context": "Model is registered as high-risk under EU AI Act. No prior FRIA update for this vendor release.",
                "questions": [
                    "Do you halt automated decisions?",
                    "How do you scope affected customers and decisions?",
                    "What evidence do you gather for regulators and auditors?"
                ],
                "expertGuidance": "Halt or human-in-the-loop override for affected cohort. Pull decision logs, feature distributions, and vendor change logs. Engage model owner, legal, and fairness lead. Trigger FRIA review update and serious incident assessment.",
                "scoringCriteria": [
                    "Decision halt or HITL escalation",
                    "Scope quantification",
                    "Evidence collection plan",
                    "FRIA / high-risk workflow invoked"
                ],
                "frameworkRefs": ["EU AI Act Art. 27", "EU AI Act Art. 73", "NIST AI RMF MANAGE 2.3"],
                "timeAllocation": 20
            },
            {
                "step": 2,
                "title": "Remediation & Governance",
                "prompt": "Vendor confirms a calibration change in production. Rollback ETA is 6 hours. Press inquiry received.",
                "context": "Board wants a remediation summary before market open.",
                "questions": [
                    "Rollback vs. retrain decision criteria?",
                    "How are exceptions/waivers for delayed fixes documented?",
                    "What goes into the regulator pack?"
                ],
                "expertGuidance": "Prefer rollback to last known-good artifact with verified metrics. Document exception if rollback blocked. Open corrective actions in incident module. Regulator pack: timeline, affected population, metrics, mitigations, contact point.",
                "scoringCriteria": [
                    "Rollback strategy articulated",
                    "Exception / waiver documentation",
                    "Regulator-ready summary",
                    "Cross-module traceability (registry + incident)"
                ],
                "frameworkRefs": ["EU AI Act Art. 73", "ISO 42001 10.2", "NIST AI RMF GOVERN 1.3"],
                "timeAllocation": 20
            }
        ]
    },
    {
        "id": "ai_vendor_llm_breach",
        "type": "ai_incident",
        "title": "Third-Party LLM Provider Breach",
        "description": "Your embedded LLM vendor discloses unauthorized access to fine-tuning datasets that included customer support transcripts from your tenant.",
        "difficulty": "intermediate",
        "estimatedTime": "35-45 min",
        "triggers": ["EU AI Act Art. 73", "Vendor Intake", "GDPR Art. 33"],
        "steps": [
            {
                "step": 1,
                "title": "Vendor Notification & Scope",
                "prompt": "Vendor email: 'Potential access to subset of fine-tuning data between Jan–Mar.' Your vendor intake score was Medium; DPA requires 24h customer notification.",
                "context": "Three production features use this vendor API. Support chat fine-tuning included PII you attempted to scrub.",
                "questions": [
                    "What do you ask the vendor in the first call?",
                    "How do you map affected AI systems in your inventory?",
                    "GDPR vs. AI Act notification — who leads?"
                ],
                "expertGuidance": "Request IOCs, tenant isolation proof, exact fields accessed, and retention status. Link vendor record to model registry entries. DPO leads GDPR; AI governance lead leads Art. 73 assessment. Pull vendor intake assessment and gaps as evidence.",
                "scoringCriteria": [
                    "Structured vendor questions",
                    "Inventory / registry mapping",
                    "GDPR vs AI Act roles clear",
                    "Vendor intake evidence reused"
                ],
                "frameworkRefs": ["GDPR Art. 33", "EU AI Act Art. 73", "ISO 42001 8.4"],
                "timeAllocation": 20
            },
            {
                "step": 2,
                "title": "Containment & Contractual Response",
                "prompt": "Vendor cannot confirm exfiltration volume. Legal asks whether to suspend API keys for all three features.",
                "context": "One feature is revenue-critical; failover model exists but untested in prod.",
                "questions": [
                    "Suspend, throttle, or failover?",
                    "How do you document the vendor exception if service continues?",
                    "Customer communication draft — key points?"
                ],
                "expertGuidance": "Failover to internal/alternate model where tested; otherwise throttle and disable fine-tuning pipelines. Log exception with expiry and compensating controls. Customer comms: facts known, actions taken, no speculation, support channel.",
                "scoringCriteria": [
                    "Proportionate containment",
                    "Exception documentation",
                    "Customer communication quality"
                ],
                "frameworkRefs": ["EU AI Act Art. 73", "NIST AI RMF GOVERN 6.1", "ISO 42001 A.10"],
                "timeAllocation": 15
            }
        ]
    },
    {
        "id": "vendor_breach",
        "type": "vendor_breach",
        "title": "Third-Party Vendor Data Breach",
        "description": "Your cloud analytics provider notifies you they suffered a data breach. Your customer data in their system — including PII and usage analytics for 200,000 users — was accessed by an unauthorized party. The vendor is a critical part of your data pipeline.",
        "difficulty": "intermediate",
        "estimatedTime": "40-55 min",
        "triggers": ["SOC 2 CC9.2", "SOC 2 CC5.2", "GDPR Art. 28", "NIST 800-53 SR-4"],
        "steps": [
            {
                "step": 1,
                "title": "Initial Triage",
                "prompt": "You receive an email from your analytics vendor's security team at 10 PM: 'We experienced unauthorized access to our data processing environment. Your tenant data, including the customer_profiles and usage_events datasets, was accessed between March 3-5. We are still investigating. More details to follow within 48 hours.'",
                "context": "This is a third-party breach. You are the data controller. The vendor is the processor. Your responsibilities under GDPR and state laws are not waived because a vendor was breached.",
                "questions": [
                    "What information do you immediately request from the vendor?",
                    "Who do you notify internally?",
                    "Do you have any notification obligations yet, or do you wait for more information?"
                ],
                "expertGuidance": "Immediately request from vendor: specific data fields accessed, number of records, jurisdictions, breach timeline, containment status. Notify internally: CISO, DPO, General Counsel, CTO. The GDPR 72-hour clock starts when YOU become aware. Check your DPA: what are the vendor's contractual notification obligations?",
                "scoringCriteria": [
                    "Were specific information requests made to the vendor?",
                    "Was the 'controller liability' concept recognized?",
                    "Was the GDPR 72-hour clock started?",
                    "Were DPO and legal counsel engaged?",
                    "Was the DPA/contract reviewed?"
                ],
                "frameworkRefs": ["GDPR Art. 28", "GDPR Art. 33", "SOC 2 CC5.2", "ISO 27001 A.15"],
                "timeAllocation": 15
            },
            {
                "step": 2,
                "title": "Regulatory & Customer Notification",
                "prompt": "The vendor provides an update: customer_profiles included names, emails, DOB, addresses. Usage_events includes feature usage patterns. Affected: US (180k), EU (15k), UK (5k). Root cause investigation ongoing.",
                "context": "Multi-jurisdictional breach notification event. You are the data controller.",
                "questions": [
                    "What are your notification obligations to regulators?",
                    "How do you notify affected individuals?",
                    "How do you coordinate messaging with the vendor?"
                ],
                "expertGuidance": "Regulatory: Notify EU supervisory authority within 72 hours, UK ICO within 72 hours, relevant US state AGs. Individual notification: GDPR requires individual notice if high risk. Notify via email, website banner, in-app notification. Coordinate all public statements with the vendor.",
                "scoringCriteria": [
                    "Were EU/UK regulatory notifications addressed?",
                    "Were individual notifications planned?",
                    "Was multi-channel notification considered?",
                    "Was vendor coordination addressed?"
                ],
                "frameworkRefs": ["GDPR Art. 33-34", "UK GDPR Art. 33-34", "SOC 2 CC9.2"],
                "timeAllocation": 20
            },
            {
                "step": 3,
                "title": "Vendor Relationship & Future Prevention",
                "prompt": "Root cause: intern committed API key to public GitHub repo. Key was active for 9 days. Vendor had no secret scanning, no key rotation, no admin panel logging.",
                "context": "Your organization relied on this vendor for critical data processing. Customers are asking if data is still safe.",
                "questions": [
                    "Do you continue working with this vendor? Conditions?",
                    "What due diligence gaps existed?",
                    "How do you prevent this with other vendors?"
                ],
                "expertGuidance": "Vendor requirements: SOC 2 Type II within 90 days, secret scanning, mandatory key rotation, admin panel logging, penetration test. Overhaul vendor assessment: add secret management to questionnaires, require SOC 2/ISO for PII processors, annual reviews, vendor risk register.",
                "scoringCriteria": [
                    "Were specific vendor remediation requirements identified?",
                    "Was vendor assessment overhaul described?",
                    "Was ongoing vendor monitoring addressed?",
                    "Were contractual/DPA updates considered?"
                ],
                "frameworkRefs": ["SOC 2 CC5.2", "ISO 27001 A.15.1", "GDPR Art. 28", "NIST 800-53 SR-6"],
                "timeAllocation": 15
            }
        ]
    },
    {
        "id": "data_breach",
        "type": "data_breach",
        "title": "Customer Data Exposure via Misconfigured S3 Bucket",
        "description": "A security researcher notifies you that a public S3 bucket contains 500,000 customer records including names, addresses, and partial payment information. The bucket has been publicly accessible for 8 months.",
        "difficulty": "beginner",
        "estimatedTime": "30-45 min",
        "triggers": ["SOC 2 CC6.1", "SOC 2 CC7.3", "ISO 27001 A.8.2", "GDPR Art. 33"],
        "steps": [
            {
                "step": 1,
                "title": "Immediate Response",
                "prompt": "A security researcher emails your security@ alias: 'Your S3 bucket customer-analytics-prod is publicly readable. Contains 500K+ records with PII.' DevOps confirms the bucket policy allows public read access.",
                "context": "The bucket has been public for 8 months. Data includes names, emails, addresses, phone numbers, partial credit card data for 500,000 customers.",
                "questions": [
                    "What is your immediate response in the first 15 minutes?",
                    "Do you acknowledge the researcher's finding?",
                    "How do you determine who accessed the data?"
                ],
                "expertGuidance": "Immediately restrict bucket to private. Enable S3 server access logs and CloudTrail. Acknowledge researcher professionally. Notify CISO, General Counsel, DPO within 15 minutes.",
                "scoringCriteria": [
                    "Was the bucket immediately secured?",
                    "Was access logging enabled?",
                    "Was the researcher acknowledged professionally?",
                    "Were key stakeholders notified?"
                ],
                "frameworkRefs": ["SOC 2 CC6.1", "ISO 27001 A.8.2", "NIST 800-53 AC-6"],
                "timeAllocation": 15
            },
            {
                "step": 2,
                "title": "Scope & Notification Assessment",
                "prompt": "CloudTrail shows 47 unique IPs across 12 countries over 8 months. Some access suggests automated scraping. Customers in all 50 US states, EU, and California affected.",
                "context": "Triggers GDPR, CCPA, and all 50 US state breach notification laws. The 72-hour GDPR clock is ticking.",
                "questions": [
                    "Which jurisdictions require notification?",
                    "How do you prioritize notifications?",
                    "What must each notification contain?"
                ],
                "expertGuidance": "GDPR: 72 hours to authority, individual notice if high risk. CCPA: without unreasonable delay. All 50 states: 30-60 days. Prioritize: GDPR first, then CA, then others. Engage outside privacy counsel.",
                "scoringCriteria": [
                    "Were multi-jurisdictional obligations identified?",
                    "Was GDPR 72-hour deadline recognized?",
                    "Was legal counsel engaged?"
                ],
                "frameworkRefs": ["GDPR Art. 33-34", "CCPA 1798.82", "SOC 2 CC9.2"],
                "timeAllocation": 20
            },
            {
                "step": 3,
                "title": "Root Cause & Prevention",
                "prompt": "Root cause: data engineer created bucket for one-time export, left default public-read policy. No automated scanning for public buckets. No data classification policy.",
                "context": "Process failure, not malicious. Engineer wasn't trained. No guardrails existed.",
                "questions": [
                    "What controls would have prevented this?",
                    "What detection mechanisms should be in place?",
                    "How do you ensure secure data handling across engineering?"
                ],
                "expertGuidance": "Preventive: S3 Block Public Access at account level, AWS Config rules to detect public buckets, data classification policy, mandatory training. Detective: CSPM scanning, automated alerts for public bucket creation. Process: security review for new S3 buckets.",
                "scoringCriteria": [
                    "Were preventive controls identified?",
                    "Were detective controls identified?",
                    "Was data classification policy addressed?",
                    "Was training addressed?"
                ],
                "frameworkRefs": ["SOC 2 CC6.1", "SOC 2 CC7.2", "ISO 27001 A.8.2", "NIST 800-53 AC-3"],
                "timeAllocation": 15
            }
        ]
    }
]


def list_scenarios():
    return SCENARIOS


def get_scenario(scenario_id: str):
    for s in SCENARIOS:
        if s["id"] == scenario_id:
            return s
    return None
