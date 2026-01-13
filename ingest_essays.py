import os
import glob
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

def load_pdfs(directory_path):
    print(f"Loading PDFs from {directory_path}...")
    documents = []
    pdf_files = glob.glob(os.path.join(directory_path, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {directory_path}")
        return []

    for pdf_file in pdf_files:
        try:
            loader = PyPDFLoader(pdf_file)
            docs = loader.load()
            documents.extend(docs)
            print(f"Loaded {pdf_file} ({len(docs)} pages)")
        except Exception as e:
            print(f"Error loading {pdf_file}: {e}")
            
    return documents

def split_text(documents):
    print("Splitting text into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True,
    )
    all_splits = text_splitter.split_documents(documents)
    print(f"Created {len(all_splits)} chunks.")
    return all_splits

def store_in_chroma(chunks, persist_directory="./chroma_db"):
    print("Initializing Vector Database...")
    # Use a lightweight local embedding model
    embedding_function = HuggingFaceEmbeddings(
        model_name="all-MiniLM-L6-v2",
        model_kwargs={'device': 'cpu'}
    )
    
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embedding_function,
        persist_directory=persist_directory,
        collection_name="college_essays"
    )
    print(f"Stored {len(chunks)} chunks in ChromaDB at {persist_directory}")
    return vectorstore

def main():
    # Directory containing PDFs
    pdf_dir = "pdfs"
    
    # Ensure the directory exists
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)
        print(f"Created directory '{pdf_dir}'. Please put your PDF files there.")
        return

    documents = load_pdfs(pdf_dir)
    if not documents:
        print("No documents found to process. Please add PDF files to the 'pdfs' folder.")
        return

    chunks = split_text(documents)
    if not chunks:
        print("No text chunks created.")
        return

    vectorstore = store_in_chroma(chunks)
    
    # Verification query
    print("\n--- Verifying with a sample query ---")
    query = "essay" # Generic query
    print(f"Querying for: '{query}'")
    results = vectorstore.similarity_search(query, k=1)
    if results:
        print(f"Top result match:\n{results[0].page_content[:200]}...")
    else:
        print("No results found for verification query.")

if __name__ == "__main__":
    main()
