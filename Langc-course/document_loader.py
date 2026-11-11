import os
import tempfile
from pathlib import Path
from langchain_community.document_loaders import ( 
    DirectoryLoader,
    TextLoader,
    WebBaseLoader,
    PyPDFLoader,
)
from langchain_core.documents import Document


from dotenv import load_dotenv

load_dotenv()

def load_text_file():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as temp_file:
        temp_file.write(b"Hello, this is a sample text file.")
        temp_file.flush()
        temp_file_path = temp_file.name

    try:
        loader = TextLoader(temp_file_path)
        documents = loader.load()

        print(f"Loaded {len(documents)} documents.")
        print(f"Content preview: {documents[0].page_content[:100]}...")
        print(f"Metadata: {documents[0].metadata}")

        # for doc in documents:
        #     print("Document content:")
        #     print(doc)
        #     print(doc.page_content)
    finally:
        os.remove(temp_file_path)

def web_loader():
    loader = WebBaseLoader("https://www.doomanman.com",
                           bs_kwargs={"parse_only": None})
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from the web.")
    print(f"Content preview: {documents[0].page_content[:100]}...")
    print(f"Metadata: {documents[0].metadata}")

def lazy_loader():
    with tempfile.TemporaryDirectory() as temp_dir:

        for i in range(5):
            path = Path(temp_dir) / f"doc_{i}.txt"
            path.write_text(f"This is the content of document {i}. It contains some sample text.")

        loader = DirectoryLoader(temp_dir,
                                 glob="*.txt",
                                 loader_cls=TextLoader)
        
        print("Initializing lazy loader for directory:", temp_dir)
        for doc in loader.lazy_load():
            print(f"Content preview: {doc.page_content[:100]}...")
            print(f"Metadata: {doc.metadata}")
        
def doc_structure():
    doc = Document(
        page_content="Sample content", 
        metadata={"source": "manual_creation.txt", "author": "test", 
                  "created_at": "2024-06-06",
                  "tags": ["sample", "test"]
        }
    )
    print("Document structure:")
    print(f"Page content (type: {type(doc.page_content)})")
    print(f"Document content: {doc.page_content}")
    print(f"Document metadata: {doc.metadata}")

    updated_doc = Document(
        page_content=doc.page_content + " Updated content.",
        metadata={**doc.metadata, "updated_at": "2024-06-06"}
    )
    print("Updated document structure:")
    print(f"Page content (type: {type(updated_doc.page_content)})")
    print(f"Document content: {updated_doc.page_content}")
    print(f"Document metadata: {updated_doc.metadata}")

def pdf_loader(pdf_path: str):
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    print(f"Loaded {len(documents)} documents from PDF.")
    print(f"Content preview: {documents[0].page_content[:100]}...")
    print(f"Metadata: {documents[0].metadata}")

if __name__ == "__main__":
    #load_text_file()
    #web_loader()
    #lazy_loader()
    #doc_structure()
    pdf_loader("./docs/langchain_demo.pdf")

    
    