from contextlib import asynccontextmanager
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from sentence_transformers import SentenceTransformer

from data import documents

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
COLLECTION_NAME = "programming_concepts"
DATABASE_PATH = Path(__file__).parent / "qdrant_data"


class Document(BaseModel):
    text: str = Field(min_length=1)
    category: str = Field(min_length=1)


class IndexRequest(BaseModel):
    documents: list[Document] = Field(min_length=1, max_length=500)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    top_k: int = Field(default=3, ge=1, le=50)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.model = SentenceTransformer(MODEL_NAME)
    app.state.client = QdrantClient(path=str(DATABASE_PATH))
    try:
        yield
    finally:
        app.state.client.close()


app = FastAPI(
    title="Semantic Search & Vector Database",
    description="Pencarian konsep pemrograman menggunakan embedding dan Qdrant.",
    lifespan=lifespan,
)


def get_model(request: Request) -> SentenceTransformer:
    model = getattr(request.app.state, "model", None)
    if model is None:
        raise HTTPException(status_code=503, detail="Embedding model belum siap.")
    return model


def get_client(request: Request) -> QdrantClient:
    client = getattr(request.app.state, "client", None)
    if client is None:
        raise HTTPException(status_code=503, detail="Qdrant belum siap.")
    return client


@app.get("/health")
def health(request: Request) -> dict[str, str]:
    return {
        "status": "OK",
        "model": "ready" if getattr(request.app.state, "model", None) else "not ready",
    }


@app.post("/index")
def index_dataset(
    request: Request,
    body: IndexRequest | None = None,
) -> dict[str, int | str]:
    model = get_model(request)
    client = get_client(request)
    items = body.documents if body is not None else [Document(**item) for item in documents]
    vectors = model.encode(
        [item.text for item in items],
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    vector_size = len(vectors[0])

    if client.collection_exists(COLLECTION_NAME):
        client.delete_collection(COLLECTION_NAME)
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
    )

    points = [
        PointStruct(
            id=str(uuid5(NAMESPACE_URL, f"{index}:{item.text}:{item.category}")),
            vector=vector.tolist(),
            payload={"text": item.text, "category": item.category},
        )
        for index, (item, vector) in enumerate(zip(items, vectors, strict=True))
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points, wait=True)
    return {"status": "indexed", "count": len(points), "collection": COLLECTION_NAME}


@app.post("/search")
def semantic_search(request: Request, body: SearchRequest) -> dict[str, object]:
    model = get_model(request)
    client = get_client(request)
    if not client.collection_exists(COLLECTION_NAME):
        raise HTTPException(status_code=409, detail="Dataset belum di-index. Jalankan POST /index.")

    query_vector = model.encode(
        body.query,
        normalize_embeddings=True,
        show_progress_bar=False,
    )
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector.tolist(),
        limit=body.top_k,
        with_payload=True,
    )
    results = [
        {
            "text": point.payload["text"],
            "category": point.payload["category"],
            "score": round(point.score, 4),
        }
        for point in response.points
        if point.payload is not None
    ]
    return {"query": body.query, "results": results}
