import logging
import os
import uuid

from dotenv import load_dotenv
from fastapi import FastAPI
import inngest
import inngest.fast_api
from inngest.experimental import ai

from data_loader import embed_texts, load_and_chunk_pdf
from vector_db import QdrantStorage  # adjust to wherever your class lives
from custom_types import RAGSearchResult, RAGUpSertResult, RAGChunkAndSrc

load_dotenv()

inngest_client = inngest.Inngest(
    app_id="rag_app",
    logger=logging.getLogger("uvicorn"),
    is_production=False,
    serializer=inngest.PydanticSerializer(),
)


@inngest_client.create_function(
    fn_id="RAG: Ingest PDF",
    trigger=inngest.TriggerEvent(event="rag/inngest_pdf"),
)
async def rag_ingest_pdf(ctx: inngest.Context):
    def _load() -> RAGChunkAndSrc:
        pdf_path = ctx.event.data["pdf_path"]
        source_id = ctx.event.data.get("source_id", pdf_path)
        chunks = load_and_chunk_pdf(pdf_path)
        return RAGChunkAndSrc(chunks=chunks, source_id=source_id)

    def _upsert() -> RAGUpSertResult:
        chunks = chunk_and_src.chunks
        source_id = chunk_and_src.source_id
        vectors = embed_texts(chunks)
        ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, f"{source_id}:{i}")) for i in range(len(chunks))]
        payloads = [{"source": source_id, "text": chunks[i]} for i in range(len(chunks))]
        QdrantStorage().upsert(ids, vectors, payloads)
        return RAGUpSertResult(ingested=len(chunks))

    chunk_and_src = await ctx.step.run("load-and-chunk", _load, output_type=RAGChunkAndSrc)
    ingested = await ctx.step.run("embed-and-upsert", _upsert, output_type=RAGUpSertResult)
    return ingested.model_dump()


@inngest_client.create_function(
    fn_id="RAG: Query PDF",
    trigger=inngest.TriggerEvent(event="rag/query_pdf_ai"),
)
async def rag_query_pdf_ai(ctx: inngest.Context):
    question = ctx.event.data["question"]
    top_k = int(ctx.event.data.get("top_k", 5))

    # Fix 1: closure, reads question/top_k from the enclosing scope
    def _search() -> RAGSearchResult:
        query_vector = embed_texts([question])[0]
        search_result = QdrantStorage().search(query_vector, top_k=top_k)
        return RAGSearchResult(
            contexts=search_result["contexts"],
            sources=search_result["sources"],
        )

    found = await ctx.step.run("embed-and-search", _search, output_type=RAGSearchResult)

    context_block = "\n\n".join(f"- {c}" for c in found.contexts)

    # Fix: parentheses so the strings concatenate into one prompt
    user_content = (
        "Answer the question based on the context below. "
        "If the context does not contain the answer, say 'I don't know'.\n\n"
        f"Context:\n{context_block}\n\nQuestion: {question}"
    )

    adapter = ai.openai.Adapter(
        model="openai/gpt-oss-120b",
        auth_key=os.getenv("GROQ_API_KEY"),
        base_url="https://api.groq.com/openai/v1",
    )

    res = await ctx.step.ai.infer(
        "llm-answer",
        adapter=adapter,
        body={
            "max_tokens": 1024,
            "temperature": 0.2,
            "messages": [
                {
                    "role": "system",
                    "content": "You answer questions based on the context provided. If the context does not contain the answer, respond with 'I don't know'.",
                },
                {"role": "user", "content": user_content},
            ],
        },
    )

    answer = res["choices"][0]["message"]["content"].strip()
    return {"answer": answer, "sources": found.sources, "num_contexts": len(found.contexts)}


app = FastAPI()

inngest.fast_api.serve(app, inngest_client, functions=[rag_ingest_pdf, rag_query_pdf_ai])