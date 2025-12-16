import json
import sys
import time
from typing import Dict, List, Optional, Any
from src.core import actions
from src.llm import LLMClient, INTENT_CLASSIFICATION_PROMPT

# Global Data Storage
API_KEY = "sk-a328def3a0c94b0eaf4f5f2da8110cd8"

class Interpreter:
    def __init__(self, ir_file: str):
        self.steps = self.load_ir(ir_file)
        self.context: Dict[str, Any] = {
            "last_intent": "",
            "last_user_input": "",
            "last_order_id": "",
            "check_result": ""
        }
        self.current_step_name: str = list(self.steps.keys())[0] if self.steps else ""
        self.llm_client = LLMClient(API_KEY)
        
    def load_ir(self, ir_file: str) -> Dict[str, Any]:
        try:
            with open(ir_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Error: IR file '{ir_file}' not found.")
            sys.exit(1)
            
    def run(self):
        print("系统启动...")
        while True:
            if not self.current_step_name:
                break
                
            step = self.steps.get(self.current_step_name)
            if not step:
                print(f"Error: Step {self.current_step_name} not found.")
                break
            
            instructions = step.get("instructions", [])
            should_branch = True
            
            for instr in instructions:
                if instr["type"] == "Speak":
                    message = self.format_message(instr["content"])
                    print(f"Robot: {message}")
                    
                elif instr["type"] == "Action":
                    self.execute_action(instr["name"], instr["args"])
                    
                elif instr["type"] == "Listen":
                    # Parse timeout from params if available
                    timeout = None
                    params = instr.get("params", [])
                    if params and params[0].isdigit():
                        timeout = int(params[0])
                    user_input = input("User: ")

                    if not user_input:
                        silence_step = step.get("silence_step")
                        if silence_step:
                            self.current_step_name = silence_step
                            should_branch = False 
                            break 
                    last_user_input = user_input.strip()
                    self.context["last_user_input"] = last_user_input
                    # Intent analysis
                    branches = step.get("branches", {})
                    intent = self.analyze_intent(user_input, list(branches.keys()))
                    self.context["last_intent"] = intent
                    
                elif instr["type"] == "Exit":
                    sys.exit(0)

            if not should_branch:
                continue
                
            branches = step.get("branches", {})
            default_step = step.get("default_step")
            
            if branches or default_step:
                intent = self.context.get("last_intent", "")
                if intent in branches:
                    self.current_step_name = branches[intent]
                elif default_step:
                     self.current_step_name = default_step
                else:
                    pass
            elif step.get("is_exit"):
                break
            else:
                 pass

    def format_message(self, template: str) -> str:
        msg = template
        for key, value in self.context.items():
            placeholder = f"${key}"
            if placeholder in msg:
                msg = msg.replace(placeholder, str(value))
        return msg

    def execute_action(self, action_name: str, args: List[str]):
        if hasattr(actions, action_name):
            func = getattr(actions, action_name)
            func(self.context, args)
        else:
            print(f"Error: Action '{action_name}' not found.")
    
    def analyze_intent(self, user_input: str, candidates: List[str]) -> str:
        

        if not user_input: return "None"
        
        # 1. Exact match
        if user_input in candidates:
            return user_input
            
        # 2. Numerical comparison
        if user_input.replace('.', '', 1).isdigit():
            try:
                val = float(user_input)
                for cand in candidates:
                    if cand.startswith("<="):
                        limit = float(cand[2:])
                        if val <= limit: return cand
                    elif cand.startswith(">="):
                        limit = float(cand[2:])
                        if val >= limit: return cand
                    elif cand.startswith("<"):
                        limit = float(cand[1:])
                        if val < limit: return cand
                    elif cand.startswith(">"):
                        limit = float(cand[1:])
                        if val > limit: return cand
                    elif cand.startswith("="):
                        limit = float(cand[1:])
                        if val == limit: return cand
            except ValueError:
                pass

        # 3. Keyword match
        for cand in candidates:
            if cand in user_input:
                return cand

        # 4. LLM Match
        if not candidates:
            return "None"  
        return self.llm_client.classify_intent(user_input, candidates, INTENT_CLASSIFICATION_PROMPT)
