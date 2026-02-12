from typing import List, Dict

import httpx


def search_huggingface(query: str, max_results: int = 5) -> List[Dict]:
    """Search HuggingFace Hub for models."""
    try:
        resp = httpx.get(
            "https://huggingface.co/api/models",
            params={
                "search": query,
                "sort": "downloads",
                "direction": "-1",
                "limit": max_results,
            },
            timeout=15,
        )
        resp.raise_for_status()
        models = resp.json()
        results = []
        for model in models[:max_results]:
            model_id = model.get("modelId", model.get("id", ""))
            results.append({
                "model_id": model_id,
                "author": model_id.split("/")[0] if "/" in model_id else "",
                "downloads": model.get("downloads", 0),
                "likes": model.get("likes", 0),
                "tags": model.get("tags", [])[:5],
                "url": f"https://huggingface.co/{model_id}",
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]
