"""Tool schemas for Groq function calling."""

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "search_arxiv",
            "description": "Search arXiv for academic papers and preprints about AI, machine learning, and related topics. Use for research, algorithms, models, or technical concepts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for arXiv. Include relevant technical terms."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of papers to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for general knowledge articles. Use for background information, definitions, history, or broader context.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Wikipedia."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of articles to return (1-5, default 3)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "Search the web for recent news, blog posts, tutorials, and general content. Use for current events, recent developments, or practical information.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Web search query."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_youtube",
            "description": "Search YouTube for educational videos, tutorials, and presentations. Use when visual explanations or conference talks would be helpful.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "YouTube search query. Include terms like 'tutorial', 'explained' for better results."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of videos to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_semantic_scholar",
            "description": "Search Semantic Scholar for academic papers with citation counts. Use for finding highly-cited or recent research papers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Semantic Scholar."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of papers to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_huggingface",
            "description": "Search HuggingFace Hub for ML models. Use when looking for pre-trained models, fine-tuned models, or model architectures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for HuggingFace models."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of models to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_github",
            "description": "Search GitHub for ML/AI repositories. Use for finding open-source implementations, libraries, and tools.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for GitHub repositories."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of repos to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_papers_with_code",
            "description": "Search Papers With Code for papers that have code implementations. Use when looking for reproducible research with code.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Papers With Code."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (1-10, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_anthropic",
            "description": "Search Anthropic's research page for articles about Claude, constitutional AI, and AI safety. Use for Anthropic-specific research.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search query for Anthropic research."
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of articles to return (1-5, default 5)"
                    }
                },
                "required": ["query"]
            }
        }
    },
]
