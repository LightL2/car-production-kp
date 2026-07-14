# -*- coding: utf-8 -*-
"""Build split photo/video KPs and publish standalone GitHub Pages repos."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
DEPLOY = ROOT / "split-kp" / "deploy"
REPOS = (
    ("photo", DEPLOY / "photo", "car-production-kp-photo", "Car Production KP — Photo"),
    ("video", DEPLOY / "video", "car-production-kp-video", "Car Production KP — Video"),
)
GITIGNORE = """__pycache__/
*.pyc
.DS_Store
Thumbs.db
"""


def run_build():
    subprocess.run([sys.executable, str(ROOT / "build_split_presentations.py")], check=True, cwd=ROOT)


def ensure_gitignore(folder: Path):
    path = folder / ".gitignore"
    if not path.exists():
        path.write_text(GITIGNORE, encoding="utf-8")


def git(cmd: list[str], cwd: Path):
    sd = str(cwd.resolve()).replace("\\", "/")
    full = ["git", f"-c", f"safe.directory={sd}"] + cmd
    subprocess.run(full, check=True, cwd=cwd)



def publish_repo(mode: str, folder: Path, repo_name: str, title: str):
    if not (folder / "index.html").exists():
        raise SystemExit(f"Missing deploy package: {folder / 'index.html'}")

    ensure_gitignore(folder)
    remote = f"https://github.com/LightL2/{repo_name}.git"

    if not (folder / ".git").exists():
        git(["init"], folder)
        git(["branch", "-M", "main"], folder)

    git(["add", "-A"], folder)
    status = subprocess.run(
        ["git", "-c", f"safe.directory={str(folder.resolve()).replace(chr(92), '/')}", "status", "--porcelain"],
        capture_output=True,
        text=True,
        cwd=folder,
    )
    if status.stdout.strip():
        git(["commit", "-m", f"Deploy {mode} KP presentation for GitHub Pages."], folder)
    else:
        print(f"{repo_name}: no changes to commit")

    result = subprocess.run(
        ["gh", "repo", "view", f"LightL2/{repo_name}"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        subprocess.run(
            ["gh", "repo", "create", f"LightL2/{repo_name}", "--public", "--description", title, "--confirm"],
            check=True,
        )
        try:
            git(["remote", "remove", "origin"], folder)
        except subprocess.CalledProcessError:
            pass
        git(["remote", "add", "origin", remote], folder)
        git(["push", "-u", "origin", "main"], folder)
        print(f"Created and pushed: https://github.com/LightL2/{repo_name}")
    else:
        try:
            git(["remote", "get-url", "origin"], folder)
        except subprocess.CalledProcessError:
            git(["remote", "add", "origin", remote], folder)
        git(["push", "-u", "origin", "main"], folder)
        print(f"Pushed: https://github.com/LightL2/{repo_name}")

    pages = subprocess.run(
        ["gh", "api", f"repos/LightL2/{repo_name}/pages", "-X", "POST", "-f", "build_type=legacy", "-f", "source[branch]=main", "-f", "source[path]=/"],
        capture_output=True,
        text=True,
    )
    if pages.returncode == 0:
        print(f"GitHub Pages enabled: https://lightl2.github.io/{repo_name}/")
    elif "already exists" in (pages.stderr or pages.stdout or "").lower():
        print(f"GitHub Pages already configured: https://lightl2.github.io/{repo_name}/")
    else:
        print(f"Pages setup note ({repo_name}): enable legacy Pages from branch main / root in repo settings.")


def main():
    run_build()
    for mode, folder, repo_name, title in REPOS:
        print(f"\n=== {mode.upper()} ===")
        publish_repo(mode, folder, repo_name, title)


if __name__ == "__main__":
    main()
