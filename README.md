# Experiment 5: Automated Legal Document Analyzer using GPT-4
**Course:** 24CS2506 – Building Applications using GPT-4

A command-line tool that reads a legal document (`.txt` or `.pdf`), sends it to GPT-4, and produces a structured analysis: document type, parties, purpose, duration, obligations, payment, termination, important dates, governing law, key clauses and a plain-English summary.

## Workflow

```
Legal Document -> Text Extraction -> Preprocessing -> Chunking
   -> Prompt Generation -> GPT-4 -> Information Extraction
   -> (Merge chunk results) -> Structured Report -> Save Results
```

## Project structure

```
legal_analyzer/
├── main.py                  # CLI entry point
├── analyzer.py              # extraction, GPT-4 calls, merging, report, saving
├── chunker.py               # paragraph-aware chunking with overlap
├── prompts.py               # Role + Task + Extract + Constraint + Format prompts
├── requirements.txt
├── .env.example             # copy to .env and add your key
├── sample_documents/
│   └── employment_agreement.txt
└── results/                 # created automatically
```

## Setup in VS Code

1. Install Python 3.9+ and open this folder in VS Code (`File > Open Folder`).
2. Open the terminal (`Ctrl + ` `) and create a virtual environment:

   **Windows**
   ```
   python -m venv venv
   venv\Scripts\activate
   ```
   **macOS / Linux**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```
3. In VS Code press `Ctrl+Shift+P` -> **Python: Select Interpreter** -> choose the `venv` one.
4. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Create your `.env` file:
   ```
   copy .env.example .env      (Windows)
   cp .env.example .env        (macOS / Linux)
   ```
   Open `.env` and replace `your-openai-api-key-here` with your real OpenAI API key.

## Run

```
python main.py                                  # analyzes the sample employment agreement
python main.py path/to/contract.pdf             # your own .txt or .pdf
python main.py path/to/contract.pdf --out out   # custom output folder
```

Results are printed in the terminal and saved to `results/<name>_analysis.txt` and `.json`.

## Expected output (format)

```
LEGAL DOCUMENT ANALYSIS
--------------------------------
Document Type:
Employment Agreement

Parties:
• Nova Tech Solutions Pvt. Ltd. (Employer)
• Arjun Kumar (Employee)
...
Summary:
This agreement defines the terms of employment...
```

## How it works

- **Prompting:** `prompts.py` gives GPT-4 a role, task, fields to extract, the constraint "use only information in the document, do not invent facts", and a JSON output format.
- **Abstractive summarization:** GPT-4 writes a new summary from the meaning of the document rather than copying sentences.
- **Chunking:** documents longer than `CHUNK_SIZE` characters are split into overlapping chunks, each analyzed separately, then merged by a second GPT-4 call.
- **temperature=0** keeps output factual and repeatable.

## Troubleshooting

- `OPENAI_API_KEY not found` -> make sure `.env` exists in this folder (not `.env.example`).
- `ModuleNotFoundError` -> activate the venv and run `pip install -r requirements.txt`.
- `model not found` / access error -> set `OPENAI_MODEL=gpt-4o` (or another model your account can use) in `.env`.
- Scanned PDFs with no selectable text will return empty text (OCR is not included).

*AI-generated analysis for learning purposes. Not legal advice.*
