# Código base para azure_connection.py con el contenido que el usuario proporcionó

import os
import logging
from dotenv import load_dotenv
from openai import AzureOpenAI
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class AzureConnection:
    def __init__(self):
        """Initialize Azure OpenAI connection."""
        # Load environment variables from .env file
        load_dotenv()
        
        # Get Azure credentials
        self.endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.key = os.getenv("AZURE_OPENAI_KEY")
        self.deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4")
        
        if not self.endpoint or not self.key:
            raise ValueError("Azure OpenAI credentials not found in environment variables. Please check your .env file.")
        
        # Clean and format the endpoint
        self.endpoint = self.endpoint.strip()
        if not self.endpoint.startswith("https://"):
            self.endpoint = f"https://{self.endpoint}"
        
        logger.info(f"Using OpenAI endpoint: {self.endpoint}")
        
        try:
            # Initialize Azure OpenAI client
            self.client = AzureOpenAI(
                api_key=self.key,
                api_version="2024-02-15-preview",
                azure_endpoint=self.endpoint
            )
            
            # Test connection
            if not self.test_connection():
                raise ConnectionError("Failed to connect to Azure OpenAI. Please check your credentials.")
                
        except Exception as e:
            logger.error(f"Error initializing Azure OpenAI client: {str(e)}")
            raise

    def test_connection(self) -> bool:
        """Test the connection to Azure OpenAI."""
        try:
            if not self.client:
                raise ValueError("Azure OpenAI client not initialized")

            # Test with a simple completion
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are a test assistant."},
                    {"role": "user", "content": "Say 'hello'"}
                ],
                max_tokens=10
            )
            
            if not response:
                raise ValueError("No response received from Azure OpenAI")
            
            logger.info("Successfully connected to Azure OpenAI!")
            return True

        except Exception as e:
            logger.error(f"Error connecting to Azure OpenAI: {str(e)}")
            return False

    def get_match(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send matching request to Azure OpenAI and get the best match.
        
        Args:
            payload: Dictionary containing ticket and ambassador data
            
        Returns:
            Dictionary containing the best match and explanation
        """
        try:
            # Format the prompt
            prompt = self._format_matching_prompt(payload)

            if not prompt or not isinstance(prompt, str):
                logger.error("Prompt generation failed: prompt is empty or invalid.")
                return {}

            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that selects the best ambassador for a support ticket based on skills, workload, and CSAT. Reply only in valid JSON."
                    },
                    {
                        "role": "user",
                        "content": prompt  # ⚠️ ahora garantizado que es string no vacío
                    }
                ],
                temperature=0.7,
                max_tokens=600
            )

            
            # Parse the response
            content = response.choices[0].message.content
            logger.debug(f"Azure response raw content:\n{content}")

            try:
                result = json.loads(content)
                print(result)
            except json.JSONDecodeError:
                logger.warning("Respuesta no es JSON válido. Devolviendo texto como 'raw_response'.")
                return {"raw_response": content}

            
            return {
                "best_match": {
                    "ambassador_id": result["ambassador_id"],
                    "explanation": result["explanation"],
                    "confidence_score": result["confidence_score"]
                }
            }
            
        except Exception as e:
            logger.error(f"Error in Azure OpenAI matching: {str(e)}")
            return {}



    def _format_matching_prompt(self, payload: Dict[str, Any]) -> str:
        ticket = payload["ticket"]
        ambassadors = payload["available_ambassadors"]

        prompt = f"""
    You are an AI assistant that must select the most suitable ambassador for a support ticket.

    You will receive:
    - One support TICKET with metadata.
    - A list of AVAILABLE AMBASSADORS with their attributes.

    ⚠️ Respond ONLY with a valid JSON object in the following format (without any explanation or text before or after):

    {{
    "ambassador_id": "<best_match_id>",
    "explanation": "<short_reason>",
    "confidence_score": <float between 0.0 and 1.0>
    }}

    TICKET:
    {json.dumps(ticket, indent=2)}

    AVAILABLE AMBASSADORS:
    {json.dumps(ambassadors, indent=2)}
        """
        return prompt.strip()

