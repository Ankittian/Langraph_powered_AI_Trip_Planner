import os
from typing import Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError
from langchain_groq import ChatGroq
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables
load_dotenv()

class ModelConfig(BaseModel):
    google_api_key: str = Field(..., description="API Key for Google Generative AI")
    groq_api_key: str = Field(..., description="API Key for Groq")

class ConfigLoader:
    """Loads and validates configuration using Pydantic."""
    def __init__(self):
        try:
            # Attempt to load from environment variables
            self.config = ModelConfig(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                groq_api_key=os.getenv("GROQ_API_KEY")
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

    def load_groq_model(self, model_name: str = "llama3-8b-8192"):
        return ChatGroq(
            api_key=self.config.groq_api_key,
            model_name=model_name
        )

    def load_google_model(self, model_name: str = "gemini-pro"):
        """
        Loads the Google Gemini model.
        
        Args:
            model_name (str): The name of the model to load. defaults to "gemini-pro".
        """
        return ChatGoogleGenerativeAI(
            google_api_key=self.config.google_api_key,
            model=model_name,
            convert_system_message_to_human=True
        )