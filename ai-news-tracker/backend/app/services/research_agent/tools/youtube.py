import logging
from typing import List, Dict

from ....config import settings

logger = logging.getLogger(__name__)

try:
    from googleapiclient.discovery import build
    YOUTUBE_AVAILABLE = True
except ImportError as e:
    logger.warning("YouTube API not available: %s", e)
    YOUTUBE_AVAILABLE = False


def search_youtube(query: str, max_results: int = 5) -> List[Dict]:
    """Search YouTube for relevant videos."""
    if not YOUTUBE_AVAILABLE:
        return [{"error": "google-api-python-client not installed"}]
    if not settings.youtube_api_key:
        return [{"error": "YouTube API key not configured"}]
    try:
        youtube = build('youtube', 'v3', developerKey=settings.youtube_api_key)
        request = youtube.search().list(
            q=query,
            part='snippet',
            type='video',
            maxResults=max_results,
            relevanceLanguage='en'
        )
        response = request.execute()

        results = []
        for item in response.get('items', []):
            snippet = item['snippet']
            video_id = item['id']['videoId']
            results.append({
                "title": snippet['title'],
                "channel": snippet['channelTitle'],
                "description": snippet['description'][:200] if snippet['description'] else "",
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail_url": snippet['thumbnails']['medium']['url'],
                "published_at": snippet['publishedAt'],
            })
        return results
    except Exception as e:
        return [{"error": str(e)}]
