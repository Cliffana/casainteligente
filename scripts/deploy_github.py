"""Upload entire project to GitHub via API (no git CLI needed)."""

import os
import base64
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
    parts = rel.parts
    for part in parts:
        if part in EXCLUDE_DIRS:
            return True
        if part.endswith(".pyc"):
            return True
    return False


def main():
    auth = Auth.Token(TOKEN)
    g = Github(auth=auth)
    user = g.get_user()

    # Create or get repo
    try:
        repo = user.get_repo(REPO_NAME)
        print(f"[OK] Repository '{REPO_NAME}' already exists")
    except GithubException:
        repo = user.create_repo(REPO_NAME, private=False)
        print(f"[OK] Repository '{REPO_NAME}' created")

    # Collect all files
    files = []
    for filepath in sorted(ROOT.rglob("*")):
        if filepath.is_file() and not should_exclude(filepath, ROOT):
            rel_path = str(filepath.relative_to(ROOT)).replace("\\", "/")
            files.append((rel_path, filepath))

    print(f"[INFO] Uploading {len(files)} files...")

    # Create blobs for all files
    blobs = []
    for rel_path, filepath in files:
        content = filepath.read_bytes()
        blob = repo.create_git_blob(base64.b64encode(content).decode(), "base64")
        blobs.append((rel_path, blob))
        print(f"  + {rel_path}")

    # Create tree
    tree_elements = [
        InputGitTreeElement(path=path, mode="100644", type="blob", sha=blob.sha)
        for path, blob in blobs
    ]
    tree = repo.create_git_tree(tree_elements)

    # Create commit
    try:
        parent_ref = repo.get_git_ref(f"heads/{BRANCH}")
        parent_commit = repo.get_git_commit(parent_ref.object.sha)
        commit = repo.create_git_commit(
            "Initial commit - Casa Inteligente PT site",
            tree,
            [parent_commit],
        )
        parent_ref.edit(commit.sha, force=False)
        print(f"[OK] Updated existing branch '{BRANCH}'")
    except GithubException:
        # No existing branch - create it
        commit = repo.create_git_commit(
            "Initial commit - Casa Inteligente PT site",
            tree,
            [],
        )
        ref = repo.create_git_ref(f"refs/heads/{BRANCH}", commit.sha)
        print(f"[OK] Created branch '{BRANCH}'")

    print(f"\n[DONE] Repository: https://github.com/{USERNAME}/{REPO_NAME}")


if __name__ == "__main__":
    main()
