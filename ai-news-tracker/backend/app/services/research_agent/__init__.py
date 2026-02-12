from .agent import ResearchAgentService

# Singleton instance
research_agent = ResearchAgentService()

__all__ = ["ResearchAgentService", "research_agent"]
