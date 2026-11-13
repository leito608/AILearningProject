from dotenv import load_dotenv

load_dotenv()

from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough, RunnableParallel
from langchain_core.output_parsers import StrOutputParser
from langchain.chat_models import init_chat_model
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pydantic import BaseModel, Field
from typing import List, Optional
import tempfile

ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")


gg_embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)

llm = init_chat_model("gemini-3.5-flash-lite",
                    model_provider="google_genai",
                    max_retries=3)
# Sample knowledge base
KNOWLEDGE_BASE = """# LangChain Framework

LangChain is a framework for developing applications powered by language models. It was created by Harrison Chase in October 2022.

## Core Components

1. **Models**: LangChain supports various LLM providers including OpenAI, Anthropic, and local models.

2. **Prompts**: Templates for structuring inputs to language models.

3. **Chains**: Sequences of calls to models and other components.

4. **Agents**: Systems that use LLMs to determine which actions to take.

5. **Memory**: Components for persisting state between chain/agent calls.

## LangGraph

LangGraph is a library for building stateful, multi-actor applications. Key features:
- State management
- Cycles and loops
- Human-in-the-loop
- Persistence

## Pricing

LangChain itself is open source and free. LangSmith (the observability platform) has a free tier and paid plans starting at $39/month.

## Getting Started

Install with: pip install langchain langchain-openai
Create your first chain in under 10 lines of code.
"""
def create_kb():
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    doc = Document(
        page_content=KNOWLEDGE_BASE,
        metadata={"source": "langchain_kb.md"}
    )
    
    chunks = splitter.split_documents([doc])

    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=ollama_embeddings,
        persist_directory=tempfile.mkdtemp()
    )
    return vectorstore

def demo_basic_rag():
    vectorstore = create_kb()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2}, search_type="similarity")


    #RAG prmpt template
    prompt = ChatPromptTemplate.from_template(
        "Use the following context to answer the question:\n\n{context}\n\nQuestion: {question}\nAnswer: " \
        "make sure to use the context provided. If the context does not contain the answer, respond with 'I don't know.'"
    )

    #format retrieved documents into context
    def format_doc(retrieved_docs: List[Document]) -> str:
        return "\n\n".join([doc.page_content for doc in retrieved_docs])

    rag_chain = (
        {"context": retriever | format_doc, 
         "question": RunnablePassthrough()} 
         | prompt
         | llm
         | StrOutputParser()
    )

    question = [
        "What is LangChain?",
        "Who created LangChain?",
        "What is LangGraph used for?",
        "What is a leopard?"
    ]

    print(f"Begin RAG demo")
    for q in question:
        answer = rag_chain.invoke(q)
        print(f"Q: {q}\nA: {answer}\n")

    print(f"End RAG demo")


def demo_rag_with_sources():
    vectorstore = create_kb()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2}, search_type="similarity")

    prompt = ChatPromptTemplate.from_template(
        "Use the following context to answer the question:\n\n{context}\n\n" \
        "Question: {question}\n" \
        "Answer: make sure to use the context provided. If the context does not contain the answer, respond with 'I don't know.' " \
        "Answer with sources if available."
    )

    def format_doc_with_sources(retrieved_docs: List[Document]) -> str:
        return "\n\n".join([f"{doc.page_content}\nSource: {doc.metadata.get('source', 'unknown')}" for doc in retrieved_docs])

    rag_chain = (
        {"context": retriever | format_doc_with_sources, 
         "question": RunnablePassthrough()} 
         | prompt
         | llm
         | StrOutputParser()
    )

    question = [
        "What is LangChain?",
        "Who created LangChain?",
        "What is LangGraph used for?",
        "What is a leopard?"
    ]

    print(f"Begin RAG with sources demo")
    for q in question:
        answer = rag_chain.invoke(q)
        print(f"Q: {q}\nA: {answer}\n")

    print(f"End RAG with sources demo")

def demo_rag_with_fallback():
    vectorstore = create_kb()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2}, search_type="similarity")

    prompt = ChatPromptTemplate.from_template(
        "Use the following context to answer the question:\n\n{context}\n\n" \
        "Question: {question}\n" \
        "Answer: make sure to use the context provided. " \
        "If no context is found, provide a fallback response."
    )

    def format_doc_with_fallback(retrieved_docs: List[Document]) -> str:
        if not retrieved_docs:
            return "No context found."
        return "\n\n".join([f"{doc.page_content}\nSource: {doc.metadata.get('source', 'unknown')}" for doc in retrieved_docs])

    rag_chain = (
        {"context": retriever | format_doc_with_fallback, 
         "question": RunnablePassthrough()} 
         | prompt
         | llm
         | StrOutputParser()
    )

    question = [
        "What is LangChain?",
        "Who created LangChain?",
        "What is LangGraph used for?",
        "What is a leopard?"
    ]

    print(f"Begin RAG with fallback demo")
    for q in question:
        answer = rag_chain.invoke(q)
        print(f"Q: {q}\nA: {answer}\n")

    print(f"End RAG with fallback demo")

def demo_structured_rag():
    vectorstore = create_kb()
    retriever = vectorstore.as_retriever(search_kwargs={"k": 2}, search_type="similarity")

    class RAGResponse(BaseModel):
        answer: str = Field(..., description="The answer to the question based on the retrieved context")
        confidence: str = Field(..., description="High, Medium, or Low confidence in the answer")
        sources_used: List[str] = Field(..., description="List of sources used to generate the answer")
        followup: str = Field(..., description="Suggested follow-up question based on the retrieved context")

    structured_llm = llm.with_structured_output(RAGResponse)

    prompt = ChatPromptTemplate.from_template(
        "Use the following context to answer the question:\n\n{context}\n\n" \
        "Question: {question}\n" \
        "Answer: make sure to use the context provided. " \
        "If no context is found, provide a fallback response."
    )

    def format_doc_with_structured_rag(retrieved_docs: List[Document]) -> str:
        if not retrieved_docs:
            return "No context found."
        return "\n\n".join([f"{doc.page_content}\nSource: {doc.metadata.get('source', 'unknown')}" for doc in retrieved_docs])

    rag_chain = (
        {"context": retriever | format_doc_with_structured_rag, 
         "question": RunnablePassthrough()} 
         | prompt
         | structured_llm
    )

    question = [
        "What is LangChain?",
        "Who created LangChain?",
        "What is LangGraph used for?",
        "What is a leopard?"
    ]

    print(f"Begin structured RAG demo")
    for q in question:
        answer = rag_chain.invoke(q)
        print(f"Q: {q}\nA: {answer.answer}\n")
        print(f"Confidence: {answer.confidence}\nSources Used: {answer.sources_used}\nFollow-up: {answer.followup}\n")

    print(f"End structured RAG demo")

def excercise_document_qa():
    """
    Excercise: Build a complete document Q&A system that:
    1. Takes a text document as input.
    2. Splits and embeds it
    3. Allows multiple questions
    4, Return answer with confidence scores
    """
    class DocumentQA:
        def __init__(self, document: str, source_name: str = "document"):
            splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
            doc = Document(page_content=document, metadata={"source": source_name})
            chunks = splitter.split_documents([doc])
            self.vectorstore = Chroma.from_documents(chunks, embedding=gg_embeddings)
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 2}, search_type="similarity")
            self.llm = init_chat_model("gemini-3.5-flash-lite",
                    model_provider="google_genai",
                    max_retries=3)
            self.prompt = ChatPromptTemplate.from_template(
                "Use the following context to answer the question:\n\n{context}\n\n" \
                "Question: {question}\n" \
                "Answer: make sure to use the context provided. " \
                "If no context is found, provide a fallback response."
            )
            def format_doc(docs):
                return "\n".join(d.page_content for d in docs)
            self.chain = (
                {"context": self.retriever | format_doc, 
                 "question": RunnablePassthrough()} 
                 | self.prompt
                 | self.llm
                 | StrOutputParser()
            )
        
        def ask(self, question: str) -> str:
            return self.chain.invoke(question)


    document = """
    LangChain is a framework for developing applications powered by language models.
    It was created by Harrison Chase.
    LangGraph is used for building and managing graphs of language model calls.
    """
    qa_system = DocumentQA(document, source_name="Langchain_doc")
    questions = [
        "What is LangChain?",
        "Who created LangChain?",
        "What is LangGraph used for?",
        "What is a leopard?"
    ]
    for q in questions:
        answer = qa_system.ask(q)
        print(f"Q: {q}\nA: {answer}\n")

if __name__ == "__main__":
    #demo_basic_rag()
    #demo_rag_with_sources()
    #demo_rag_with_fallback()
    #demo_structured_rag()
    excercise_document_qa()
