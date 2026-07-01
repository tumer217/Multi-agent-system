from google import genai
import os
from dotenv import load_dotenv

load_dotenv()

class PlannerAgent:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key)

    def create_plan(self, code_review):
        prompt = f"""You are a senior software engineer planning a fix.

Based on this code review, create a step-by-step plan to fix the issues.
Keep it concise, numbered steps only.

Code review:
{code_review}
"""
        response = self.client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        return response.text


if __name__ == "__main__":
    from code_reader_agent import CodeReaderAgent

    reader = CodeReaderAgent()
    planner = PlannerAgent()

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