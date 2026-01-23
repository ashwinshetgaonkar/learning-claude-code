from anthropic import AsyncAnthropic
from typing import Optional
from ..config import settings


class SummarizerService:
    def __init__(self):
        self.client = None
        if settings.anthropic_api_key:
            self.client = AsyncAnthropic(api_key=settings.anthropic_api_key)

    async def summarize(
        self,
        title: str,
        abstract: str,
        content: Optional[str] = None
    ) -> Optional[str]:
        """Generate a concise summary using Claude API."""
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
            message = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=300,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            if message.content:
                return message.content[0].text.strip()
            return None

        except Exception as e:
            print(f"Error generating summary: {e}")
            return None

    async def categorize(
        self,
        title: str,
        abstract: str
    ) -> list[str]:
        """Auto-categorize an article using Claude API."""
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
            message = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            if message.content:
                categories_text = message.content[0].text.strip()
                categories = [cat.strip() for cat in categories_text.split(",")]
                return categories
            return []

        except Exception as e:
            print(f"Error categorizing: {e}")
            return []


# Singleton instance
summarizer_service = SummarizerService()
