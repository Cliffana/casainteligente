import os, base64
from pathlib import Path
from github import Github, GithubException, Auth
from github.InputGitTreeElement import InputGitTreeElement

ROOT = Path(__file__).resolve().parent.parent
REPO_NAME = "casainteligente"
BRANCH = "main"
EXCLUDE_DIRS = {"output", "__pycache__", ".git"}
TOKEN = os.environ.get("GH_TOKEN", "")

def should_exclude(path, root):
    rel = path.relative_to(root)
    for part in rel.parts:
        if part in EXCLUDE_DIRS or part.endswith(".pyc"):
            return True
    return False

def main():
    g = Github(auth=Auth.Token(TOKEN))
    user = g.get_user()
    try:
        repo = user.get_repo(REPO_NAME)
    except GithubException:
        repo = user.create_repo(REPO_NAME, private=False)
    files = []
    for fp in sorted(ROOT.rglob("*")):
        if fp.is_file() and not should_exclude(fp, ROOT):
            files.append((str(fp.relative_to(ROOT)).replace("\\", "/"), fp))
    blobs = []
    for rel_path, filepath in files:
        content = filepath.read_bytes()
        blob = repo.create_git_blob(base64.b64encode(content).decode(), "base64")
        blobs.append((rel_path, blob))
    tree_elements = [InputGitTreeElement(path=p, mode="100644", type="blob", sha=b.sha) for p, b in blobs]
    tree = repo.create_git_tree(tree_elements)
    try:
        parent_ref = repo.get_git_ref(f"heads/{BRANCH}")
        parent_commit = repo.get_git_commit(parent_ref.object.sha)
        commit = repo.create_git_commit("Redesign: modern UI with vibrant colors", tree, [parent_commit])
        parent_ref.edit(commit.sha, force=False)
    except GithubException:
        commit = repo.create_git_commit("Redesign: modern UI with vibrant colors", tree, [])
        repo.create_git_ref(f"refs/heads/{BRANCH}", commit.sha)
    print(f"DONE: https://github.com/{user.login}/{REPO_NAME}")

if __name__ == "__main__":
    main()
