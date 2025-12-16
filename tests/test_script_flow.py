import unittest
import json
import os
import sys
from unittest.mock import mock_open, patch, MagicMock

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.interpreter import Interpreter
from src.core.compiler import Compiler

class TestScriptFlow(unittest.TestCase):
    #setup和teardown函数会在每个test方法运行前和运行后调用
    def setUp(self):
        self.compiler = Compiler()
        # Ensure we have a clean context for each test
        self.mock_input_patcher = patch('builtins.input')
        self.mock_input = self.mock_input_patcher.start()
        self.mock_print_patcher = patch('builtins.print')
        self.mock_print = self.mock_print_patcher.start()
        
        
        script_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script1.txt')
        json_path = os.path.join(os.path.dirname(__file__), '..', 'scripts', 'test_script1.json')
        
        # Compile
        self.compiler.compile(script_path, json_path)
        self.json_path = json_path
        
        # Initialize interpreter
        self.interpreter = Interpreter(self.json_path)
        
        # Mock LLM to avoid API calls and ensuring deterministic branching
        self.interpreter.llm_client = MagicMock()
        self.interpreter.llm_client.classify_intent.side_effect = lambda u, c, p: "None" # Default fallback

    def tearDown(self):
        self.mock_input_patcher.stop()
        self.mock_print_patcher.stop()
        if os.path.exists(self.json_path):
            os.remove(self.json_path)

    def test_login_and_exit(self):
        """Test simple login and immediate exit."""
        # Inputs: "Alice" (Login) -> "退出" (Exit)
        self.mock_input.side_effect = ["Alice", "退出"]
        
        # Need to mock actions because they might print or fail
        with patch('src.core.actions.user_login') as mock_login:
            try:
                self.interpreter.run()
            except SystemExit:
                pass
            
            # Verify login action was called
            mock_login.assert_called()
            
            # Verify exit message
            printed_messages = [call[0][0] for call in self.mock_print.call_args_list]
            self.assertTrue(any("再见" in msg for msg in printed_messages))

    def test_charge_bill_flow(self):
        """Test charging bill flow: Login -> 充话费 -> 100 -> 退出"""
        self.mock_input.side_effect = ["Bob", "充话费", "100", "退出"]
        
        with patch('src.core.actions.user_login'), \
             patch('src.core.actions.charge_bill') as mock_charge:
             
            try:
                self.interpreter.run()
            except SystemExit:
                pass
                
            # Verify charge action called with context
            mock_charge.assert_called()
            
            # Verify success message
            printed_messages = [call[0][0] for call in self.mock_print.call_args_list]
            self.assertTrue(any("话费充值成功" in msg for msg in printed_messages))

    def test_invalid_charge_amount(self):
        """Test invalid charge amount: Login -> 充话费 -> -50 -> 100 -> 退出"""

        self.mock_input.side_effect = ["Charlie", "充话费", "-50", "100", "退出"]
        
        with patch('src.core.actions.user_login'), \
             patch('src.core.actions.charge_bill') as mock_charge:
            
            try:
                self.interpreter.run()
            except SystemExit:
                pass
            
            printed_messages = [call[0][0] for call in self.mock_print.call_args_list]
            
            # Should see error message
            self.assertTrue(any("数值有误" in msg for msg in printed_messages))
            # Should eventually succeed
            self.assertTrue(any("话费充值成功" in msg for msg in printed_messages))

    def test_change_combo(self):
        """Test combo change: Login -> 变更套餐 -> 套餐2 -> 退出"""
        self.mock_input.side_effect = ["Dave", "变更套餐", "套餐2", "退出"]
        
        with patch('src.core.actions.user_login'), \
             patch('src.core.actions.change_combo') as mock_combo:
             
            try:
                self.interpreter.run()
            except SystemExit:
                pass
                
            mock_combo.assert_called()
            printed_messages = [call[0][0] for call in self.mock_print.call_args_list]
            self.assertTrue(any("套餐变更成功" in msg for msg in printed_messages))

if __name__ == "__main__":
    unittest.main()
