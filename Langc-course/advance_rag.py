from langchain_classic.retrievers.multi_query import MultiQueryRetriever
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import ParentDocumentRetriever
from langchain_classic.storage import InMemoryStore
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chat_models import init_chat_model
from dotenv import load_dotenv
import logging as log

load_dotenv()

log.basicConfig()
log.basicConfig(level=log.INFO, format="%(name)s - %(message)s")
log.getLogger("langchain_classic.retrievers.multi_query").setLevel(log.INFO)

INFO_BURIED = [
    Document(
        page_content="""ACME AI SOLUTIONS - COMPANY HISTORY AND TECHNOLOGY STACK

Founded in 2018 by three Stanford graduates, ACME AI Solutions began as a
small consulting firm helping enterprises adopt machine learning. Our first
office was a converted garage in Palo Alto, and we had just two laptops and
a dream. The early days were challenging - we survived on instant ramen and
the occasional pizza from the client meetings.

In 2019, we secured our first major contract with a Fortune 500 retailer,
helping them build a recommendation engine. This led to rapid growth and we
moved to a proper office space in San Francisco. By 2020, we had grown to
50 employees and opened offices in Austin and Seattle.

Our current technology stack has evolved significantly over the years. For
backend services, we use Python and FastAPI. Our data pipeline runs on
Apache Spark and Airflow. For frontend, we've standardized on React and
TypeScript.

LangChain is a framework for building LLM applications. It provides tools
for prompts, chains, agents, and memory. LangChain supports multiple LLM
providers including OpenAI, Anthropic, and local models like Llama.

The company culture at ACME emphasizes work-life balance. We offer unlimited
PTO, which most employees use for an average of 25 days per year. Our
engineering teams follow agile methodology with two-week sprints.

Our revenue has grown consistently, from $2M in 2019 to $45M in 2023. We
project $70M for 2024, driven by our new enterprise AI platform. The company
went through Series B funding in 2022, raising $80M at a $500M valuation.

Employee benefits include comprehensive health insurance through Aetna, a
401(k) with 4% matching, and a generous equity package.""",
        metadata={"source": "acme_company_overview.pdf"},
    ),
    Document(
        page_content="""ACME AI PLATFORM - TECHNICAL DOCUMENTATION v2.4

Chapter 1: System Architecture Overview

The ACME AI Platform is built on a microservices architecture deployed on
AWS EKS (Elastic Kubernetes Service). Each microservice is containerized
using Docker and orchestrated by Kubernetes. We use Istio as our service
mesh for traffic management and observability.

Our database layer consists of PostgreSQL for transactional data, Redis
for caching, and Pinecone for vector storage. All databases are deployed
in high-availability configurations with automatic failover.

Chapter 2: Authentication and Authorization

User authentication is handled through Auth0, supporting both SSO via SAML
2.0 and OAuth 2.0 flows. We implement role-based access control (RBAC) with
four default roles: Admin, Developer, Analyst, and Viewer.

Chapter 3: AI Framework Integration

LangGraph is a library for building stateful, multi-actor applications with
LLMs. Key features include state management, cycles and loops, human-in-the-
loop workflows, and persistence. LangGraph extends LangChain for complex
agent architectures.

Chapter 4: Monitoring and Logging

We use DataDog for application performance monitoring (APM) and log
aggregation. All services emit structured JSON logs that are collected and
indexed for searching. Alert thresholds are configured for latency (p99 >
500ms), error rates (> 1%), and resource utilization (CPU > 80%).

Chapter 5: Disaster Recovery

Our disaster recovery plan includes daily database backups stored in S3
with cross-region replication. RTO is 4 hours, and RPO is 1 hour.""",
        metadata={"source": "technical_docs_v2.4.pdf"},
    ),
]
# Sample knowledge base for demos
TECH_DOCS = [
    Document(
        page_content="Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming. Python is widely used in web development, data science, artificial intelligence, and automation.",
        metadata={
            "topic": "programming",
            "language": "python",
            "difficulty": "beginner",
        },
    ),
    Document(
        page_content="JavaScript is the language of the web. It runs in browsers and on servers with Node.js. Modern frameworks like React, Vue, and Angular make building interactive web applications efficient. JavaScript supports asynchronous programming with Promises and async/await.",
        metadata={
            "topic": "programming",
            "language": "javascript",
            "difficulty": "intermediate",
        },
    ),
    Document(
        page_content="Machine learning is a subset of AI that enables systems to learn from data. Supervised learning uses labeled data, while unsupervised learning finds patterns in unlabeled data. Popular ML frameworks include TensorFlow, PyTorch, and scikit-learn.",
        metadata={
            "topic": "ai",
            "subtopic": "machine_learning",
            "difficulty": "advanced",
        },
    ),
    Document(
        page_content="LangChain is a framework for building LLM applications. It provides tools for prompts, chains, agents, and memory. LangChain supports multiple LLM providers including OpenAI, Anthropic, and local models.",
        metadata={
            "topic": "ai",
            "subtopic": "llm_frameworks",
            "difficulty": "intermediate",
        },
    ),
    Document(
        page_content="LangGraph is a library for building stateful, multi-actor applications with LLMs. Key features include state management, cycles and loops, human-in-the-loop workflows, and persistence. LangGraph extends LangChain for complex agent architectures.",
        metadata={
            "topic": "ai",
            "subtopic": "llm_frameworks",
            "difficulty": "advanced",
        },
    ),
    Document(
        page_content="Docker is a platform for containerizing applications. Containers package code and dependencies together for consistent deployment. Docker Compose orchestrates multi-container applications. Kubernetes scales Docker containers in production.",
        metadata={
            "topic": "devops",
            "subtopic": "containers",
            "difficulty": "intermediate",
        },
    ),
    Document(
        page_content="PostgreSQL is an advanced open-source relational database. It supports JSON data types, full-text search, and extensions like pgvector for vector similarity search. PostgreSQL is ACID compliant and highly extensible.",
        metadata={
            "topic": "database",
            "type": "relational",
            "difficulty": "intermediate",
        },
    ),
    Document(
        page_content="Vector databases like Pinecone, Chroma, and Qdrant are optimized for storing and searching embeddings. They enable semantic similarity search for RAG applications. Most support metadata filtering and hybrid search combining keywords with vectors.",
        metadata={"topic": "database", "type": "vector", "difficulty": "intermediate"},
    ),
]

ollama_embeddings = OllamaEmbeddings(model="nomic-embed-text:latest")

gg_embeddings = GoogleGenerativeAIEmbeddings(
    model="gemini-embedding-001"
)
llm = init_chat_model("gemini-3.5-flash-lite",
                    model_provider="google_genai",
                    max_retries=3)

def create_base_vectorstore():
    return Chroma.from_documents(
        documents=TECH_DOCS,
        embedding=gg_embeddings
    )

def demo_multi_query_retriever():
    print("=" * 60)
    print("MULTI-QUERY RETRIEVER DEMO")
    print("Generates multiple perspectives on your question")
    print("=" * 60)

    vectorstore = create_base_vectorstore()

    retriever = MultiQueryRetriever.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(search_kwargs={"k": 4})
    )

    query = "What tools can i use to build AI applications?"

    print(f"Original query: {query}")
    print(f"\nThe retriver will generate multiple query variations")
    print(f"(Check INFO logs above for generated queries)")
    
    docs = retriever.invoke(query)
    print(f"Retrieved {len(docs)} unique documents:")
    for i, doc in enumerate(docs, 1):
        print(f"\n{i+1}. [{doc.metadata.get('topic', 'N/A')}] {doc.page_content[:100]}")


def demo_contextual_compression():
    print("=" * 60)
    print("CONTEXTUAL COMPRESSION DEMO")
    print("Compresses retrieved documents based on context")
    print("=" * 60)

    vectorstore = create_base_vectorstore()

    compressor = LLMChainExtractor.from_llm(llm)

    query = "What tools can i use to build AI applications?"

    print(f"Original query: {query}")
    print(f"\nRetrieving documents for compression demo")

    compressor_retriever = ContextualCompressionRetriever(
        base_retriever=vectorstore.as_retriever(search_kwargs={"k": 4}),
        base_compressor=compressor
    )
    base_docs = vectorstore.as_retriever(search_kwargs={"k": 4}).invoke(query)
    print(f"Retrieved {len(base_docs)} base documents before compression:") 
    for i, doc in enumerate(base_docs, 1):
        print(f"\n{i}. [{doc.metadata.get('topic', 'N/A')}] {doc.page_content[:100]}")
    
    print("=" * 60)
    compressed_docs = compressor_retriever.invoke(query)
    print(f"Retrieved {len(compressed_docs)} compressed documents:")
    for i, doc in enumerate(compressed_docs, 1):
        print(f"\n{i}. [{doc.metadata.get('topic', 'N/A')}] {doc.page_content[:100]}")
    print("=" * 60)

def demo_ensemble_hybrid_search():
    print("=" * 60)
    print("ENSEMBLE HYBRID SEARCH DEMO")
    print("Combines multiple retrieval strategies for better results")
    print("=" * 60)

    vectorstore = create_base_vectorstore()

    bm25_retriever = BM25Retriever.from_documents(TECH_DOCS)
    bm25_retriever.k = 3

    semantic_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm25_retriever, semantic_retriever],
        weights=[0.4, 0.6]  # Assign weights to both retrievers
    )

    query = ["PostgreSQL pgvector",
             "What database stores embeddings?",
             "ACID"]
    for q in query:
        bm25_result = bm25_retriever.invoke(q)
        semantic_result = semantic_retriever.invoke(q)
        ensemble_result = ensemble_retriever.invoke(q)

        print(f"Query: {q}")
        print(f"BM25 retrieved {len(bm25_result)} documents:")
        for i, doc in enumerate(bm25_result, 1):
            print(f"\n{i}. [{doc.metadata.get('topic', 'N/A')}] {doc.page_content[:100]}")

        print(f"\nSemantic retrieved {len(semantic_result)} documents:")
        for i, doc in enumerate(semantic_result, 1):
            print(f"\n{i}. [{doc.metadata.get('topic', 'N/A')}] {doc.page_content[:100]}")

        print(f"\nEnsemble retrieved {len(ensemble_result)} documents:")
        for i, doc in enumerate(ensemble_result, 1):
            print(f"\n{i}. [{doc.metadata.get('topic', 'N/A')}] {doc.page_content[:100]}")  
        print("=" * 60) 
    # End of demo_ensemble_hybrid_search function

def demo_parent_document_retriever():
    long_doc = Document(
        page_content="""
# Complete Guide to Building AI Agents

## Chapter 1: Introduction to AI Agents

AI agents are autonomous systems that can perceive their environment, make decisions, and take actions to achieve goals. Unlike simple chatbots, agents can use tools, maintain state, and execute multi-step plans.

The key components of an AI agent include:
- A language model for reasoning
- Tools for interacting with external systems
- Memory for maintaining context
- A planning mechanism for complex tasks

## Chapter 2: Agent Frameworks

Several frameworks exist for building AI agents:

LangChain provides the foundational abstractions for chains and simple agents. It excels at straightforward tool-calling patterns and integrates with many LLM providers.

LangGraph extends LangChain for complex, stateful agents. It introduces graph-based state management, enabling cycles, human-in-the-loop workflows, and persistent execution.

CrewAI focuses on multi-agent collaboration, allowing teams of specialized agents to work together on complex tasks.

## Chapter 3: Production Considerations

Deploying agents to production requires careful attention to:
- Error handling and fallbacks
- Token usage optimization
- Observability and tracing
- Security and access control
- State persistence and recovery

LangSmith provides observability for LangChain/LangGraph applications, offering tracing, evaluation, and monitoring capabilities.
        """,
        metadata={"source": "ai_agents_guide.md"},
    )
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=800,
        chunk_overlap=100
    )
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=200,
        chunk_overlap=20
    )
    store = InMemoryStore()
    vector_store = Chroma(
        collection_name="parent_child_demo",
        embedding_function=gg_embeddings
    )
    retriever = ParentDocumentRetriever(
        vectorstore=vector_store,
        docstore=store,
        parent_splitter=parent_splitter,
        child_splitter=child_splitter
    )
    retriever.add_documents([long_doc])
    query = "What is LangGraph used for?"
    print("Query:", query)

    child_docs = vector_store.similarity_search(query, k=1)
    print(f"\n--- /Child chunk (what search found) ---")
    print(f"Length of child_docs: {len(child_docs[0].page_content)} chars")
    print(f"Content of child_docs: {child_docs[0].page_content}")

    parent_docs = retriever.invoke(query)
    print(f"\n--- /Parent chunk (what search found) ---")
    print(f"Length of parent_docs: {len(parent_docs[0].page_content)} chars")
    print(f"Content of parent_docs: {parent_docs[0].page_content[:200]}...")

def demo_advanced_rag_chain():
    """Complete demonstration of the advanced RAG chain."""
    print("=== Advanced RAG Chain Demo === ")

    vectorestore = create_base_vectorstore()
    multi_retriever = MultiQueryRetriever.from_llm(
        llm=llm,
        retriever=vectorestore.as_retriever(search_kwargs={"k": 3})
    )

    compressor = LLMChainExtractor.from_llm(llm)
    advanced_retriever = ContextualCompressionRetriever(
        base_retriever=multi_retriever,
        base_compressor=compressor
    )
    prompt = ChatPromptTemplate.from_template(
        """
        Answer the question based on the following context. Be specific and cite which part of the context supports your answer.    
        Context: {context}
        Question: {question}
        Answer:
        """
    )
    def format_docs(docs):
        return "\n\n".join([doc.page_content for doc in docs])

    rag_chain = (
        {"context": advanced_retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )

    question = "How can I store and search embeddings?"
    print("Query:", question)
    answer = rag_chain.invoke(question)
    print("Answer:", answer)
    




if __name__ == "__main__":
    #demo_multi_query_retriever()
    #demo_contextual_compression()
    #demo_ensemble_hybrid_search()
    #demo_parent_document_retriever()
    demo_advanced_rag_chain()
