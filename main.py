import sys
import os

# Add src to python path if needed, though usually not if we run as module or from root
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.interpreter import Interpreter
from src.core.compiler import Compiler

def main():
    if len(sys.argv) < 2:
        
        print("Usage:")
        print("  python main.py run <script_json>")
        print("  python main.py compile <script_txt> <output_json>")
        return

    command = sys.argv[1]
    
    if command == "run":
        if len(sys.argv) < 3:
            print("Usage: python main.py run <script_json>")
            return
        interpreter = Interpreter(sys.argv[2])
        interpreter.run()
        
    elif command == "compile":
        if len(sys.argv) < 4:
            print("Usage: python main.py compile <script_txt> <output_json>")
            return
        compiler = Compiler()
        compiler.compile(sys.argv[2], sys.argv[3])
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()
