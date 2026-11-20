
import uuid
import chromadb

from app.services.privacy_engine import PrivacyEngine


class RAGService:

    def __init__(
        self,
        db_path="data/chroma_db",
        collection_name="datarakshak_documents",
        chunk_size=500,
        chunk_overlap=100
    ):
        if chunk_size <= 0 or not 0 <= chunk_overlap < chunk_size:
            raise ValueError("Invalid chunk size or overlap")

        self.client = chromadb.PersistentClient(path=db_path)

        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"description": "PII-protected document chunks"}
        )

        self.privacy_engine = PrivacyEngine()
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def split_into_chunks(self, text):
        if not text.strip():
            return []

        chunks = []
        start = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk = text[start:end].strip()

            if chunk:
                chunks.append(chunk)

            if end == len(text):
                break

            start = end - self.chunk_overlap

        return chunks

    def ingest_document(self, text, document_id=None):
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Document text cannot be empty")

        result = self.privacy_engine.process(
            text=text,
            action="redact"
        )

        protected_text = result["text"]
        chunks = self.split_into_chunks(protected_text)

        if not chunks:
            raise ValueError("No document chunks generated")

        doc_id = document_id or str(uuid.uuid4())

        existing = self.collection.get(
            where={"document_id": doc_id}
        )

        if existing["ids"]:
            self.collection.delete(ids=existing["ids"])

        chunk_ids = [
            f"{doc_id}_{index}"
            for index in range(len(chunks))
        ]

        metadata = [
            {
                "document_id": doc_id,
                "chunk_index": index,
                "pii_detected": len(result["detections"]) > 0
            }
            for index in range(len(chunks))
        ]

        self.collection.add(
            ids=chunk_ids,
            documents=chunks,
            metadatas=metadata
        )

        return {
            "document_id": doc_id,
            "chunks_stored": len(chunks),
            "pii_detected": len(result["detections"]) > 0,
            "detection_count": len(result["detections"]),
            "storage_status": "protected_and_stored"
        }

    def search_documents(self, query, top_k=3):
        if not isinstance(query, str) or not query.strip():
            raise ValueError("Search query cannot be empty")

        if not isinstance(top_k, int) or not 1 <= top_k <= 10:
            raise ValueError("top_k must be between 1 and 10")

        result = self.privacy_engine.process(
            text=query,
            action="redact"
        )

        protected_query = result["text"]

        if self.collection.count() == 0:
            return {
                "query_protected": protected_query,
                "query_pii_detected": len(result["detections"]) > 0,
                "results": [],
                "message": "No documents ingested yet"
            }

        retrieved = self.collection.query(
            query_texts=[protected_query],
            n_results=min(top_k, self.collection.count()),
            include=["documents", "metadatas", "distances"]
        )

        results = []

        for document, metadata, distance in zip(
            retrieved["documents"][0],
            retrieved["metadatas"][0],
            retrieved["distances"][0]
        ):
            results.append({
                "text": document,
                "document_id": metadata["document_id"],
                "chunk_index": metadata["chunk_index"],
                "distance": distance
            })

        return {
            "query_protected": protected_query,
            "query_pii_detected": len(result["detections"]) > 0,
            "results": results
        }
