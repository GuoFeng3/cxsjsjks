import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.llm.client import LLMClient
from src.llm.prompts import INTENT_CLASSIFICATION_PROMPT

def test_real_llm_call():
    # Using the API key found in the source code
    api_key = "sk-a328def3a0c94b0eaf4f5f2da8110cd8"
    client = LLMClient(api_key)
    
    print("Testing LLM connection with prompt: '还有多少钱'...")
    candidates = ["查询", "充值", "退出"]
    user_input = "还有多少钱"
    
    try:
        result = client.classify_intent(user_input, candidates, INTENT_CLASSIFICATION_PROMPT)
        print(f"User Input: {user_input}")
        print(f"Candidates: {candidates}")
        print(f"LLM Result: {result}")
        
        if result == "查询":
            print("SUCCESS: Intent correctly classified.")
        elif result == "None":
            print("FAILURE: LLM returned None.")
        else:
            print(f"WARNING: LLM returned unexpected result: {result}")
            
    except Exception as e:
        print(f"ERROR: Exception occurred: {e}")

if __name__ == "__main__":
    test_real_llm_call()
