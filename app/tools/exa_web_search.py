import os
from exa_py import Exa


def get_exa_client() -> Exa:
    api_key = os.getenv("EXA_API_KEY")

    if not api_key:
        raise ValueError("EXA_API_KEY is not set.")

    return Exa(api_key=api_key)

def search_web_exa(query: str, k: int = 5) -> list[dict]:
    exa_client = get_exa_client()

    response = exa_client.search(query, num_results=k, contents={"highlights": True, "text": {"max_characters": 1200}},)
    clean_response = []

    for result in response.results:
        highlights = getattr(result, "highlights", None)
        text = getattr(result, "text", None)
        clean_response.append(
            {
                "title": getattr(result, "title", None),
                "url": getattr(result, "url", None),
                "published_date": getattr(result, "published_date", None),
                "author": getattr(result, "author", None),
                "highlights": highlights,
                "text_preview": text[:1200] if text else None,
            }
        )

    return clean_response