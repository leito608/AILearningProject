# AILearningProject

This repository is a small learning workspace containing multiple Python-based AI experiments and mini-applications. Each project explores a different practical use case, from agentic chat to resume analysis and image classification.

## Project Overview

### 1. Project 1: AI Agent with LangChain + Groq
Location: `project1/`

A conversational AI assistant built with LangChain and LangGraph. It provides a simple tool-calling workflow where the agent can:

- perform arithmetic calculations
- respond to user greetings
- interact through a command-line interface

This project demonstrates how to connect a local Python app to an OpenAI-compatible API, using Groq as the LLM provider.

### 2. Project 2: AI Resume Critiquer
Location: `project2/`

A Streamlit app that allows a user to upload a resume in PDF or TXT format and receive AI-based feedback. The app:

- extracts text from uploaded resumes
- prompts a model to review the resume like a recruiter and ATS reviewer
- gives structured analysis and rewriting suggestions

This is designed as a resume improvement tool for job-seeking and hiring insight.

### 3. Project 3: AI Image Classifier
Location: `project3/`

A Streamlit app that classifies uploaded images using a pre-trained MobileNetV2 model from TensorFlow/Keras. It:

- lets the user upload an image
- preprocesses the image for classification
- displays the top predictions with confidence scores

This project is a beginner-friendly introduction to image recognition and computer vision.

### 4. Project 4: RAG PDF Ingestion and Question Answering
Location: `RAG/`

A local document Q&A system that ingests PDF files, stores embeddings in Qdrant, and answers user questions through a Streamlit UI. The app includes:

- PDF upload and local storage
- text chunking and embedding generation
- semantic retrieval from a vector database
- AI-powered answer generation using LLMs
- asynchronous event-driven background processing with Inngest
- FastAPI backend and Streamlit frontend for a complete RAG workflow

This project demonstrates a practical production-style retrieval-augmented generation pipeline for document-based knowledge retrieval.

### 5. Project 5: Spring AI PDF Ingestion
Location: `RAGSpringAI/`

A Spring Boot application that reads a bundled PDF, splits it into documents, and stores them in a PostgreSQL/pgvector vector store. It uses Ollama for chat and embedding models.

## Tech Stack

- Python
- uv for dependency management
- LangChain and LangGraph
- OpenAI-compatible Groq API
- Gemini API for embeddings
- Streamlit
- FastAPI
- Inngest
- Qdrant vector database
- PyPDF2 / PDF parsing
- OpenCV
- TensorFlow / Keras
- Python dotenv
- Docker
- Java 17
- Spring Boot and Spring AI
- Ollama
- PostgreSQL with pgvector

## Repository Structure

```text
AILearningProject/
├── README.md
├── RAGSpringAI/
│   ├── compose.yaml
│   ├── pom.xml
│   └── src/
├── project1/
│   ├── main.py
│   ├── pyproject.toml
│   └── README.md
├── project2/
│   ├── main.py
│   ├── pyproject.toml
│   └── README.md
├── project3/
│   ├── main.py
│   ├── pyproject.toml
│   └── README.md
├── RAG/
│   ├── main.py
│   ├── streamlit_app.py
│   ├── data_loader.py
│   ├── vector_db.py
│   ├── custom_types.py
│   ├── pyproject.toml
│   ├── README.md
│   └── uploads/
└── .gitignore
```

## Prerequisites

- Python 3.12+ (Project 3 requires Python 3.12, while the others use Python 3.14 in their configuration)
- uv installed on your machine
- A Groq API key for projects that connect to the Groq API
- Java 17+ and Docker for `RAGSpringAI`
- Ollama installed and running at `http://localhost:11434` for `RAGSpringAI`

## Environment Setup

Create a `.env` file in the relevant project folder and add your API key:

```env
GROQ_API_KEY=your_api_key_here
```

## Running the Projects

### Project 1

```bash
cd project1
uv sync
uv run python main.py
```

### Project 2

```bash
cd project2
uv sync
uv run streamlit run main.py
```

### Project 3

```bash
cd project3
uv sync
uv run streamlit run main.py
```

### Project 4: RAG PDF Assistant

```bash
cd RAG
uv sync
# Start Qdrant in Docker
# Start the FastAPI app
uv run uvicorn main:app --reload
# Start Inngest dev server
npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
# Start the Streamlit UI
uv run streamlit run streamlit_app.py
```

### Project 5: Spring AI PDF Ingestion

Start the pgvector database from the repository root:

```bash
docker compose -f RAGSpringAI/compose.yaml up -d
```

Make sure Ollama is running and the configured models are available:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Run the Spring Boot application:

```bash
cd RAGSpringAI
./mvnw spring-boot:run
```

On startup, the application ingests `src/main/resources/pdf/spring-boot-reference.pdf` and stores its document chunks in pgvector. The database is published on `localhost:5432`; that port must be available.

## Notes

This workspace is intended for learning and experimentation. The projects are intentionally simple and modular so they can be expanded further into production-ready AI tools.

## License

This project is for educational and learning purposes.
