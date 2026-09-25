from typing import Protocol

class EmbeddingPort(Protocol):
    def embed(self, texts: list[str]) -> list[list[float]]: ...

class VectorStorePort(Protocol):
    def query(self, query_vector: list[float], user_id: str, top_k: int) -> dict: ...