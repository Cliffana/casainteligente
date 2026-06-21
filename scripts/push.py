"""Push local changes to GitHub via API."""
import os, base64
from pathlib import Path
from github import Github, InputGitTreeElement, Auth

ROOT = Path(__file__).resolve().parent.parent
TOKEN = os.environ.get("GH_TOKEN", "")
REPO_NAME = "Cliffana/casainteligente"
BRANCH = "main"

EXCLUDE_DIRS = {"__pycache__", ".git", ".venv", "venv", "output"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}
EXCLUDE_PREFIXES = {"."}

def should_include(path):
    rel = path.relative_to(ROOT)
    parts = list(rel.parts)
    for p in parts:
        if p in EXCLUDE_DIRS: return False
        if p.startswith(".") and p not in (".github", ".gitignore"): return False
    if path.suffix in EXCLUDE_SUFFIXES: return False
    return True

def push():
    auth = Auth.Token(TOKEN)
    g = Github(auth=auth)
    repo = g.get_repo(REPO_NAME)

    try:
        ref = repo.get_git_ref(f"heads/{BRANCH}")
        latest_commit = repo.get_git_commit(ref.object.sha)
        base_tree = repo.get_git_tree(latest_commit.tree.sha, recursive=True)
        parent = latest_commit
    except:
        base_tree = None
        parent = None

    blobs = []
    files = []
    for fp in sorted(ROOT.rglob("*")):
        if fp.is_file() and should_include(fp):
            files.append(fp)

    for fp in files:
        rel = str(fp.relative_to(ROOT)).replace("\\", "/")
        raw = fp.read_bytes()
        try:
            content = raw.decode("utf-8")
            enc = "utf-8"
        except:
            content = base64.b64encode(raw).decode("ascii")
            enc = "base64"
        blob = repo.create_git_blob(content, enc)
        blobs.append(InputGitTreeElement(path=rel, mode="100644", type="blob", sha=blob.sha))

    new_tree = repo.create_git_tree(blobs, base_tree=base_tree)
    parents = [parent] if parent else []
    commit = repo.create_git_commit(
        message="Multi-language site: pt+es+fr+en, GoatCounter tracking, template content",
        tree=new_tree, parents=parents)
    ref.edit(commit.sha)
    print(f"Pushed {len(files)} files to {REPO_NAME}:{BRANCH} ({commit.sha[:8]})")

if __name__ == "__main__":
    push()
