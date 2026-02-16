"""Model loader — validates API keys and provides LLM instances."""

import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv(override=True)


class ModelConfig(BaseModel):
    google_api_key: str = Field(default="", description="API Key for Google Generative AI")
    groq_api_key: str = Field(default="", description="API Key for Groq")


class ConfigLoader:
    """Loads and validates configuration using Pydantic."""

    def __init__(self):
        try:
            self.config = ModelConfig(
                google_api_key=os.getenv("GOOGLE_API_KEY", ""),
                groq_api_key=os.getenv("GROQ_API_KEY", ""),
            )
        except ValidationError as e:
            raise ValueError(f"Configuration validation error: {e}")

    def get_config(self) -> ModelConfig:
        return self.config


class ModelLoader:
    """Loads API models using validated configuration."""

    def __init__(self):
        self.config_loader = ConfigLoader()
        self.config = self.config_loader.get_config()

    def load_groq_model(self, model_name: str = "llama-3.3-70b-versatile"):
        """Load a Groq-hosted model (default: Llama 3.3 70B)."""
        if not self.config.groq_api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables.")
        return ChatGroq(
            api_key=self.config.groq_api_key,
            model_name=model_name,
            temperature=0,
        )

    def load_google_model(self, model_name: str = "gemini-2.5-flash-lite"):
        """Load a Google Gemini model (default: gemini-2.5-flash-lite)."""
        if not self.config.google_api_key:
            raise ValueError("GOOGLE_API_KEY is not set in environment variables.")
        return ChatGoogleGenerativeAI(
            google_api_key=self.config.google_api_key,
            model=model_name,
            temperature=0,
        )