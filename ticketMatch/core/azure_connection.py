# Código base para azure_connection.py con el contenido que el usuario proporcionó

import os
import logging
from openai import AzureOpenAI
from dotenv import load_dotenv

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AzureConnection:
    def __init__(self):
        load_dotenv()
        self.endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
        self.api_key = os.environ.get("AZURE_OPENAI_KEY")
        self.deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "gpt-4o-mini")
        self.client = None
        logger.info(f"Deployment set to: {self.deployment}")

    def initialize(self) -> bool:
        try:
            if not self.endpoint or not self.api_key:
                raise ValueError("Azure OpenAI credentials not found in environment variables")

            self.client = AzureOpenAI(
                api_key=self.api_key,
                api_version="2024-10-21",
                azure_endpoint=self.endpoint
            )

            self.test_connection()
            return True

        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI: {str(e)}")
            return False

    def test_connection(self) -> bool:
        try:
            if not self.client:
                raise ValueError("Azure OpenAI client not initialized")

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Say 'hello'"}
                ],
                max_tokens=10
            )

            logger.info("Successfully connected to Azure OpenAI!")
            return True

        except Exception as e:
            logger.error(f"Error connecting to Azure OpenAI: {str(e)}")
            return False

    def get_client(self) -> AzureOpenAI:
        if not self.client:
            raise ValueError("Azure OpenAI client not initialized")
        return self.client

