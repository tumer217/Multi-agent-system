from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class CodeWriterAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def write_fix(self, original_code, plan):
        prompt = f"""You are a senior software engineer implementing a fix.

Here is the original code:
{original_code}

Here is the plan to fix it:
{plan}

Write the complete, fixed version of the code. Only output the code itself, no explanations.
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text


if __name__ == "__main__":
    from code_reader_agent import CodeReaderAgent
    from planner_agent import PlannerAgent

    reader = CodeReaderAgent()
    planner = PlannerAgent()
    writer = CodeWriterAgent()

    fake_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    return total
"""

    review = reader.read_code(fake_code)
    print("=== CODE REVIEW ===")
    print(review)

    plan = planner.create_plan(review)
    print("\n=== PLAN ===")
    print(plan)

    fixed_code = writer.write_fix(fake_code, plan)
    print("\n=== FIXED CODE ===")
    print(fixed_code)