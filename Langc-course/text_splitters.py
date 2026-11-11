"""
Text Splitters and Chunking Strategies
Optimizing document chunks for RAG
"""

from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    CharacterTextSplitter,
    TokenTextSplitter,
    MarkdownHeaderTextSplitter,
    Language,
)
from langchain_core.documents import Document
from dotenv import load_dotenv

load_dotenv()

# Sample documents for testing
SAMPLE_TEXT = """# Introduction to Machine Learning

Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.

## Types of Machine Learning

### Supervised Learning
Supervised learning uses labeled data to train models. The algorithm learns to map inputs to outputs based on example input-output pairs.

Common algorithms include:
- Linear Regression
- Decision Trees
- Neural Networks

### Unsupervised Learning
Unsupervised learning finds hidden patterns in unlabeled data. The algorithm discovers structure without predefined labels.

Common algorithms include:
- K-Means Clustering
- Principal Component Analysis
- Autoencoders

## Applications

Machine learning is used in many fields:
1. Image recognition
2. Natural language processing
3. Recommendation systems
4. Fraud detection
5. Autonomous vehicles
""".strip()

SAMPLE_CODE = '''
def quicksort(arr):
    """
    Quicksort implementation in Python.
    Time complexity: O(n log n) average, O(n²) worst case.
    """
    if len(arr) <= 1:
        return arr

    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]

    return quicksort(left) + middle + quicksort(right)


def binary_search(arr, target):
    """
    Binary search implementation.
    Requires sorted array.
    Time complexity: O(log n)
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == target:
            return mid
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return -1
'''


def recursive_splitter():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""],
    )
    chunks = splitter.split_text(SAMPLE_TEXT)

    print(f"Original length: {len(SAMPLE_TEXT)} chars")
    print(f"Number of chunks: {len(chunks)}")
    print(f"Chunk sizes: {[len(c) for c in chunks]}")
    print(f"\nFirst chunk preview:\n{chunks[0][:200]}...")



def chunk_size_comparison():
    sizes = [200, 500, 1000]

    print("Chunk size comparison:")
    for size in sizes:
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=size,
            chunk_overlap=size // 5,
            separators=["\n\n", "\n", " ", ""],
        )
        chunks = splitter.split_text(SAMPLE_TEXT)
        print(f"Chunk size: {size}, Number of chunks: {len(chunks)}")



def overlap_importance():
    text = "The quick brown fox jumps over the lazy dog. " * 10

    with_overlap_splitter = RecursiveCharacterTextSplitter(
        chunk_size=50,
        chunk_overlap=20,
        separators=["\n\n", "\n", " ", ""],
    )
    no_overlap_chunks = RecursiveCharacterTextSplitter(
        chunk_size=50,
        chunk_overlap=0,
        separators=["\n\n", "\n", " ", ""],
    )

    chunks_with_overlap = with_overlap_splitter.split_text(text)
    chunks_no_overlap = no_overlap_chunks.split_text(text)

    print(f"Chunks with overlap: {len(chunks_with_overlap)}")
    print(f" Chunk 1 end: ...{chunks_with_overlap[0][-20:]}")
    print(f" Chunk 1 start: {chunks_with_overlap[0][:20]}")


    print(f"Chunks without overlap: {len(chunks_no_overlap)}")
    print(f" Chunk 1 end: ...{chunks_no_overlap[0][-20:]}")
    print(f" Chunk 1 start: {chunks_no_overlap[0][:20]}")   


def markdown_splitter():
    headers_to_split_on = [
        ("#", "h1"),
        ("##", "h2"),
        ("###", "h3")
    ]

    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers_to_split_on
    )
    chunks = splitter.split_text(SAMPLE_TEXT)

    print(f"Original length: {len(SAMPLE_TEXT)} chars")
    print(f"Number of chunks: {len(chunks)}")
    for i, chunk in enumerate(chunks):
        print(f"--- Chunk {i+1} ---\n{chunk.page_content[:200]}...")
        print(f" Metadata: {chunk.metadata}")
        print()


def code_splitter():
    python_splitter = RecursiveCharacterTextSplitter.from_language(language=Language.PYTHON,
                                                                   chunk_size=500,
                                                                   chunk_overlap=50,
                                                                   )
    chunks = python_splitter.split_text(SAMPLE_CODE)
    print(f"\nCode split into {len(chunks)} chunks")
    for i, chunk in enumerate(chunks):
        print(f"\n Chunk {i} ({len(chunk)} chars)")
        print(chunk[:150] + "..." if len(chunk) > 150 else chunk)
    

def document_splitter():
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_core.documents import Document

    loader = PyPDFLoader("./docs/langchain_demo.pdf")

    documents = loader.load()
    print(f"Loaded {len(documents)} documents from PDF")

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", " ", ""]
    )
    split_documents = splitter.split_documents(documents)
    print(f"Split into {len(split_documents)} chunks")
    for i, chunk in enumerate(split_documents):
        content = chunk.page_content
        print(f"\n Chunk {i} ({len(content)} chars)")
        print(content[:150] + "..." if len(content) > 150 else content)

    

if __name__ == "__main__":
    #recursive_splitter()
    #chunk_size_comparison()
    #overlap_importance()
    #markdown_splitter()
    #code_splitter()
    document_splitter()
