from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class TestWriterAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def write_tests(self, fixed_code):
        prompt = f"""You are a senior software engineer writing unit tests.

Here is the fixed code:
{fixed_code}

Write pytest unit tests that cover the normal case and the edge cases (missing attributes, non-numeric values, negative values). Only output the test code, no explanations.
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text


if __name__ == "__main__":
    from code_reader_agent import CodeReaderAgent
    from planner_agent import PlannerAgent
    from code_writer_agent import CodeWriterAgent

    reader = CodeReaderAgent()
    planner = PlannerAgent()
    writer = CodeWriterAgent()
    tester = TestWriterAgent()

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

    tests = tester.write_tests(fixed_code)
    print("\n=== TESTS ===")
    print(tests)