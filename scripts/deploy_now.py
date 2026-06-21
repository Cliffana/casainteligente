"""Push redesign to GitHub."""
import os, base64, requests, json, sys
from pathlib import Path

TOKEN = os.environ.get("GH_TOKEN", "")
if not TOKEN:
    print("Set GH_TOKEN env var")
    sys.exit(1)

HEADERS = {"Authorization": f"Bearer {TOKEN}", "Accept": "application/vnd.github.v3+json"}
API = "https://api.github.com/repos/Cliffana/casainteligente"
ROOT = Path(__file__).resolve().parent.parent
EXCLUDE = {"__pycache__", ".git", ".venv", "venv", "output"}
EXCLUDE_SUFFIXES = {".pyc", ".pyo"}

def include(fp):
    for p in fp.relative_to(ROOT).parts:
        if p in EXCLUDE: return False
        if p.startswith(".") and p not in (".github", ".gitignore"): return False
    return fp.suffix not in EXCLUDE_SUFFIXES

ref = requests.get(f"{API}/git/ref/heads/main", headers=HEADERS).json()
base_commit = requests.get(ref["object"]["url"], headers=HEADERS).json()
base_tree_sha = base_commit["tree"]["sha"]
print(f"Base tree: {base_tree_sha[:8]}")

files = sorted(f for f in ROOT.rglob("*") if f.is_file() and include(f))
tree_items = []
for i, fp in enumerate(files):
    rel = str(fp.relative_to(ROOT)).replace("\\", "/")
    raw = fp.read_bytes()
    try:
        content = raw.decode("utf-8")
        enc = "utf-8"
    except:
        content = base64.b64encode(raw).decode("ascii")
        enc = "base64"
    blob = requests.post(f"{API}/git/blobs", headers=HEADERS, json={"content": content, "encoding": enc}).json()
    tree_items.append({"path": rel, "mode": "100644", "type": "blob", "sha": blob["sha"]})

tree = requests.post(f"{API}/git/trees", headers=HEADERS, json={"base_tree": base_tree_sha, "tree": tree_items}).json()
print(f"Tree: {tree['sha'][:8]}")

commit = requests.post(f"{API}/git/commits", headers=HEADERS, json={
    "message": "Redesign: warm palette, DM Serif + Inter fonts, cleaner layout",
    "tree": tree["sha"],
    "parents": [base_commit["sha"]],
}).json()
print(f"Commit: {commit['sha'][:8]}")

r = requests.patch(f"{API}/git/refs/heads/main", headers=HEADERS, json={"sha": commit["sha"], "force": True})
if r.ok:
    print(f"Pushed {len(files)} files to main")
else:
    print(f"Push failed: {r.status_code} {r.text}")
