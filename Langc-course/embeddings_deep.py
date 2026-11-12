from dotenv import load_dotenv
from httpx2 import query
import numpy as np

load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings

embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

def basic_embedding():
    text = "What is machine learning?"
    single_embedding = embeddings.embed_query(text)
    print(f"Vector dimenension: {len(single_embedding)}")
    print(f"First 5 values: {single_embedding[:5]}")
    print(f"Vector norm: {np.linalg.norm(single_embedding):.4f}")


def batch_embedding():
    texts = ["What is machine learning?", 
             "Explain deep learning.", 
             "Define artificial intelligence."
             ]
    batch_embeddings = embeddings.embed_documents(texts)
    for i, emb in enumerate(batch_embeddings):
        print(f"Text: {texts[i]}")
        print(f"Vector dimenension: {len(emb)}")
        print(f"First 5 values: {emb[:5]}")
        print(f"Vector norm: {np.linalg.norm(emb):.4f}")
        print() 

def similarity():
    docs = [
        "Python is a programming language.",
        "JavaScript is used for web development.",
        "Machine learning is a subset of artificial intelligence.",
        "Deep leaning is uses neural networks to model complex patterns.",
        "Cat are popular pets."
    ]

    doc_embeddings = embeddings.embed_documents(docs)
    query_text = "What is programming language?"

    query_embedding = embeddings.embed_query(query_text)
   
    def cosine_similarity(vec1, vec2):
        return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

    similarities = [cosine_similarity(query_embedding, doc_emb) for doc_emb in doc_embeddings]

    ranked_docs = sorted(zip(docs, similarities), key=lambda x: x[1], reverse=True)
    print(f"Query: {query_text}")
    print("Ranked documents by similarity:")
    for doc, score in ranked_docs:
        print(f" {score:.4f} : {doc}")
    print()


#Caching embeddings to avoid redundant API calls
def embbed_caching():
    from langchain_classic.embeddings import CacheBackedEmbeddings
    from langchain_classic.storage import LocalFileStore
    import tempfile

    with tempfile.TemporaryDirectory() as tmpdir:
        file_store = LocalFileStore(tmpdir)
        cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
            embeddings, file_store, namespace="excercise", query_embedding_cache=True,
            key_encoder="sha256",
        )
        # Example usage of cached embeddings
        text = "What is Reinforcement learning?"
        first_call = cached_embeddings.embed_query(text)
        print(f"First call vector dimenension: {len(first_call)}")
        print(f"First 5 values: {first_call[:5]}")
        print(f"Vector norm: {np.linalg.norm(first_call):.4f}")

        second_call = cached_embeddings.embed_query(text)
        print(f"Second call vector dimenension: {len(second_call)}")
        print(f"First 5 values: {second_call[:5]}")
        print(f"Vector norm: {np.linalg.norm(second_call):.4f}")

        print(f"\nSame embedding returned: {np.allclose(first_call, second_call)}")

if __name__ == "__main__":
    #basic_embedding()
    #batch_embedding()
    #similarity()
    embbed_caching() 

