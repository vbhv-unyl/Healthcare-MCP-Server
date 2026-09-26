from mcp.server.fastmcp import Context, FastMCP

from settings import build_retrieval_dependencies

mcp = FastMCP("medical-report-retrieval", host="0.0.0.0", port=8899, stateless_http=True)

_embedder, _vector_store = build_retrieval_dependencies()

@mcp.tool()
def search_report_chunks(ctx: Context, query: str, top_k: int = 5) -> list[dict]:
    """
    Searches the user's ingested medical reports for passages relevant
    to the query. Returns the most relevant chunks with their source
    section and page numbers, so an answer built from them can cite
    where it came from.
    """
    user_id = ctx.request_context.request.headers.get("x-user-id") if ctx.request_context.request else None
    if not user_id:
        raise ValueError("x-user-id header is required -- the client must set it from the logged-in session")

    vectors = _embedder.embed([query])
    results = _vector_store.query(query_vector=vectors[0], user_id=user_id, top_k=top_k)
    return [
        {
            "text": r.text,
            "section": r.section,
            "page_start": r.page_start,
            "page_end": r.page_end,
            "source_type": r.source_type,
            "score": r.score,
        }
        for r in results
    ]

if __name__ == "__main__":
    mcp.run(transport="streamable-http")