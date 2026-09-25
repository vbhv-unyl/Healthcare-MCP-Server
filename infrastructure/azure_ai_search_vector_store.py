from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizedQuery

from domain.models import RetrievedChunk

_VECTOR_FIELD = "content_vector"

def _escape_odata_string(value: str) -> str:
    """OData string literals escape a single quote by doubling it -- same idea as SQL parameterization."""
    return value.replace("'", "''")


class AzureAISearchVectorStore:
    """Implements VectorStorePort."""

    def __init__(self, endpoint: str, api_key: str, index_name: str):
        credential = AzureKeyCredential(api_key)
        self._client = SearchClient(endpoint=endpoint, index_name=index_name, credential=credential)

    def query(self, query_vector: list[float], user_id: str, top_k: int = 5) -> list[RetrievedChunk]:
        vector_query = VectorizedQuery(vector=query_vector, k_nearest_neighbors=top_k, fields=_VECTOR_FIELD)
        filter_expr = f"user_id eq '{_escape_odata_string(user_id)}'"

        results = self._client.search(
            search_text=None,
            vector_queries=[vector_query],
            filter=filter_expr,
            top=top_k,
            select=["content", "section", "page_start", "page_end", "low_confidence", "source_type"],
        )

        return [
            RetrievedChunk(
                text=r["content"],
                section=r["section"],
                page_start=r["page_start"],
                page_end=r["page_end"],
                low_confidence=r["low_confidence"],
                source_type=r["source_type"],
                score=r["@search.score"],
            )
            for r in results
        ]