#!/usr/bin/env python3
"""
FULL RETRAIN SCRIPT (BYPASS CACHE)
Directly creates chromadb client without using cached version.
"""
import os
import sys
import json
from datetime import datetime

# Force reimport
if 'backend' in sys.modules:
    del sys.modules['backend']

# Direct imports without using backend's cached functions
import chromadb
from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

DB_PATH = "/Users/krishjain/Desktop/College essays/chroma_db"
PDF_DIR = "/Users/krishjain/Desktop/College essays/pdfs"
BRAIN_CONFIG_PATH = "/Users/krishjain/Desktop/College essays/brain_config.json"

def main():
    print("=== FRESH RETRAIN (BYPASS CACHE) ===")
    
    # 1. Create fresh chromadb client
    print(f"Creating fresh DB at {DB_PATH}...")
    client = chromadb.PersistentClient(path=DB_PATH)
    
    # 2. Load embedding model
    print("Loading embedding model...")
    embeddings = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    # 3. Create vectorstore
    vectorstore = Chroma(
        client=client,
        collection_name="college_essays",
        embedding_function=embeddings
    )
    
    # 4. Load all PDFs
    pdfs = [f for f in os.listdir(PDF_DIR) if f.endswith('.pdf')]
    print(f"Found {len(pdfs)} PDFs...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,
        chunk_overlap=200
    )
    
    all_chunks = []
    for i, pdf_name in enumerate(pdfs):
        pdf_path = os.path.join(PDF_DIR, pdf_name)
        print(f"[{i+1}/{len(pdfs)}] Loading: {pdf_name}")
        try:
            loader = PyPDFLoader(pdf_path)
            docs = loader.load()
            full_text = "\n".join([d.page_content for d in docs])
            chunks = text_splitter.split_text(full_text)
            for chunk in chunks:
                all_chunks.append(Document(page_content=chunk, metadata={"source": pdf_name}))
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print(f"\nTotal chunks: {len(all_chunks)}")
    
    # 5. Add to vectorstore
    print("Adding chunks to vectorstore...")
    vectorstore.add_documents(all_chunks)
    
    # 6. Verify
    count = vectorstore._collection.count()
    print(f"Vectorstore now has {count} documents.")
    
    # 7. Save basic brain config
    brain_config = {
        "Structure_Blueprint": {
            "Q1_percentage": 20,
            "Q2_percentage": 55,
            "Q3_percentage": 25,
            "typical_total_chars": 4000,
            "notes": "Pending analysis"
        },
        "_metadata": {
            "analyzed_chunks": count,
            "analysis_date": datetime.now().strftime("%c"),
            "model_used": "retrain_script"
        }
    }
    with open(BRAIN_CONFIG_PATH, 'w') as f:
        json.dump(brain_config, f, indent=2)
    
    print(f"\nSaved brain config to {BRAIN_CONFIG_PATH}")
    print("=== RETRAIN COMPLETE ===")

if __name__ == "__main__":
    main()
