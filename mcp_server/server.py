from mcp.server.fastmcp import FastMCP

from app.tools.consortium import search_consortium
from app.tools.registry import consortium_installment_simulation
from app.rag.retriever import search_documents, format_search_results

mcp = FastMCP(
    name="banking-consortium-mcp",
    host="0.0.0.0",
    port=8001,
)

@mcp.tool()
def health_check() -> str:
    """Check if the MCP server is running."""
    return "MCP server is running."

@mcp.tool()
def search_consortium_products(consortium_type: str | None = None) -> list[dict]:
    """
    Search active consortium products from the internal PostgreSQL database.

    consortium_type can be:
    - automobile
    - motorcycle
    - real estate
    - services

    Use None to return all active consortium products.
    """
    return search_consortium(consortium_type)


@mcp.tool()
def simulate_consortium_payment(
    credit_amount: float,
    term_months: int,
    admin_fee_percentage: float,
    reserve_fund_percentage: float,
) -> dict:
    """
    Simulate the estimated monthly payment for a consortium.
    """
    return consortium_installment_simulation.invoke(
        {
            "credit_amount": credit_amount,
            "term_months": term_months,
            "admin_fee_percentage": admin_fee_percentage,
            "reserve_fund_percentage": reserve_fund_percentage,
        }
    )


@mcp.tool()
def search_consortium_documents(query: str, k: int = 4) -> str:
    """
    Search internal consortium manuals, policies, FAQs, and document chunks.
    """
    results = search_documents(query=query, k=k)
    return format_search_results(results)

if __name__ == "__main__":
    print("Starting MCP server on 0.0.0.0:8001...", flush=True)
    mcp.run(transport="sse")