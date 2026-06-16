"""Supergit Git 작업 모듈 - GitPython 기반"""

import subprocess
import json
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple

try:
    import git
    from git import Repo, InvalidGitRepositoryError, GitCommandError
    GITPYTHON_OK = True
except ImportError:
    GITPYTHON_OK = False


def _run(cmd: List[str], cwd: str, timeout: int = 30) -> Tuple[str, str, int]:
    """서브프로세스 명령 실행. (stdout, stderr, returncode) 반환"""
    try:
        result = subprocess.run(
            cmd, cwd=cwd, capture_output=True, text=True,
            timeout=timeout, encoding="utf-8", errors="replace"
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "Timeout", -1
    except FileNotFoundError:
        return "", f"Command not found: {cmd[0]}", -1
    except Exception as e:
        return "", str(e), -1


class GitOps:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self._repo: Optional[Any] = None
        if GITPYTHON_OK:
            try:
                self._repo = Repo(repo_path)
            except Exception:
                self._repo = None

    @staticmethod
    def is_git_repo(path: str) -> bool:
        try:
            Repo(path)
            return True
        except Exception:
            return False

    # ── Status ────────────────────────────────────────────────────────────────

    def status(self) -> Dict[str, Any]:
        """현재 저장소 상태 반환"""
        if self._repo is None:
            return {"error": "Not a git repo"}
        try:
            repo = self._repo
            staged = []
            unstaged = []
            untracked = []

            for item in repo.index.diff("HEAD"):
                staged.append({
                    "path": item.a_path or item.b_path,
                    "change_type": item.change_type,
                })
            # 새 파일 (스테이징된)
            for item in repo.index.diff(None):
                unstaged.append({
                    "path": item.a_path or item.b_path,
                    "change_type": item.change_type,
                })
            untracked = repo.untracked_files

            try:
                current = repo.active_branch.name
            except TypeError:
                current = "HEAD (detached)"

            ahead, behind = 0, 0
            try:
                tracking = repo.active_branch.tracking_branch()
                if tracking:
                    ahead_commits = list(repo.iter_commits(f"{tracking}..HEAD"))
                    behind_commits = list(repo.iter_commits(f"HEAD..{tracking}"))
                    ahead = len(ahead_commits)
                    behind = len(behind_commits)
            except Exception:
                pass

            return {
                "current": current,
                "staged": staged,
                "unstaged": unstaged,
                "untracked": untracked,
                "ahead": ahead,
                "behind": behind,
            }
        except Exception as e:
            return {"error": str(e)}

    # ── Staging ───────────────────────────────────────────────────────────────

    def stage_file(self, filepath: str) -> Tuple[bool, str]:
        out, err, code = _run(["git", "add", filepath], self.repo_path)
        return code == 0, err or out

    def unstage_file(self, filepath: str) -> Tuple[bool, str]:
        out, err, code = _run(["git", "restore", "--staged", filepath], self.repo_path)
        return code == 0, err or out

    def stage_all(self) -> Tuple[bool, str]:
        out, err, code = _run(["git", "add", "-A"], self.repo_path)
        return code == 0, err or out

    def unstage_all(self) -> Tuple[bool, str]:
        out, err, code = _run(["git", "restore", "--staged", "."], self.repo_path)
        return code == 0, err or out

    # ── Commit ────────────────────────────────────────────────────────────────

    def commit(self, message: str) -> Tuple[bool, str]:
        out, err, code = _run(["git", "commit", "-m", message], self.repo_path)
        return code == 0, out or err

    # ── Push / Pull / Fetch ───────────────────────────────────────────────────

    def push(self) -> Tuple[bool, str]:
        out, err, code = _run(["git", "push"], self.repo_path, timeout=60)
        return code == 0, out + err

    def pull(self) -> Tuple[bool, str]:
        out, err, code = _run(["git", "pull"], self.repo_path, timeout=60)
        return code == 0, out + err

    def fetch(self) -> Tuple[bool, str]:
        out, err, code = _run(["git", "fetch", "--all"], self.repo_path, timeout=60)
        return code == 0, out + err

    # ── Branches ──────────────────────────────────────────────────────────────

    def branches(self) -> Dict[str, Any]:
        try:
            repo = self._repo
            if repo is None:
                return {"error": "Not a git repo"}

            try:
                current = repo.active_branch.name
            except TypeError:
                current = "(detached HEAD)"

            local = [b.name for b in repo.branches]
            remote = []
            for ref in repo.remotes:
                for r in ref.refs:
                    name = r.name
                    if "HEAD" not in name:
                        remote.append(name)
            return {"current": current, "local": local, "remote": remote}
        except Exception as e:
            return {"error": str(e)}

    def checkout(self, branch: str) -> Tuple[bool, str]:
        out, err, code = _run(["git", "checkout", branch], self.repo_path)
        if self._repo:
            try:
                self._repo = Repo(self.repo_path)
            except Exception:
                pass
        return code == 0, out + err

    def create_branch(self, name: str, checkout: bool = True) -> Tuple[bool, str]:
        cmd = ["git", "checkout", "-b", name] if checkout else ["git", "branch", name]
        out, err, code = _run(cmd, self.repo_path)
        if self._repo:
            try:
                self._repo = Repo(self.repo_path)
            except Exception:
                pass
        return code == 0, out + err

    def delete_branch(self, name: str) -> Tuple[bool, str]:
        out, err, code = _run(["git", "branch", "-d", name], self.repo_path)
        return code == 0, out + err

    # ── Log ───────────────────────────────────────────────────────────────────

    def log(self, max_count: int = 100) -> List[Dict[str, str]]:
        fmt = "%H||%h||%an||%ae||%ad||%s"
        out, err, code = _run(
            ["git", "log", f"--max-count={max_count}", f"--format={fmt}", "--date=short"],
            self.repo_path
        )
        if code != 0:
            return []
        commits = []
        for line in out.strip().splitlines():
            parts = line.split("||")
            if len(parts) == 6:
                commits.append({
                    "hash": parts[0],
                    "short_hash": parts[1],
                    "author": parts[2],
                    "email": parts[3],
                    "date": parts[4],
                    "message": parts[5],
                })
        return commits

    def cherry_pick(self, commit_hash: str) -> Tuple[bool, str]:
        out, err, code = _run(["git", "cherry-pick", commit_hash], self.repo_path)
        return code == 0, out + err

    # ── Diff ──────────────────────────────────────────────────────────────────

    def diff_file(self, filepath: str) -> str:
        out, err, _ = _run(["git", "diff", "HEAD", "--", filepath], self.repo_path)
        return out or err

    def diff_staged(self, filepath: str) -> str:
        out, err, _ = _run(["git", "diff", "--cached", "--", filepath], self.repo_path)
        return out or err

    # ── Terminal ──────────────────────────────────────────────────────────────

    def run_command(self, command: str) -> Tuple[str, bool]:
        """쉘 명령어 실행 (터미널 탭용)"""
        try:
            result = subprocess.run(
                command, cwd=self.repo_path, shell=True,
                capture_output=True, text=True,
                timeout=30, encoding="utf-8", errors="replace"
            )
            output = ""
            if result.stdout:
                output += result.stdout
            if result.stderr:
                output += result.stderr
            return output or "(명령 완료, 출력 없음)", result.returncode == 0
        except subprocess.TimeoutExpired:
            return "타임아웃 (30초)", False
        except Exception as e:
            return str(e), False


# ── GitHub CLI ────────────────────────────────────────────────────────────────

def gh_installed() -> bool:
    out, err, code = _run(["gh", "--version"], ".")
    return code == 0


def gh_create_pr(repo_path: str, title: str, body: str, base: str, head: str) -> Tuple[bool, str]:
    out, err, code = _run(
        ["gh", "pr", "create", "--title", title, "--body", body, "--base", base, "--head", head],
        repo_path, timeout=30
    )
    return code == 0, out + err


def gh_list_prs(repo_path: str) -> Tuple[bool, Any]:
    out, err, code = _run(
        ["gh", "pr", "list", "--json", "number,title,state,author,createdAt"],
        repo_path, timeout=20
    )
    if code == 0:
        try:
            return True, json.loads(out)
        except Exception:
            return False, out + err
    return False, err
