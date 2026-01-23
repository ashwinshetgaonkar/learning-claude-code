from typing import List
import re


def auto_categorize(title: str, abstract: str = "") -> List[str]:
    """
    Rule-based auto-categorization as a fallback when LLM is not available.
    """
    text = f"{title} {abstract}".lower()
    categories = set()

    # Category patterns
    patterns = {
        "NLP": [
            r"\bnlp\b", r"natural language", r"language model", r"text generation",
            r"sentiment", r"translation", r"transformer", r"bert", r"gpt",
            r"chatbot", r"dialogue", r"question answering", r"summarization",
            r"named entity", r"parsing", r"tokeniz",
        ],
        "Computer Vision": [
            r"computer vision", r"image", r"video", r"object detection",
            r"segmentation", r"visual", r"cnn", r"convolutional",
            r"recognition", r"diffusion", r"stable diffusion", r"dalle",
            r"midjourney", r"image generation",
        ],
        "Machine Learning": [
            r"machine learning", r"\bml\b", r"supervised", r"unsupervised",
            r"classification", r"regression", r"clustering", r"training",
            r"optimization", r"gradient", r"loss function",
        ],
        "Reinforcement Learning": [
            r"reinforcement learning", r"\brl\b", r"reward", r"agent",
            r"policy", r"q-learning", r"rlhf", r"environment",
        ],
        "Generative AI": [
            r"generative", r"generation", r"diffusion", r"gan",
            r"autoencoder", r"vae", r"creative", r"synthesis",
        ],
        "AI Safety": [
            r"safety", r"alignment", r"harmful", r"bias", r"fairness",
            r"interpretab", r"explainab", r"robustness", r"adversarial",
            r"ethics", r"responsible ai",
        ],
        "Robotics": [
            r"robot", r"manipulation", r"navigation", r"autonomous",
            r"control", r"motor", r"embodied",
        ],
        "Neural Networks": [
            r"neural network", r"deep learning", r"layer", r"architecture",
            r"attention", r"backprop", r"activation", r"neuron",
        ],
        "LLM": [
            r"\bllm\b", r"large language model", r"gpt", r"claude",
            r"llama", r"gemini", r"palm", r"chatgpt", r"foundation model",
            r"instruction", r"fine-tun", r"prompt",
        ],
    }

    for category, category_patterns in patterns.items():
        for pattern in category_patterns:
            if re.search(pattern, text):
                categories.add(category)
                break

    # If no categories found, default to AI
    if not categories:
        categories.add("AI")

    return list(categories)


def deduplicate_articles(articles: List[dict]) -> List[dict]:
    """
    Remove duplicate articles based on title similarity and source_id.
    """
    seen_ids = set()
    seen_titles = set()
    unique_articles = []

    for article in articles:
        source_id = article.get("source_id", "")
        title = article.get("title", "").lower().strip()

        # Normalize title for comparison
        normalized_title = re.sub(r"[^\w\s]", "", title)
        normalized_title = " ".join(normalized_title.split())

        # Check for duplicates
        if source_id in seen_ids:
            continue

        # Check for similar titles (allows for minor differences)
        is_duplicate = False
        for seen_title in seen_titles:
            # Simple similarity check - if 80% of words match
            title_words = set(normalized_title.split())
            seen_words = set(seen_title.split())
            if title_words and seen_words:
                overlap = len(title_words & seen_words)
                max_len = max(len(title_words), len(seen_words))
                if overlap / max_len > 0.8:
                    is_duplicate = True
                    break

        if not is_duplicate:
            seen_ids.add(source_id)
            seen_titles.add(normalized_title)
            unique_articles.append(article)

    return unique_articles
