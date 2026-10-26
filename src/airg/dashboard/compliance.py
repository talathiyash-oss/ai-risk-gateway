"""Compliance view content (FR-27): which rules apply, which control addresses each risk, and
who owns the OWASP risks the gateway doesn't cover. Sources: design spec §5, PRD §8,
docs/02-brd/sources.md."""

APPLICABILITY = [
    {"Framework": "NIST AI RMF 1.0 (+ AI 600-1 Generative AI Profile)",
     "Applies to Brindlemoor?": "Voluntary; the US reference point",
     "How it's used": "Main structure for the control mapping"},
    {"Framework": "ISO/IEC 42001:2023",
     "Applies to Brindlemoor?": "Voluntary, certifiable",
     "How it's used": "Shows what an AI management-system audit would ask for"},
    {"Framework": "EU AI Act",
     "Applies to Brindlemoor?": "Yes, through Brindlemoor Wealth S.A. (Luxembourg) as a deployer. The RM copilot is likely not "
                                "high-risk (Annex III); high-risk duties would start 2 December 2027 after the Digital Omnibus",
     "How it's used": "Art. 4 AI literacy measures apply; high-risk articles used as voluntary benchmarks"},
    {"Framework": "Federal Reserve SR 26-2 (model risk; replaced SR 11-7 on 17 April 2026)",
     "Applies to Brindlemoor?": "Generative AI is outside its scope; the FAIR risk model is a quantitative model and likely inside it",
     "How it's used": "Validation evidence for the risk model; general governance for the copilot"},
    {"Framework": "NYDFS Part 500",
     "Applies to Brindlemoor?": "Yes, for Brindlemoor Trust Company of New York",
     "How it's used": "Risk assessment and audit evidence for the certification due 15 April 2027"},
    {"Framework": "GDPR",
     "Applies to Brindlemoor?": "Yes, for Brindlemoor Wealth S.A.",
     "How it's used": "Privacy impact assessment before go-live; personal data removed from audit logs"},
    {"Framework": "OWASP Top 10 for LLM Applications (2025)",
     "Applies to Brindlemoor?": "Industry threat taxonomy",
     "How it's used": "Threat categories for the guardrails and the test suite"},
]

CONTROL_REGISTER = [
    {"ID": "GR-01", "Guardrail": "Prompt-injection detection (prompts and retrieved documents)", "OWASP": "LLM01",
     "NIST AI RMF": "MEASURE 2.7", "ISO/IEC 42001": "A.6 verification & validation", "EU AI Act": "Art. 15*",
     "Status": "Built (Sprint 1)"},
    {"ID": "GR-02", "Guardrail": "PII redaction, entitlement filter on retrieved records, cross-client check", "OWASP": "LLM02, LLM08",
     "NIST AI RMF": "MEASURE 2.10", "ISO/IEC 42001": "A.7 data for AI systems", "EU AI Act": "Art. 10*",
     "Status": "Built (Sprint 1)"},
    {"ID": "GR-03", "Guardrail": "System-prompt leak blocking", "OWASP": "LLM07",
     "NIST AI RMF": "MEASURE 2.7", "ISO/IEC 42001": "A.6 life cycle", "EU AI Act": "Art. 15*",
     "Status": "Built (Sprint 1)"},
    {"ID": "GR-04", "Guardrail": "Rate limits and usage caps", "OWASP": "LLM10",
     "NIST AI RMF": "MANAGE 4.1", "ISO/IEC 42001": "A.6 operation & monitoring", "EU AI Act": "Art. 15*",
     "Status": "Built (Sprint 1)"},
    {"ID": "GR-05", "Guardrail": "Audit log of every gateway decision", "OWASP": "Supports all",
     "NIST AI RMF": "MANAGE 4.1", "ISO/IEC 42001": "A.6 event logging", "EU AI Act": "Art. 12*",
     "Status": "Built (Sprint 1)"},
    {"ID": "GR-06", "Guardrail": "Strip links and images to unapproved domains", "OWASP": "LLM05",
     "NIST AI RMF": "MEASURE 2.7", "ISO/IEC 42001": "A.6 verification & validation", "EU AI Act": "Art. 15*",
     "Status": "Planned (Sprint 2A)"},
]

OWASP_COVERAGE = [
    {"Risk": "LLM01 Prompt Injection", "Coverage": "Gateway: GR-01", "Owner": "This product"},
    {"Risk": "LLM02 Sensitive Information Disclosure", "Coverage": "Gateway: GR-02", "Owner": "This product"},
    {"Risk": "LLM03 Supply Chain", "Coverage": "Out of scope", "Owner": "Third-party risk management: vendor due diligence (ISO/IEC 42001 A.10)"},
    {"Risk": "LLM04 Data and Model Poisoning", "Coverage": "Partly: poisoned documents removed by GR-01", "Owner": "Model vendor (weights, training data); content owners (document review)"},
    {"Risk": "LLM05 Improper Output Handling", "Coverage": "Planned: GR-06 (Sprint 2A)", "Owner": "This product"},
    {"Risk": "LLM06 Excessive Agency", "Coverage": "Not applicable by design: the copilot is read-only", "Owner": "Architecture decision"},
    {"Risk": "LLM07 System Prompt Leakage", "Coverage": "Gateway: GR-03", "Owner": "This product"},
    {"Risk": "LLM08 Vector and Embedding Weaknesses", "Coverage": "GR-02 drops other clients' records before generation (D-9); upstream index fix modelled (FR-31)", "Owner": "This product and the platform team"},
    {"Risk": "LLM09 Misinformation", "Coverage": "Out of scope", "Owner": "Business line: grounding checks and human review of client advice"},
    {"Risk": "LLM10 Unbounded Consumption", "Coverage": "Gateway: GR-04", "Owner": "This product"},
]

CITATION_NOTE = (
    "Framework clause references are drafts from the design spec and still need checking against primary "
    "sources (PRD DEP-4). * = voluntary benchmark unless the system is classed as high-risk."
)
