import json
import urllib.request
import urllib.error
from typing import List

class LLMClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.api_url = "https://api.deepseek.com/chat/completions"

    def classify_intent(self, user_input: str, candidates: List[str], prompt_template: str) -> str:
        prompt = prompt_template.format(
            user_input=user_input, 
            candidates=json.dumps(candidates, ensure_ascii=False)
        )
        payload = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are an intent classifier."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        try:
            req = urllib.request.Request(
                self.api_url,
                data=json.dumps(payload).encode('utf-8'),
                headers=headers,
                method="POST"
            )
            with urllib.request.urlopen(req) as response:
                result = json.loads(response.read().decode('utf-8'))

                content = result['choices'][0]['message']['content'].strip()
                # Simple validation: ensure the returned content is one of the candidates
                # or contains it (heuristic from original code)
                for cand in candidates:
                    if cand in content:
                        return cand
                return "None"
        except Exception as e:
            return "None"
