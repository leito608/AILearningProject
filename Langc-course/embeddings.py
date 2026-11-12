from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings

from langchain_ollama import OllamaEmbeddings
#nomic-embed-text:latest 

ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")


embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

#single text
text = "Hello, world!"
# embedding = embeddings.embed_query(text)
# #print(f"Embedding: {embedding}")

# print(len(embedding))

# embeds = embeddings.embed_documents(
#     ["Hello, world!", "How are you?", "Goodbye!"]
# )


# print(len(embeds))

embedding = ollama_embeddings.embed_query(text)
print(f"Embedding: {embedding}")

print(len(embedding))