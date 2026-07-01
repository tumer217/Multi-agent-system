from github import Github
import os
from dotenv import load_dotenv
load_dotenv()
class ResearchAgent:
    def __init__(self):
        github_token = os.getenv("GITHUB_TOKEN")
        self.github = Github(github_token)
    def research(self, repo_name, code_review):
        repo = self.github.get_repo(repo_name)
        contents = repo.get_contents("")
        file_list = []
        while contents:
            file_item = contents.pop(0)
            if file_item.type == "dir":
                contents.extend(repo.get_contents(file_item.path))
            else:
                file_list.append(file_item.path)
        notes = "Other files found in the repository:\n" + "\n".join(file_list)
        return notes
if __name__ == "__main__":
    agent = ResearchAgent()
    notes = agent.research("tumer217/agent-test-repo", "calculate_total missing validation")
    print(notes)