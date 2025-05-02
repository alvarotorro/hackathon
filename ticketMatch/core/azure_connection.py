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
            
            # Get completion from Azure OpenAI
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {"role": "system", "content": "You are an expert at matching support tickets with the most suitable ambassadors based on their skills, availability, and historical performance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            # Parse the response
            result = json.loads(response.choices[0].message.content)
            
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
        """Format the prompt for Azure OpenAI."""
        ticket = payload["ticket"]
        ambassadors = payload["available_ambassadors"]
        
        prompt = f"""
        Please analyze the following ticket and available ambassadors to find the best match.
        
        TICKET:
        - Case Number: {ticket['case_number']}
        - Line of Business: {ticket['line_of_business']}
        - Product: {ticket['primary_product']}
        - Priority: {ticket['priority']}
        - Complexity: {ticket['complexity']}
        - State: {ticket['current_state']}
        
        AVAILABLE AMBASSADORS:
        """
        
        for amb in ambassadors:
            prompt += f"""
            Ambassador {amb['name']}:
            - Skills: {', '.join(amb['skills'])}
            - CSAT Score: {amb['csat_score']}
            - Expertise Level: {amb['expertise_level']}
            - Current Workload: {amb['current_workload']}
            """
        
        prompt += """
        Please provide your analysis in the following JSON format:
        {
            "ambassador_id": "ID of the best matching ambassador",
            "explanation": "Detailed explanation of why this ambassador is the best match",
            "confidence_score": 0.95
        }
        """
        
        return prompt

