from mcp.server.fastmcp import FastMCP

from app.tools.consortium import search_consortium
from app.tools.registry import consortium_installment_simulation
from app.rag.pgvector_store import search_documents_pgvector, format_search_results_pgvector
from app.tools.exa_web_search import search_web_exa

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
    Search internal consortium documents, manuals, FAQs, and policies.

    Use this tool for questions about:
    - how consortiums work
    - contemplation rules
    - bid offers
    - cancellation
    - missed payments
    - default/inadimplência
    - risks
    - suitability guidelines
    - policy explanations
    - required documents after contemplation

    Do not use this tool for exact product options, fees, terms,
    minimum income, or credit ranges. For product data, use the
    PostgreSQL consortium database tool.
    """
    results = search_documents_pgvector(query=query, k=k)
    return format_search_results_pgvector(results)

@mcp.tool()
def search_public_web(query: str, k: int = 4) -> list[dict]:
    """
    Search the internet using Exa API.

    Use this only for external, public, current, or non-bank-internal information.
    Do not use this for internal consortium product names, fees, terms, or credit ranges.
    Internal product information must come from the PostgreSQL consortium tools.

    Examples of when to use this tool:
    - Current value of government specific rates, such as Selic, IPCA, CDI, etc.
    - Current value of the dollar, euro, or other currencies.
    - Current value of the stock market, such as Ibovespa, Nasdaq, S&P 500, etc.
    - Current news or events that may affect consortiums or financial markets. 
    """
    return search_web_exa(query=query, k=k)

if __name__ == "__main__":
    print("Starting MCP server on 0.0.0.0:8001...", flush=True)
    mcp.run(transport="streamable-http")