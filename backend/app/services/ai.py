import httpx
from app.core.config import settings

class AIService:
    def __init__(self):
        self.ollama_url = settings.OLLAMA_URL
        self.model_name = settings.OLLAMA_MODEL



    async def analyze_legal_text(self, text: str) -> str:
        # Avoid timeout and models token max length
        truncated_text = text[:8000]

        prompt = (
            "You are a legal expert and professional document analyst.\n"
            "Analyze the following document text, provide a concise summary, "
            "and identify the crucial points or potential risks contained within it.\n\n"
            f"Document Text:\n{truncated_text}\n\n"
            "Analysis:"
        )

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False
        }

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(self.ollama_url, json=payload)
                response.raise_for_status()
                result = response.json()
                return result.get("response", "Failed to get an AI analysis")
            except Exception as e:
                return f"Error connecting to AI Agent. {str(e)}"
            