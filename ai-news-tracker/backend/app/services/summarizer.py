import logging

from groq import AsyncGroq
from typing import Optional
from ..config import settings

logger = logging.getLogger(__name__)


class SummarizerService:
    def __init__(self):
        self._client = None
        self._initialized = False

    @property
    def client(self):
        """Lazy initialization of Groq client."""
        if not self._initialized:
            if settings.groq_api_key:
                self._client = AsyncGroq(api_key=settings.groq_api_key)
            else:
                logger.warning("GROQ_API_KEY not configured - summarization disabled")
            self._initialized = True
        return self._client

    async def summarize(
        self,
        title: str,
        abstract: str,
        content: Optional[str] = None
    ) -> Optional[str]:
        """Generate a concise summary using Groq API with Llama model."""
        if not self.client:
            return None

        # Prepare the text to summarize
        text_to_summarize = f"Title: {title}\n\n"
        if abstract:
            text_to_summarize += f"Abstract: {abstract}\n\n"
        if content:
            # Limit content length to avoid token limits
            text_to_summarize += f"Content: {content[:5000]}"

        prompt = f"""Please provide a concise summary of the following AI research paper or article.
Focus on:
1. Key findings or main contribution
2. Methodology (if applicable)
3. Practical implications

Keep the summary to 2-3 sentences maximum.

{text_to_summarize}

Summary:"""

        try:
            response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            if response.choices:
                return response.choices[0].message.content.strip()
            return None

        except Exception as e:
            logger.exception("Error generating summary")
            return None

    async def categorize(
        self,
        title: str,
        abstract: str
    ) -> list[str]:
        """Auto-categorize an article using Groq API with Llama model."""
        if not self.client:
            return []

        prompt = f"""Categorize the following AI research paper or article into one or more of these categories:
- NLP (Natural Language Processing)
- Computer Vision
- Machine Learning
- Reinforcement Learning
- Generative AI
- AI Safety
- Robotics
- Neural Networks
- LLM (Large Language Models)

Return only the category names, separated by commas. Choose 1-3 most relevant categories.

Title: {title}
Abstract: {abstract}

Categories:"""

        try:
            response = await self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            if response.choices:
                categories_text = response.choices[0].message.content.strip()
                categories = [cat.strip() for cat in categories_text.split(",")]
                return categories
            return []

        except Exception as e:
            logger.exception("Error categorizing")
            return []


# Singleton instance
summarizer_service = SummarizerService()
