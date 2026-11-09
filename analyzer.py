"""
Core logic: text extraction, Ollama AI analysis,
chunk merging, and report formatting.
"""

import json
import os
import re
from pathlib import Path
from typing import Any, Dict, List

from dotenv import load_dotenv
from openai import OpenAI

from chunker import chunk_text
from prompts import ANALYSIS_PROMPT, COMBINE_PROMPT, SYSTEM_PROMPT


# Load environment variables
load_dotenv()


# ---------- Configuration ----------

MODEL = os.getenv("OPENAI_MODEL", "llama3.2:3b")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "6000"))

OLLAMA_BASE_URL = "http://localhost:11434/v1"

_client = None


# ---------- 1. Ollama Client ----------

def get_client() -> OpenAI:
    """
    Connect to the locally running Ollama server.
    No actual API key is required.
    """

    global _client

    if _client is None:
        _client = OpenAI(
            base_url=OLLAMA_BASE_URL,
            api_key="ollama"
        )

    return _client


# ---------- 2. Text Extraction ----------

def extract_text(path: str) -> str:

    p = Path(path)

    if not p.exists():
        raise SystemExit(f"File not found: {path}")

    if p.suffix.lower() == ".pdf":

        from pypdf import PdfReader

        reader = PdfReader(str(p))

        return "\n\n".join(
            (page.extract_text() or "")
            for page in reader.pages
        )

    return p.read_text(
        encoding="utf-8",
        errors="ignore"
    )


# ---------- 3. Text Preprocessing ----------

def preprocess(text: str) -> str:

    text = text.replace("\r\n", "\n")

    text = re.sub(
        r"[ \t]+",
        " ",
        text
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text
    )

    return text.strip()


# ---------- 4. Ollama AI Call ----------

def _call_gpt(user_prompt: str) -> Dict[str, Any]:
    """
    Send prompts to Llama through Ollama.
    Enforce JSON output and parse the response.
    """

    try:

        response = get_client().chat.completions.create(

            model=MODEL,

            temperature=0,

            response_format={
                "type": "json_object"
            },

            messages=[
                {
                    "role": "system",
                    "content": (
                        SYSTEM_PROMPT
                        + "\n\n"
                        + "You MUST return only a valid JSON object. "
                        + "Do not include Markdown or explanations "
                        + "outside the JSON object."
                    )
                },
                {
                    "role": "user",
                    "content": (
                        user_prompt
                        + "\n\n"
                        + "Return a complete valid JSON object."
                    )
                }
            ]
        )

        raw = response.choices[0].message.content or ""

        raw = raw.strip()

        # Remove Markdown code blocks
        raw = re.sub(
            r"^```(?:json)?\s*|\s*```$",
            "",
            raw,
            flags=re.IGNORECASE
        ).strip()

        # Parse JSON
        try:

            result = json.loads(raw)

            if not isinstance(result, dict):
                raise ValueError(
                    "Expected a JSON object."
                )

            return result

        except json.JSONDecodeError:

            # Try extracting JSON from additional text
            match = re.search(
                r"\{.*\}",
                raw,
                re.DOTALL
            )

            if match:

                result = json.loads(
                    match.group(0)
                )

                if isinstance(result, dict):
                    return result

            print("\n[ERROR] Invalid JSON received from Llama.")

            print("\n[DEBUG] Model response:")
            print(raw)

            raise ValueError(
                "Llama returned invalid JSON."
            )

    except Exception as e:

        print(f"\n[ERROR] Ollama API Error: {e}")

        raise


# ---------- 5. Analyze Individual Chunk ----------

def analyze_chunk(chunk: str) -> Dict[str, Any]:

    prompt = ANALYSIS_PROMPT.format(
        document=chunk
    )

    return _call_gpt(prompt)


# ---------- 6. Combine Multiple Chunk Results ----------

def combine_results(
    partials: List[Dict[str, Any]]
) -> Dict[str, Any]:

    prompt = COMBINE_PROMPT.format(
        partials=json.dumps(
            partials,
            indent=2,
            ensure_ascii=False
        )
    )

    return _call_gpt(prompt)


# ---------- 7. Full Analysis Pipeline ----------

def analyze_document(
    text: str,
    verbose: bool = True
) -> Dict[str, Any]:

    # Preprocess document
    text = preprocess(text)

    # Split document into chunks
    chunks = chunk_text(
        text,
        max_chars=CHUNK_SIZE
    )

    if not chunks:
        raise ValueError(
            "The document contains no readable text."
        )

    if verbose:

        print(
            f"[info] Document split into {len(chunks)} chunk(s)."
        )

        print(
            f"[info] AI Model: {MODEL}"
        )

        print(
            "[info] Using Ollama Local API."
        )

    # Analyze single chunk
    if len(chunks) == 1:

        return analyze_chunk(chunks[0])

    # Analyze multiple chunks
    partials = []

    for i, chunk in enumerate(chunks, 1):

        if verbose:

            print(
                f"[info] Analyzing chunk {i}/{len(chunks)}..."
            )

        result = analyze_chunk(chunk)

        partials.append(result)

    # Combine results
    if verbose:

        print(
            "[info] Combining chunk results..."
        )

    return combine_results(partials)


# ---------- 8. Report Formatting ----------

def _bullets(items) -> str:

    if isinstance(items, str):
        items = [items]

    if not items:
        return "• Not specified"

    return "\n".join(
        f"• {item}"
        for item in items
    )


def format_report(r: Dict[str, Any]) -> str:

    def g(key):
        return r.get(key, "Not specified")

    return f"""
LEGAL DOCUMENT ANALYSIS
--------------------------------

Document Type:
{g('document_type')}

Parties:
{_bullets(g('parties'))}

Purpose:
{g('purpose')}

Duration:
{g('duration')}

Key Obligations:
{_bullets(g('key_obligations'))}

Payment:
{g('payment')}

Termination:
{g('termination')}

Important Dates:
{_bullets(g('important_dates'))}

Governing Law:
{g('governing_law')}

Potentially Important Clauses:
{_bullets(g('key_clauses'))}

Summary:
{g('summary')}

--------------------------------
Note: AI-generated analysis for learning purposes.
Not legal advice.
"""


# ---------- 9. Save Results ----------

def save_results(
    result: Dict[str, Any],
    report: str,
    out_dir: str,
    stem: str
) -> None:

    out = Path(out_dir)

    # Create results directory
    out.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save JSON report
    json_path = out / f"{stem}_analysis.json"

    json_path.write_text(
        json.dumps(
            result,
            indent=2,
            ensure_ascii=False
        ),
        encoding="utf-8"
    )

    # Save TXT report
    txt_path = out / f"{stem}_analysis.txt"

    txt_path.write_text(
        report,
        encoding="utf-8"
    )

    print(
        f"[info] Saved results to {txt_path} and {json_path}"
    )