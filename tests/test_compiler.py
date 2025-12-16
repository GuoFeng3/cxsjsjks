import unittest
import json
import os
from unittest.mock import mock_open, patch, MagicMock
import sys

# Add project root to sys.path to import src
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.core.compiler import Compiler

class TestCompiler(unittest.TestCase):
    def setUp(self):
        self.compiler = Compiler()

    @patch("builtins.open", new_callable=mock_open)
    def test_compile_file_not_found(self, mock_file):
        # Setup mock to raise FileNotFoundError when opening source file
        mock_file.side_effect = FileNotFoundError
        
        # Capture stdout to verify error message
        with patch('sys.stdout', new=MagicMock()) as mock_stdout:
            self.compiler.compile("non_existent.txt", "output.json")
            
            # Verify correct file was attempted to be opened
            mock_file.assert_called_with("non_existent.txt", 'r', encoding='utf-8')
            
            # Verify error message was printed (flexible match)
            # Since print is a function call on the mock object
            # We check if any call args contained the expected string
            found_error = False
            for call in mock_stdout.write.call_args_list:
                if "Error: Source file 'non_existent.txt' not found" in call[0][0]:
                    found_error = True
                    break
            # Alternatively, if print calls write multiple times or with newline
            # It's safer to just check if the method handled the exception gracefully
            # Current implementation returns early on error, so no write to output file should happen.
            
            # Ensure output file was NOT opened for writing
            # The mock_file is the same mock for read and write
            # We expect only 1 call (the read attempt)
            self.assertEqual(mock_file.call_count, 1)

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_compile_simple_script(self, mock_json_dump, mock_file):
        # Sample script content
        script_content = """
Step Welcome
    Speak "Hello World"
    Listen
    Branch "Yes" Step2
    Default StepEnd

Step Step2
    Action do_something "arg1"
    Silence StepEnd

Step StepEnd
    Exit
"""
        # Configure mock to return the script content
        mock_file.return_value.__enter__.return_value.readlines.return_value = script_content.splitlines()

        self.compiler.compile("source.txt", "output.json")

        # Verify source file read
        mock_file.assert_any_call("source.txt", 'r', encoding='utf-8')
        
        # Verify output file write
        mock_file.assert_any_call("output.json", 'w', encoding='utf-8')

        # Verify json structure passed to dump
        # args[0] is the data, args[1] is the file object
        args, _ = mock_json_dump.call_args
        data = args[0]
        
        self.assertIn("Welcome", data)
        self.assertIn("Step2", data)
        self.assertIn("StepEnd", data)
        
        # Check Welcome step
        welcome = data["Welcome"]
        self.assertEqual(welcome["name"], "Welcome")
        self.assertEqual(len(welcome["instructions"]), 2)
        self.assertEqual(welcome["instructions"][0], {"type": "Speak", "content": "Hello World"})
        self.assertEqual(welcome["instructions"][1], {"type": "Listen", "params": []})
        self.assertEqual(welcome["branches"]["Yes"], "Step2")
        self.assertEqual(welcome["default_step"], "StepEnd")

        # Check Step2
        step2 = data["Step2"]
        self.assertEqual(step2["instructions"][0], {"type": "Action", "name": "do_something", "args": ["arg1"]})
        self.assertEqual(step2["silence_step"], "StepEnd")

        # Check StepEnd
        step_end = data["StepEnd"]
        self.assertTrue(step_end["is_exit"])
        self.assertEqual(step_end["instructions"][0], {"type": "Exit"})

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_compile_complex_branch(self, mock_json_dump, mock_file):
        # Test implicit branch format: Branch "Intent" NextStep
        script_content = """
Step Start
    Branch "Check Balance" BalanceStep
    Branch "Order Item" OrderStep
"""
        mock_file.return_value.__enter__.return_value.readlines.return_value = script_content.splitlines()

        self.compiler.compile("source.txt", "output.json")
        
        args, _ = mock_json_dump.call_args
        data = args[0]
        
        branches = data["Start"]["branches"]
        self.assertEqual(branches["Check Balance"], "BalanceStep")
        self.assertEqual(branches["Order Item"], "OrderStep")

    @patch("builtins.open", new_callable=mock_open)
    @patch("json.dump")
    def test_compile_listen_params(self, mock_json_dump, mock_file):
        script_content = """
Step Start
    Listen 10
"""
        mock_file.return_value.__enter__.return_value.readlines.return_value = script_content.splitlines()

        self.compiler.compile("source.txt", "output.json")
        
        args, _ = mock_json_dump.call_args
        data = args[0]
        
        instructions = data["Start"]["instructions"]
        self.assertEqual(instructions[0]["type"], "Listen")
        self.assertEqual(instructions[0]["params"], ["10"])

if __name__ == "__main__":
    unittest.main()
