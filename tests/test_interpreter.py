import unittest
import json
import os
import sys
from unittest.mock import mock_open, patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.interpreter import Interpreter

class TestInterpreter(unittest.TestCase):
    def setUp(self):
        # Sample IR data
        self.sample_ir = {
            "Start": {
                "name": "Start",
                "instructions": [
                    {"type": "Speak", "content": "Welcome $name"},
                    {"type": "Listen", "params": []}
                ],
                "branches": {
                    "Yes": "StepYes",
                    "No": "StepNo"
                },
                "silence_step": "StepSilence",
                "default_step": "StepDefault",
                "is_exit": False
            },
            "StepYes": {
                "name": "StepYes",
                "instructions": [{"type": "Exit"}],
                "branches": {},
                "is_exit": True
            },
            "StepNo": {
                "name": "StepNo",
                "instructions": [{"type": "Exit"}],
                "branches": {},
                "is_exit": True
            }
        }
        
        # Patch json.load to return sample data when initializing Interpreter
        # We also need to patch open to avoid file not found error
        with patch("builtins.open", mock_open(read_data="{}")), \
             patch("json.load", return_value=self.sample_ir):
            self.interpreter = Interpreter("dummy.json")
            
        self.interpreter.context["name"] = "User"

    def test_format_message(self):
        msg = self.interpreter.format_message("Hello $name")
        self.assertEqual(msg, "Hello User")
        
        self.interpreter.context["balance"] = 100
        msg = self.interpreter.format_message("Balance: $balance")
        self.assertEqual(msg, "Balance: 100")

    def test_analyze_intent_exact(self):
        candidates = ["Yes", "No"]
        result = self.interpreter.analyze_intent("Yes", candidates)
        self.assertEqual(result, "Yes")

    def test_analyze_intent_numerical(self):
        candidates = ["<=100", ">100"]
        
        result = self.interpreter.analyze_intent("50", candidates)
        self.assertEqual(result, "<=100")
        
        result = self.interpreter.analyze_intent("150", candidates)
        self.assertEqual(result, ">100")
        
        candidates_eq = ["=50", "Other"]
        result = self.interpreter.analyze_intent("50", candidates_eq)
        self.assertEqual(result, "=50")

    def test_analyze_intent_keyword(self):
        """测试关键词匹配（优先级高于 LLM）"""
        candidates = ["充值", "查询"]
        result = self.interpreter.analyze_intent("我要查询话费", candidates)
        self.assertEqual(result, "查询")

    @patch("src.core.interpreter.LLMClient")
    def test_analyze_intent_llm_fallback(self, mock_llm_class):
        """测试 LLM 回退机制（当关键词无法匹配时）"""
        mock_llm_instance = mock_llm_class.return_value
        self.interpreter.llm_client = mock_llm_instance
        
        candidates = ["查询", "充值"]
        mock_llm_instance.classify_intent.return_value = "查询"
        
        # 输入 "还有多少钱" 不包含 "查询" 或 "充值"，因此会跳过关键词匹配，进入 LLM 逻辑
        result = self.interpreter.analyze_intent("还有多少钱", candidates, )
        
        self.assertEqual(result, "查询")
        # 验证 classify_intent 被调用了一次
        mock_llm_instance.classify_intent.assert_called_once()


    @patch("src.core.interpreter.actions")
    def test_execute_action(self, mock_actions):
        # Mock a function in actions module
        mock_actions.some_action = MagicMock()
        
        self.interpreter.execute_action("some_action", ["arg1", "arg2"])
        
        mock_actions.some_action.assert_called_with(self.interpreter.context, ["arg1", "arg2"])

    @patch("builtins.print")
    @patch("builtins.input", side_effect=["Yes"])
    @patch("sys.exit")
    def test_run_flow_yes(self, mock_exit, mock_input, mock_print):
        # Test running the flow: Start -> Input "Yes" -> StepYes -> Exit
        
        # We need to catch sys.exit because it raises SystemExit
        try:
            self.interpreter.run()
        except SystemExit:
            pass
        
        # Verify prompts
        # Python 3.8+ call_args_list contains Call objects
        # We check if "Robot: Welcome User" was printed
        printed_messages = [call[0][0] for call in mock_print.call_args_list]
        self.assertIn("Robot: Welcome User", printed_messages)
        
        # Verify transition
        self.assertEqual(self.interpreter.current_step_name, "StepYes")

    @patch("builtins.print")
    @patch("builtins.input", side_effect=[""]) # Empty input -> Silence
    def test_run_flow_silence(self, mock_input, mock_print):
        # Modify sample IR to have a silence step that is NOT exit immediately, 
        # or just check transition
        
        # Start step has silence_step="StepSilence"
        # We need to add StepSilence to steps or it will error
        self.interpreter.steps["StepSilence"] = {
            "name": "StepSilence",
            "instructions": [{"type": "Exit"}],
            "is_exit": True
        }
        
        with patch("sys.exit") as mock_exit:
            try:
                self.interpreter.run()
            except SystemExit:
                pass
            
            self.assertEqual(self.interpreter.current_step_name, "StepSilence")

if __name__ == "__main__":
    unittest.main()
