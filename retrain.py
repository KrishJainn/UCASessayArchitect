#!/usr/bin/env python3
"""
FULL RETRAIN SCRIPT
Ingests all PDFs from /pdfs and runs analysis.
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import backend

PDF_DIR = "pdfs"

def main():
    # 1. List all PDFs
    pdfs = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
    print(f"Found {len(pdfs)} PDFs to ingest...")
    
    # 2. Ingest each one
    for i, pdf_name in enumerate(pdfs):
        pdf_path = os.path.join(PDF_DIR, pdf_name)
        print(f"[{i+1}/{len(pdfs)}] Ingesting: {pdf_name}")
        try:
            backend.ingest_essay(pdf_path)
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n--- INGESTION COMPLETE ---\n")
    
    # 3. Run analysis
    print("Running full analysis...")
    result = backend.analyze_all_essays()
    
    if "error" in result:
        print(f"ANALYSIS FAILED: {result['error']}")
    else:
        print("ANALYSIS COMPLETE!")
        bp = result.get("Structure_Blueprint", {})
        print(f"  Q1: {bp.get('Q1_percentage')}%")
        print(f"  Q2: {bp.get('Q2_percentage')}%")
        print(f"  Q3: {bp.get('Q3_percentage')}%")
        print(f"  Notes: {bp.get('notes')}")

if __name__ == "__main__":
    main()
