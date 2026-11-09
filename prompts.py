"""Prompt templates for the Legal Document Analyzer (Role + Task + Extract + Constraint + Format)."""

SYSTEM_PROMPT = (
    "You are a legal document analysis assistant. "
    "You analyze and summarize the provided document. "
    "Use ONLY information present in the document. Do not invent facts. "
    "If an item is not mentioned, write \"Not specified\". "
    "You do not give legal advice."
)

ANALYSIS_PROMPT = """Analyze the legal document below and return ONLY a valid JSON object
(no markdown, no commentary) with exactly these keys:

{{
  "document_type": "string",
  "parties": ["string"],
  "purpose": "string",
  "duration": "string",
  "key_obligations": ["string"],
  "payment": "string",
  "termination": "string",
  "important_dates": ["string"],
  "governing_law": "string",
  "key_clauses": ["string"],
  "summary": "string (abstractive summary, 3-5 sentences, plain English)"
}}

Rules:
- Use only information present in the document. Do not invent facts.
- Use "Not specified" for missing items (or an empty list for list fields).
- For "key_clauses", name clauses such as Confidentiality, Payment, Termination,
  Liability, Intellectual Property, Dispute Resolution if they are present.

DOCUMENT:
\"\"\"
{document}
\"\"\"
"""

COMBINE_PROMPT = """Below are partial analyses (JSON) of consecutive chunks of ONE legal document.
Merge them into a single final analysis using the same JSON schema and the same rules.
Remove duplicates, resolve overlaps, and write one coherent summary for the whole document.
Return ONLY a valid JSON object.

PARTIAL ANALYSES:
{partials}
"""
