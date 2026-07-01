from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class CodeReaderAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def read_code(self, code_snippet):
        prompt = f"""You are a senior software engineer reviewing code.

Analyze this code and respond in this exact format:

SUMMARY: (2-3 sentences on what this code does)
POTENTIAL_ISSUES: (list any bugs, edge cases, or risks you notice. If none, say "No major issues found.")

Code:
{code_snippet}
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text


if __name__ == "__main__":
    agent = CodeReaderAgent()

    fake_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    return total
"""

    summary = agent.read_code(fake_code)
    print("Agent's summary:")
    print(summary)