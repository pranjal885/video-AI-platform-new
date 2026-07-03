import chromadb
from sentence_transformers import SentenceTransformer

print("Loading Embedding Model...")

embedding_model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)

print("Embedding Model Loaded!")

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="video_transcripts"
)


def split_text(
    text,
    chunk_size=400,
    overlap=100
):

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunks.append(
            text[start:end]
        )

        start += chunk_size - overlap

    return chunks


def store_transcript(
    transcript,
    source="uploaded_video"
):

    try:

        existing = collection.get()

        if existing["ids"]:

            collection.delete(
                ids=existing["ids"]
            )

    except Exception:
        pass

    chunks = split_text(transcript)

    embeddings = embedding_model.encode(
        chunks
    ).tolist()

    ids = [
        str(i)
        for i in range(len(chunks))
    ]

    metadatas = []

    for _ in chunks:

        metadatas.append(
            {
                "source": source
            }
        )

    collection.add(

        ids=ids,

        documents=chunks,

        embeddings=embeddings,

        metadatas=metadatas

    )

    print(f"Stored {len(chunks)} chunks.")


def search_transcript(
    question,
    top_k=3
):

    question_embedding = embedding_model.encode(
        question
    ).tolist()

    results = collection.query(

        query_embeddings=[
            question_embedding
        ],

        n_results=top_k

    )

    return "\n".join(
        results["documents"][0]
    )