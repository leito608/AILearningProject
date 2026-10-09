# PDF RAG

A local retrieval-augmented generation app that ingests PDFs, stores their
embeddings in Qdrant, and answers questions through a Streamlit interface.

## Requirements

- Python 3.12 or later
- [uv](https://docs.astral.sh/uv/)
- Docker
- Node.js and npm (for the Inngest development CLI via `npx`)
- Gemini API key for embeddings and Groq API key for answer generation

## Setup

Run these commands from the `RAG` directory:

```bash
uv sync
```

Create a `.env` file in this directory and add your API keys:

```dotenv
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
```

Start Qdrant in Docker. Its data is persisted in a Docker volume:

```bash
docker pull qdrant/qdrant
docker run -d --name qdrantRagDb \
  -p 6333:6333 \
  -v qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

If the container already exists but is stopped, start it with:

```bash
docker start qdrantRagDb
```

## Run

Open separate terminals in the `RAG` directory and start each service:

1. Start the FastAPI app:

   ```bash
   uv run uvicorn main:app --reload
   ```

2. Start the Inngest development server and point it at FastAPI:

   ```bash
   npx inngest-cli@latest dev -u http://127.0.0.1:8000/api/inngest --no-discovery
   ```

3. Start the Streamlit UI:

   ```bash
   uv run streamlit run streamlit_app.py
   ```

Open the local URL printed by Streamlit (typically `http://localhost:8501`).
Upload a PDF to trigger ingestion, then ask questions about the ingested
documents. The Inngest development dashboard is typically available at
`http://localhost:8288`.

## Stop

Stop each foreground service with `Ctrl+C`. To stop Qdrant while keeping its
data, run:

```bash
docker stop qdrantRagDb
```
