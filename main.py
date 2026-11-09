"""Automated Legal Document Analyzer using GPT-4 (Experiment 5, 24CS2506).

Usage:
    python main.py                                   # analyzes the sample document
    python main.py path/to/contract.txt              # your own .txt or .pdf
    python main.py path/to/contract.pdf --out results
"""

import argparse
from pathlib import Path

from analyzer import analyze_document, extract_text, format_report, save_results


def main() -> None:
    parser = argparse.ArgumentParser(description="GPT-4 Legal Document Analyzer")
    parser.add_argument(
        "file",
        nargs="?",
        default="sample_documents/employment_agreement.txt",
        help="Path to a .txt or .pdf legal document",
    )
    parser.add_argument("--out", default="results", help="Output folder")
    args = parser.parse_args()

    text = extract_text(args.file)
    print(f"[info] Loaded {args.file} ({len(text)} characters)")

    result = analyze_document(text)
    report = format_report(result)

    print("\n" + report)
    save_results(result, report, args.out, Path(args.file).stem)


if __name__ == "__main__":
    main()
