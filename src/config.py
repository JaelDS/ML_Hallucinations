"""
Configuration management for ML Hallucinations Research Project
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Central configuration class"""

    # Project paths
    PROJECT_ROOT = Path(__file__).parent.parent
    DATA_DIR = PROJECT_ROOT / "data"
    RESULTS_DIR = PROJECT_ROOT / "results"
    KNOWLEDGE_BASE_DIR = DATA_DIR / "knowledge_base"

    # Database
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(DATA_DIR / "hallucinations.db"))

    # OpenAI
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "500"))

    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Hallucination categories
    HALLUCINATION_TYPES = [
        "factual_error",
        "fabricated_citation",
        "fake_entity",
        "temporal_error",
        "security_misinformation",
        "fabricated_cve",
        "fake_tool",
        "confabulation"
    ]

    # Severity levels
    SEVERITY_LEVELS = ["low", "medium", "high", "critical"]

    # Mitigation strategies
    MITIGATION_STRATEGIES = [
        "baseline",  # No mitigation
        "rag",       # Retrieval-Augmented Generation
        "constitutional_ai",  # Constitutional AI
        "chain_of_thought"    # Chain-of-Thought verification
    ]

    @classmethod
    def validate(cls):
        """Validate configuration"""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY not set. Please create .env file from .env.example")

        # Create directories if they don't exist
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.RESULTS_DIR.mkdir(exist_ok=True)
        cls.KNOWLEDGE_BASE_DIR.mkdir(exist_ok=True)
        (cls.RESULTS_DIR / "charts").mkdir(exist_ok=True)
        (cls.RESULTS_DIR / "reports").mkdir(exist_ok=True)
        (cls.DATA_DIR / "exports").mkdir(exist_ok=True)

        return True

# Validate on import
if __name__ != "__main__":
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration warning: {e}")
