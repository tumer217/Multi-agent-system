from langgraph.graph import StateGraph, END
from typing import TypedDict
from github import Github
import os
from dotenv import load_dotenv
from code_reader_agent import CodeReaderAgent
from planner_agent import PlannerAgent
from code_writer_agent import CodeWriterAgent
from test_writer_agent import TestWriterAgent
from pr_opener_agent import PROpenerAgent
from research_agent import ResearchAgent
from sandbox_runner import run_tests_in_docker

load_dotenv()

class AgentState(TypedDict):
    issue: str
    code_context: str
    code_review: str
    plan: str
    complexity: str
    research_notes: str
    patch: str
    tests: str
    test_passed: bool
    test_output: str
    retry_count: int
    pr_url: str

reader = CodeReaderAgent()
planner = PlannerAgent()
writer = CodeWriterAgent()
tester = TestWriterAgent()
pr_opener = PROpenerAgent()
researcher = ResearchAgent()

REPO_NAME = "tumer217/agent-test-repo"
MAX_RETRIES = 2

def fetch_github_issue_and_code(repo_name, issue_number, file_path):
    g = Github(os.getenv("GITHUB_TOKEN"))
    repo = g.get_repo(repo_name)
    issue = repo.get_issue(number=issue_number)
    issue_text = f"{issue.title}\n\n{issue.body}"
    file_content = repo.get_contents(file_path)
    code_text = file_content.decoded_content.decode("utf-8")
    return {
        "issue": issue_text,
        "code_context": code_text,
        "retry_count": 0,
    }

def code_reader_node(state: AgentState) -> AgentState:
    print("Running Code Reader...")
    review = reader.read_code(state["code_context"])
    return {"code_review": review}

def planner_node(state: AgentState) -> AgentState:
    print("Running Planner...")
    plan = planner.create_plan(state["code_review"])
    complexity = planner.classify_complexity(state["code_review"])
    print(f"Complexity decided: {complexity}")
    return {"plan": plan, "complexity": complexity}

def route_by_complexity(state: AgentState) -> str:
    return state["complexity"]

def research_node(state: AgentState) -> AgentState:
    print("Running Research Agent...")
    notes = researcher.research(REPO_NAME, state["code_review"])
    return {"research_notes": notes}

def code_writer_node(state: AgentState) -> AgentState:
    print("Running Code Writer...")
    context = state["code_context"]
    if state.get("research_notes"):
        context = context + "\n\n" + state["research_notes"]
    # if this is a retry, tell the writer what went wrong last time
    if state.get("test_output"):
        context = context + "\n\nPrevious attempt failed these tests:\n" + state["test_output"]
    fixed = writer.write_fix(context, state["plan"])
    return {"patch": fixed}

def test_writer_node(state: AgentState) -> AgentState:
    print("Running Test Writer...")
    tests = tester.write_tests(state["patch"])
    return {"tests": tests}

def sandbox_node(state: AgentState) -> AgentState:
    print("Running Sandbox (Docker)...")
    result = run_tests_in_docker(state["patch"], state["tests"])
    print(f"Tests passed: {result['passed']}")
    retry_count = state.get("retry_count", 0)
    if not result["passed"]:
        retry_count += 1
    return {
        "test_passed": result["passed"],
        "test_output": result["output"],
        "retry_count": retry_count,
    }

def route_by_test_result(state: AgentState) -> str:
    if state["test_passed"]:
        return "pass"
    if state["retry_count"] >= MAX_RETRIES:
        print(f"Max retries ({MAX_RETRIES}) reached. Giving up, opening PR anyway with last attempt.")
        return "pass"
    print(f"Tests failed. Retrying (attempt {state['retry_count']} of {MAX_RETRIES})...")
    return "retry"

def pr_opener_node(state: AgentState) -> AgentState:
    print("Running PR Opener...")
    url = pr_opener.open_pr(
        repo_name=REPO_NAME,
        branch_name="agent-fix-branch",
        file_path="fixed_code.py",
        file_content=state["patch"],
        commit_message="Automated fix by AI agent pipeline",
        pr_title="Automated fix from multi-agent system",
        pr_body=f"## Code Review\n{state['code_review']}\n\n## Plan\n{state['plan']}\n\n## Tests\n{state['tests']}\n\n## Sandbox Result\nPassed: {state['test_passed']}"
    )
    return {"pr_url": url}

workflow = StateGraph(AgentState)
workflow.add_node("code_reader", code_reader_node)
workflow.add_node("planner", planner_node)
workflow.add_node("research_agent", research_node)
workflow.add_node("code_writer", code_writer_node)
workflow.add_node("test_writer", test_writer_node)
workflow.add_node("sandbox", sandbox_node)
workflow.add_node("pr_opener", pr_opener_node)

workflow.set_entry_point("code_reader")
workflow.add_edge("code_reader", "planner")
workflow.add_conditional_edges("planner", route_by_complexity, {
    "simple": "code_writer",
    "complex": "research_agent"
})
workflow.add_edge("research_agent", "code_writer")
workflow.add_edge("code_writer", "test_writer")
workflow.add_edge("test_writer", "sandbox")
workflow.add_conditional_edges("sandbox", route_by_test_result, {
    "pass": "pr_opener",
    "retry": "code_writer"
})
workflow.add_edge("pr_opener", END)

app = workflow.compile()

if __name__ == "__main__":
    real_input = fetch_github_issue_and_code(
        repo_name=REPO_NAME,
        issue_number=3,
        file_path="calculate.py"
    )
    result = app.invoke(real_input)
    print("\n=== FINAL RESULTS ===")
    print("Complexity:", result.get("complexity"))
    print("Tests passed:", result.get("test_passed"))
    print("PR URL:", result.get("pr_url", "No PR created"))