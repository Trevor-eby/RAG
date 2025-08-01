import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    PyMuPDFLoader,
    UnstructuredPDFLoader,
    PyPDFDirectoryLoader,
    TextLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredHTMLLoader,
    CSVLoader,
    UnstructuredEPubLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.schema.document import Document
from langchain_chroma import Chroma
from backend.get_embedding_function import get_embedding_function

CHROMA_PATH = "chroma"

def load_pdf_with_fallback(file_path: str):
    """Try multiple PDF loaders in order of preference."""
    pdf_loaders = [
        ("PyMuPDFLoader", lambda: PyMuPDFLoader(file_path)),
        ("UnstructuredPDFLoader", lambda: UnstructuredPDFLoader(file_path, mode="single")),
        ("PyPDFLoader", lambda: PyPDFLoader(file_path))
    ]
    
    for loader_name, loader_func in pdf_loaders:
        try:
            print(f"Trying {loader_name} for {os.path.basename(file_path)}")
            loader = loader_func()
            documents = loader.load()
            
            # Check if we got meaningful content
            total_content = sum(len(doc.page_content.strip()) for doc in documents)
            if total_content > 0:
                print(f"✓ Successfully loaded {len(documents)} pages using {loader_name}")
                return documents
            else:
                print(f"✗ {loader_name} returned empty content")
                
        except Exception as e:
            print(f"✗ {loader_name} failed: {str(e)}")
            continue
    
    raise ValueError(f"All PDF loaders failed for {file_path}")

def load_file(file_path: str):
    """Load a document from file path based on file extension."""
    ext = os.path.splitext(file_path)[1].lower()

    try:
        if ext == ".pdf":
            documents = load_pdf_with_fallback(file_path)
        elif ext in [".txt", ".md"]:
            loader = TextLoader(file_path, encoding="utf-8")
            documents = loader.load()
        elif ext == ".docx":
            loader = UnstructuredWordDocumentLoader(file_path)
            documents = loader.load()
        elif ext in [".html", ".htm"]:
            loader = UnstructuredHTMLLoader(file_path)
            documents = loader.load()
        elif ext == ".csv":
            loader = CSVLoader(file_path)
            documents = loader.load()
        elif ext == ".epub":
            loader = UnstructuredEPubLoader(file_path)
            documents = loader.load()
        else:
            raise ValueError(f"Unsupported file extension: {ext}")

        # Validate that we got content
        if not documents:
            raise ValueError(f"No documents loaded from {file_path}")
        
        total_content = sum(len(doc.page_content.strip()) for doc in documents)
        if total_content == 0:
            raise ValueError(f"All documents from {file_path} are empty")
            
        print(f"✓ Loaded {len(documents)} documents from {os.path.basename(file_path)} ({total_content} characters)")
        return documents
        
    except Exception as e:
        print(f"✗ Failed to load {file_path}: {e}")
        raise

def calculate_chunk_ids(chunks):
    """Calculate unique IDs for document chunks based on source and page."""
    last_page_id = None
    current_chunk_index = 0

    for chunk in chunks:
        source = chunk.metadata.get("source")
        page = chunk.metadata.get("page", 0)  # Default to 0 if no page info
        current_page_id = f"{source}:{page}"

        if current_page_id == last_page_id:
            current_chunk_index += 1
        else:
            current_chunk_index = 0

        chunk_id = f"{current_page_id}:{current_chunk_index}"
        last_page_id = current_page_id
        chunk.metadata["id"] = chunk_id

    return chunks

def process_and_add_file_to_db(file_path: str, pdf_loader_preference: str = "auto"):
    """Process a file and add new chunks to the vector database.
    
    Args:
        file_path: Path to the file to process
        pdf_loader_preference: For PDFs, specify "pymupdf", "unstructured", "pypdf", or "auto"
    """
    try:
        # Override PDF loading if specific loader requested
        if file_path.lower().endswith('.pdf') and pdf_loader_preference != "auto":
            documents = load_pdf_with_specific_loader(file_path, pdf_loader_preference)
        else:
            documents = load_file(file_path)
    except Exception as e:
        print(f"Error loading file {file_path}: {e}")
        return

    # Split documents into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=80,
        length_function=len,
        is_separator_regex=False,
    )
    chunks = text_splitter.split_documents(documents)
    
    if not chunks:
        print(f"No chunks created from {os.path.basename(file_path)}")
        return
        
    chunks = calculate_chunk_ids(chunks)

    # Initialize or connect to existing Chroma database
    db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
    
    # Get existing IDs to avoid duplicates
    existing_items = db.get(include=[])
    existing_ids = set(existing_items["ids"])

    # Filter out chunks that already exist
    new_chunks = [chunk for chunk in chunks if chunk.metadata["id"] not in existing_ids]

    if new_chunks:
        new_ids = [chunk.metadata["id"] for chunk in new_chunks]
        db.add_documents(new_chunks, ids=new_ids)
        print(f"✓ Added {len(new_chunks)} new chunks from {os.path.basename(file_path)}")
    else:
        print(f"No new chunks to add for {os.path.basename(file_path)}")

def load_pdf_with_specific_loader(file_path: str, loader_type: str):
    """Load PDF with a specific loader."""
    loaders = {
        "pymupdf": lambda: PyMuPDFLoader(file_path),
        "unstructured": lambda: UnstructuredPDFLoader(file_path, mode="single"),
        "pypdf": lambda: PyPDFLoader(file_path)
    }
    
    if loader_type not in loaders:
        raise ValueError(f"Unknown PDF loader: {loader_type}")
    
    try:
        loader = loaders[loader_type]()
        documents = loader.load()
        print(f"✓ Loaded {len(documents)} documents using {loader_type}")
        return documents
    except Exception as e:
        print(f"✗ {loader_type} failed: {e}")
        raise

def process_directory(directory_path: str):
    """Process all supported files in a directory."""
    supported_extensions = {'.pdf', '.txt', '.md', '.docx', '.html', '.htm', '.csv', '.epub'}
    
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if os.path.splitext(file)[1].lower() in supported_extensions:
                file_path = os.path.join(root, file)
                print(f"Processing: {file_path}")
                process_and_add_file_to_db(file_path)

def clear_database():
    """Clear all documents from the database."""
    if os.path.exists(CHROMA_PATH):
        import shutil
        shutil.rmtree(CHROMA_PATH)
        print("Database cleared successfully")
    else:
        print("Database directory doesn't exist")

def get_database_stats():
    """Get statistics about the current database."""
    try:
        db = Chroma(persist_directory=CHROMA_PATH, embedding_function=get_embedding_function())
        existing_items = db.get(include=[])
        total_chunks = len(existing_items["ids"])
        
        # Count documents by source
        sources = {}
        for item_id in existing_items["ids"]:
            source = item_id.split(':')[0]
            sources[source] = sources.get(source, 0) + 1
        
        print(f"Total chunks in database: {total_chunks}")
        print("Documents by source:")
        for source, count in sources.items():
            print(f"  - {os.path.basename(source)}: {count} chunks")
            
    except Exception as e:
        print(f"Error getting database stats: {e}")

if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python script.py <file_path_or_directory>")
        print("       python script.py --clear")
        print("       python script.py --stats")
        sys.exit(1)
    
    arg = sys.argv[1]
    
    if arg == "--clear":
        clear_database()
    elif arg == "--stats":
        get_database_stats()
    elif os.path.isfile(arg):
        process_and_add_file_to_db(arg)
    elif os.path.isdir(arg):
        process_directory(arg)
    else:
        print(f"Path not found: {arg}")