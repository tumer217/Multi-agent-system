from github import Github
import os
import time
from dotenv import load_dotenv
load_dotenv()
class PROpenerAgent:
    def __init__(self):
        github_token = os.getenv("GITHUB_TOKEN")
        self.github = Github(github_token)
    def open_pr(self, repo_name, branch_name, file_path, file_content, commit_message, pr_title, pr_body):
        branch_name = f"{branch_name}-{int(time.time())}"
        repo = self.github.get_repo(repo_name)
        main_branch = repo.get_branch("main")
        repo.create_git_ref(ref=f"refs/heads/{branch_name}", sha=main_branch.commit.sha)
        repo.create_file(
            path=file_path,
            message=commit_message,
            content=file_content,
            branch=branch_name
        )
        pr = repo.create_pull(
            title=pr_title,
            body=pr_body,
            head=branch_name,
            base="main"
        )
        return pr.html_url
if __name__ == "__main__":
    agent = PROpenerAgent()
    pr_url = agent.open_pr(
        repo_name="tumer217/agent-test-repo",
        branch_name="agent-test-branch",
        file_path="fixed_code.py",
        file_content="# This file was created automatically by an AI agent\nprint('Hello from the agent!')",
        commit_message="Add fixed code via AI agent",
        pr_title="Automated fix from Code Writer Agent",
        pr_body="This PR was opened automatically by the PR Opener agent as part of the multi-agent pipeline."
    )
    print(f"Pull request created: {pr_url}")