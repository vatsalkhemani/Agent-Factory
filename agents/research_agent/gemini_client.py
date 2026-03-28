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

    def generate(self, prompt: str, system_instruction: str = "", temperature: float = 0.7, model: str = "") -> str:
        config = genai.types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=8192,
            system_instruction=system_instruction if system_instruction else None,
        )
        last_error = None
        for attempt in range(4):
            try:
                response = self.client.models.generate_content(
                    model=model or self.model,
                    contents=prompt,
                    config=config,
                )
                text = response.text
                if text is None:
                    raise ValueError("Gemini returned empty response (possibly blocked by safety filters)")
                return text
            except Exception as e:
                last_error = e
                err_str = str(e)
                if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    wait = min(30 * (attempt + 1), 90)
                    print(f"Rate limited, waiting {wait}s (attempt {attempt + 1}/4)...")
                    time.sleep(wait)
                    continue
                if "empty response" in err_str and attempt < 2:
                    time.sleep(2)
                    continue
                if attempt < 1:
                    time.sleep(2)
                    continue
                raise e
        raise last_error or RuntimeError("All Gemini API attempts failed")

    def _clean_json_text(self, text: str) -> str:
        text = text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
        return text

    def _parse_json_robust(self, text: str):
        text = self._clean_json_text(text)

        # Strategy 1: Direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Find outermost array or object
        for start_char, end_char in [('[', ']'), ('{', '}')]:
            start = text.find(start_char)
            if start != -1:
                end = text.rfind(end_char)
                if end != -1 and end > start:
                    try:
                        return json.loads(text[start:end + 1])
                    except json.JSONDecodeError:
                        pass

        # Strategy 3: Multiple JSON objects -- collect into array
        objects = []
        decoder = json.JSONDecoder()
        idx = 0
        while idx < len(text):
            while idx < len(text) and text[idx] in ' \t\n\r,':
                idx += 1
            if idx >= len(text):
                break
            if text[idx] in '{[':
                try:
                    obj, end_idx = decoder.raw_decode(text, idx)
                    objects.append(obj)
                    idx = end_idx
                except json.JSONDecodeError:
                    idx += 1
            else:
                idx += 1

        if objects:
            return objects if len(objects) > 1 else objects[0]

        raise json.JSONDecodeError("No valid JSON found", text, 0)

    def generate_json(self, prompt: str, system_instruction: str = "", temperature: float = 0.7, model: str = "") -> dict:
        json_instruction = (
            (system_instruction + "\n\n") if system_instruction else ""
        ) + "IMPORTANT: Respond ONLY with valid JSON. No markdown, no code fences, no explanation. Ensure all string values are properly escaped. If returning multiple items, wrap them in a JSON array."

        for attempt in range(3):
            text = self.generate(prompt, json_instruction, temperature, model=model)
            try:
                return self._parse_json_robust(text)
            except json.JSONDecodeError:
                if attempt < 2:
                    json_instruction = (
                        (system_instruction + "\n\n") if system_instruction else ""
                    ) + "CRITICAL: Return ONLY a single valid JSON object or array. No text before or after. No unescaped quotes in strings. No trailing commas. Wrap multiple items in a JSON array []."
                    time.sleep(1)
                    continue
                raise
