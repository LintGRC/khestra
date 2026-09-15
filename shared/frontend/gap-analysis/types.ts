export interface ScopeQuestion {
  id: string;
  text: string;
  hint?: string;
  ifNo?: {
    skipCategories?: string[];
    skipIds?: string[];
  };
}

export interface Question {
  id: string;
  category: string;
  framework: string;
  clause: string;
  text: string;
  hint?: string;
  scopeGate?: string;
}

export interface Category {
  id: string;
  label: string;
  framework: string;
  description: string;
  gate?: string;
}

export interface Result {
  category: string;
  label: string;
  framework: string;
  score: number;
  max: number;
  percent: number;
  gaps: { id: string; text: string; clause: string; hint?: string }[];
}

export interface PhaseProps {
  onNext: () => void;
  onBack?: () => void;
  scopeAnswers: Record<string, boolean>;
  setScopeAnswers: (a: Record<string, boolean>) => void;
  answers: Record<string, boolean>;
  setAnswers: (a: Record<string, boolean>) => void;
}

export const SCOPING: ScopeQuestion[] = [
  { id: "scope_develop", text: "Does your organization develop or deploy AI systems?", hint: "Includes any in-house models, fine-tuned models, or hosted open-source models." },
  { id: "scope_third_party", text: "Do you use third-party AI APIs or vendor AI tools?", hint: "e.g. OpenAI, Anthropic, Azure AI, Salesforce Einstein, Workday AI", ifNo: { skipCategories: ["vendors"], skipIds: ["g7", "o4"] } },
  { id: "scope_decisions", text: "Do your AI systems make decisions affecting individuals?", hint: "e.g. hiring, loan approvals, healthcare triage, insurance pricing", ifNo: { skipCategories: ["bias"], skipIds: ["me2", "m2"] } },
  { id: "scope_personal_data", text: "Do your AI systems process personal data?", hint: "e.g. customer PII, employee data, biometrics, behavioral data", ifNo: { skipCategories: ["data"], skipIds: ["m4", "c3"] } },
  { id: "scope_regulated", text: "Is your organization subject to EU AI Act or similar AI regulation?", hint: "Includes EU AI Act, Canada AIDA, Brazil AI Bill, Colorado AI Act, etc.", ifNo: { skipIds: ["m6"] } },
];

export const CATEGORIES: Category[] = [
  { id: "govern", label: "Governance & Policy", framework: "NIST + ISO", description: "AI governance policies, roles, and accountability" },
  { id: "risk", label: "Risk Management", framework: "NIST + ISO", description: "AI risk assessment, classification, and treatment" },
  { id: "data", label: "Data Governance", framework: "NIST + ISO", description: "Data sourcing, lineage, privacy, and quality", gate: "scope_personal_data" },
  { id: "vendors", label: "Vendor Management", framework: "NIST + ISO", description: "Third-party AI provider oversight", gate: "scope_third_party" },
  { id: "bias", label: "Bias & Fairness", framework: "NIST", description: "Fairness testing, bias mitigation, equity", gate: "scope_decisions" },
  { id: "ops", label: "Operations & Monitoring", framework: "NIST + ISO", description: "Deployment, drift detection, incident response" },
  { id: "docs", label: "Documentation & Transparency", framework: "NIST + ISO", description: "Technical docs, model cards, registries", gate: "scope_regulated" },
];

export const QUESTIONS: Question[] = [
  { id: "g1", category: "govern", framework: "NIST", clause: "GOVERN 1.1", text: "Do you have a documented AI Governance Policy?", hint: "Defines AI principles, risk tolerance, and oversight." },
  { id: "g2", category: "govern", framework: "NIST", clause: "GOVERN 1.2", text: "Is an executive accountable for AI risk management?", hint: "A named C-suite or senior leader." },
  { id: "g3", category: "govern", framework: "NIST", clause: "GOVERN 1.3", text: "Are AI roles and responsibilities defined across teams?" },
  { id: "g4", category: "govern", framework: "NIST", clause: "GOVERN 1.4", text: "Do you maintain an inventory of all AI systems in production?" },
  { id: "g5", category: "govern", framework: "NIST", clause: "GOVERN 1.5", text: "Is there a process for ethical review of new AI use cases?" },
  { id: "g6", category: "govern", framework: "NIST", clause: "GOVERN 1.6", text: "Do you have an AI Acceptable Use Policy for employees?" },

  { id: "r1", category: "risk", framework: "ISO", clause: "ISO 42001 8.2", text: "Are AI risk assessments conducted before deployment?" },
  { id: "r2", category: "risk", framework: "NIST", clause: "MAP 2.1", text: "Are AI systems classified by risk tier (e.g. high/limited/minimal)?" },
  { id: "r3", category: "risk", framework: "ISO", clause: "ISO 42001 8.3", text: "Do you have a process for treating identified AI risks?" },
  { id: "r4", category: "risk", framework: "NIST", clause: "MEASURE 3.4", text: "Are AI risk assessments reviewed and updated periodically?" },

  { id: "d1", category: "data", framework: "NIST", clause: "MAP 2.4", text: "Do you map data sources including training, validation, and production data?", scopeGate: "scope_personal_data" },
  { id: "d2", category: "data", framework: "ISO", clause: "ISO 42001 A.7", text: "Do you have a documented data governance policy for AI systems?", scopeGate: "scope_personal_data" },
  { id: "d3", category: "data", framework: "NIST", clause: "MAP 2.2", text: "Do you identify and document potential harms from data processing?", scopeGate: "scope_personal_data" },
  { id: "d4", category: "data", framework: "ISO", clause: "ISO 42001 4.2", text: "Have you identified interested parties and their AI-related requirements?", scopeGate: "scope_personal_data" },

  { id: "v1", category: "vendors", framework: "NIST", clause: "MAP 2.5", text: "Are third-party AI vendors subject to a formal risk assessment?", scopeGate: "scope_third_party" },
  { id: "v2", category: "vendors", framework: "ISO", clause: "ISO 42001 A.10", text: "Are external AI providers subject to documented controls?", scopeGate: "scope_third_party" },
  { id: "v3", category: "vendors", framework: "NIST", clause: "MAP 2.5", text: "Do you assess AI supply chain dependencies?", scopeGate: "scope_third_party" },

  { id: "b1", category: "bias", framework: "NIST", clause: "MEASURE 3.2", text: "Is bias testing conducted on AI models before deployment?", scopeGate: "scope_decisions" },
  { id: "b2", category: "bias", framework: "NIST", clause: "MEASURE 3.1", text: "Do you have quantitative fairness metrics for AI outputs?", scopeGate: "scope_decisions" },
  { id: "b3", category: "bias", framework: "NIST", clause: "MAP 2.3", text: "Are affected stakeholders identified for each AI system?", scopeGate: "scope_decisions" },

  { id: "o1", category: "ops", framework: "NIST", clause: "MANAGE 4.1", text: "Do you have a documented AI incident response plan?" },
  { id: "o2", category: "ops", framework: "NIST", clause: "MEASURE 3.4", text: "Are AI systems monitored for drift in production?" },
  { id: "o3", category: "ops", framework: "NIST", clause: "MEASURE 3.3", text: "Do you conduct robustness and stress testing?" },
  { id: "o4", category: "ops", framework: "ISO", clause: "ISO 42001 A.6", text: "Is there a version control process for AI systems?" },
  { id: "o5", category: "ops", framework: "NIST", clause: "MANAGE 4.2", text: "Is there a process for escalating AI risks to management?" },
  { id: "o6", category: "ops", framework: "NIST", clause: "MANAGE 4.4", text: "Is there a process for safely decommissioning AI systems?" },
  { id: "o7", category: "ops", framework: "NIST", clause: "MANAGE 4.6", text: "Do you communicate AI risk posture to stakeholders regularly?" },

  { id: "t1", category: "docs", framework: "ISO", clause: "ISO 42001 7.5", text: "Do you maintain technical documentation for each AI system?", scopeGate: "scope_regulated" },
  { id: "t2", category: "docs", framework: "NIST", clause: "MAP 2.6", text: "Have you documented legal/regulatory requirements for each AI system?", scopeGate: "scope_regulated" },
  { id: "t3", category: "docs", framework: "ISO", clause: "ISO 42001 5.2", text: "Is there a documented AI policy communicated across the organization?" },
  { id: "t4", category: "docs", framework: "NIST", clause: "MANAGE 4.3", text: "Do you track corrective actions from AI risk assessments to closure?" },
  { id: "t5", category: "docs", framework: "ISO", clause: "ISO 42001 7.5", text: "Do you maintain records of AI training, audits, and reviews?" },
  { id: "t6", category: "docs", framework: "ISO", clause: "ISO 42001 9.2", text: "Do you conduct internal audits of your AI management system?" },
];
