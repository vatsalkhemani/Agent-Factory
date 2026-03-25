import json
import os
import time

from dotenv import load_dotenv
from google import genai

from config import GEMINI_MODEL, LLM_TIMEOUT

load_dotenv()


class GeminiClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        self.client = genai.Client(api_key=api_key)
        self.model = GEMINI_MODEL

    def generate(self, prompt: str, system_instruction: str = "", temperature: float = 0.7) -> str:
        config = genai.types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=8192,
            system_instruction=system_instruction if system_instruction else None,
        )
        for attempt in range(2):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )
                return response.text
            except Exception as e:
                if attempt == 0:
                    time.sleep(2)
                    continue
                raise e

    def generate_json(self, prompt: str, system_instruction: str = "", temperature: float = 0.7) -> dict:
        json_instruction = (
            (system_instruction + "\n\n") if system_instruction else ""
        ) + "IMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences, no explanation."

        text = self.generate(prompt, json_instruction, temperature)
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return json.loads(text)
