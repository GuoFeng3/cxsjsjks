import json
import sys
from typing import Dict, List, Optional, Any

class Step:
    def __init__(self, name: str):
        self.name = name
        # Instead of separate buckets, we store a sequence of instructions
        self.instructions: List[Dict[str, Any]] = []
        self.branches: Dict[str, str] = {}
        self.silence_step: Optional[str] = None
        self.default_step: Optional[str] = None
        self.is_exit: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "instructions": self.instructions,
            "branches": self.branches,
            "silence_step": self.silence_step,
            "default_step": self.default_step,
            "is_exit": self.is_exit
        }

class Compiler:
    def compile(self, source_file: str, output_file: str):
        steps = {}
        current_step: Optional[Step] = None
        
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
        except FileNotFoundError:
            print(f"Error: Source file '{source_file}' not found.")
            return
            
        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split()
            token = parts[0]
            
            try:
                if token == 'Step':
                    step_name = parts[1]
                    current_step = Step(step_name)
                    steps[step_name] = current_step
                elif current_step:
                    if token == 'Speak':
                        msg = " ".join(parts[1:]).strip('"')
                        current_step.instructions.append({"type": "Speak", "content": msg})
                    elif token == 'Listen':
                        # Listen params are optional
                        params = parts[1:] if len(parts) > 1 else []
                        current_step.instructions.append({"type": "Listen", "params": params})
                    elif token == 'Branch':
                        remainder = " ".join(parts[1:])
                        if '"' in remainder:
                            intent = remainder.split('"')[1]
                            next_step = remainder.split('"')[2].strip().replace(',', '').strip()
                        else:
                            intent = parts[1].replace(',', '')
                            next_step = parts[2]
                        current_step.branches[intent] = next_step
                    elif token == 'Action':
                        action_name = parts[1]
                        args = [arg.strip('"') for arg in parts[2:]]
                        current_step.instructions.append({"type": "Action", "name": action_name, "args": args})
                    elif token == 'Silence':
                        current_step.silence_step = parts[1]
                    elif token == 'Default':
                        current_step.default_step = parts[1]
                    elif token == 'Exit':
                        current_step.is_exit = True
                        current_step.instructions.append({"type": "Exit"})
            except IndexError:
                print(f"Error compiling line {line_num}: {line}")
                continue

        # Convert to IR (Intermediate Representation) - JSON format
        ir_data = {name: step.to_dict() for name, step in steps.items()}
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(ir_data, f, indent=4, ensure_ascii=False)
            
        print(f"Compilation successful. IR written to '{output_file}'")

def main():
    if len(sys.argv) < 3:
        print("Usage: python compiler.py <source_file> <output_file>")
        print("Example: python compiler.py script.txt script.json")
        return
        
    compiler = Compiler()
    compiler.compile(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()
