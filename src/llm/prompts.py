
INTENT_CLASSIFICATION_PROMPT = """
            User input: "{user_input}"
            Candidates: {candidates}
            Identify which candidate matches the user input.
            Return ONLY the candidate string. If no match, return "None".
            """
