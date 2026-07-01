from langgraph.graph import StateGraph, END
from typing import TypedDict

from code_reader_agent import CodeReaderAgent
from planner_agent import PlannerAgent
from code_writer_agent import CodeWriterAgent
from test_writer_agent import TestWriterAgent
from pr_opener_agent import PROpenerAgent

# Step 1: Define the shared state (the whiteboard)
class AgentState(TypedDict):
    original_code: str
    code_review: str
    plan: str
    fixed_code: str
    tests: str
    pr_url: str

# Step 2: Create agent instances
reader = CodeReaderAgent()
planner = PlannerAgent()
writer = CodeWriterAgent()
tester = TestWriterAgent()
pr_opener = PROpenerAgent()

# Step 3: Define node functions
def code_reader_node(state: AgentState) -> AgentState:
    print("Running Code Reader...")
    review = reader.read_code(state["original_code"])
    return {"code_review": review}

def planner_node(state: AgentState) -> AgentState:
    print("Running Planner...")
    plan = planner.create_plan(state["code_review"])
    return {"plan": plan}

def code_writer_node(state: AgentState) -> AgentState:
    print("Running Code Writer...")
    fixed = writer.write_fix(state["original_code"], state["plan"])
    return {"fixed_code": fixed}

def test_writer_node(state: AgentState) -> AgentState:
    print("Running Test Writer...")
    tests = tester.write_tests(state["fixed_code"])
    return {"tests": tests}

def pr_opener_node(state: AgentState) -> AgentState:
    print("Running PR Opener...")
    url = pr_opener.open_pr(
        repo_name="tumer217/agent-test-repo",
        branch_name="agent-fix-branch",
        file_path="fixed_code.py",
        file_content=state["fixed_code"],
        commit_message="Automated fix by AI agent pipeline",
        pr_title="Automated fix from multi-agent system",
        pr_body=f"## Code Review\n{state['code_review']}\n\n## Plan\n{state['plan']}\n\n## Tests\n{state['tests']}"
    )
    return {"pr_url": url}

# Step 4: Build the graph
workflow = StateGraph(AgentState)

workflow.add_node("code_reader", code_reader_node)
workflow.add_node("planner", planner_node)
workflow.add_node("code_writer", code_writer_node)
workflow.add_node("test_writer", test_writer_node)
workflow.add_node("pr_opener", pr_opener_node)

# Step 5: Connect the nodes with edges
workflow.set_entry_point("code_reader")
workflow.add_edge("code_reader", "planner")
workflow.add_edge("planner", "code_writer")
workflow.add_edge("code_writer", "test_writer")
workflow.add_edge("test_writer", "pr_opener")
workflow.add_edge("pr_opener", END)

# Step 6: Compile and run
app = workflow.compile()

if __name__ == "__main__":
    fake_code = """
def calculate_total(items):
    total = 0
    for item in items:
        total += item.price * item.quantity
    return total
"""

    result = app.invoke({"original_code": fake_code})

    print("\n=== FINAL RESULTS ===")
    print("PR URL:", result.get("pr_url", "No PR created"))