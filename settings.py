import os
from dotenv import load_dotenv

load_dotenv()

from domain.ports import EmbeddingPort, VectorStorePort
from infrastructure.azure_ai_search_vector_store import AzureAISearchVectorStore
from infrastructure.azure_openai_embedder import AzureOpenAIEmbedder


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set")
    return value


def build_retrieval_dependencies() -> tuple[EmbeddingPort, VectorStorePort]:
    embedder = AzureOpenAIEmbedder(
        endpoint=_require_env("AZURE_OPENAI_ENDPOINT"),
        api_key=_require_env("AZURE_OPENAI_KEY"),
        deployment_name=_require_env("AZURE_OPENAI_EMBEDDING_DEPLOYMENT"),
        api_version=_require_env("AZURE_OPENAI_API_VERSION"),
    )
    vector_store = AzureAISearchVectorStore(
        endpoint=_require_env("AZURE_SEARCH_ENDPOINT"),
        api_key=_require_env("AZURE_SEARCH_KEY"),
        index_name=_require_env("AZURE_SEARCH_INDEX_NAME"),
    )
    return embedder, vector_store