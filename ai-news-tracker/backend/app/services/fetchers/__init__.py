from .arxiv import ArxivFetcher
from .huggingface import HuggingFaceFetcher
from .blogs import BlogFetcher
from .aggregators import AggregatorFetcher

__all__ = ["ArxivFetcher", "HuggingFaceFetcher", "BlogFetcher", "AggregatorFetcher",
           "FETCHER_REGISTRY", "get_fetcher"]

FETCHER_REGISTRY = {
    "arxiv": {"class": ArxivFetcher},
    "huggingface": {"class": HuggingFaceFetcher},
    "blogs": {"class": BlogFetcher},
    "aggregators": {"class": AggregatorFetcher, "settings_kwargs": ["reddit_client_id", "reddit_client_secret"]},
}


def get_fetcher(source: str, **override_kwargs):
    """Return an instantiated fetcher for the given source.

    Args:
        source: Source name (must be a key in FETCHER_REGISTRY).
        **override_kwargs: Override default kwargs for the fetcher constructor.
    """
    entry = FETCHER_REGISTRY.get(source)
    if not entry:
        raise ValueError(f"Unknown source: {source}. Valid sources: {list(FETCHER_REGISTRY.keys())}")

    cls = entry["class"]
    if override_kwargs:
        return cls(**override_kwargs)

    # Pull kwargs from settings if specified
    settings_kwargs = entry.get("settings_kwargs")
    if settings_kwargs:
        from ...config import settings
        kwargs = {k: getattr(settings, k, "") for k in settings_kwargs}
        return cls(**kwargs)

    return cls()
