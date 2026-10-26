"""
version.py — Release and Versioning tied to GitHub Releases & Git Metadata
"""
import os
import time
import subprocess
import logging
from typing import Any
import httpx

logger = logging.getLogger(__name__)

GITHUB_REPO = os.getenv("GITHUB_REPO", "rbaronia/synology-geek-dashboard")
DEFAULT_VERSION = os.getenv("DASHBOARD_VERSION", "v1.2.0")
DEFAULT_RELEASE = os.getenv("DASHBOARD_RELEASE", "2026.10-LTS")
DEFAULT_CHANNEL = os.getenv("DASHBOARD_CHANNEL", "STABLE")


def get_git_commit() -> str:
    """Attempt to get short git commit hash from local repo or environment."""
    env_commit = os.getenv("GIT_COMMIT")
    if env_commit:
        return env_commit[:7]
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            timeout=1.5,
        ).decode().strip()
        if commit:
            return commit
    except Exception:
        pass
    return os.getenv("DASHBOARD_BUILD", "721c444")


# In-memory GitHub release cache (15 minute TTL)
_release_cache: dict[str, Any] = {}
_cache_timestamp: float = 0.0
CACHE_TTL = 900  # 15 minutes


def get_static_meta() -> dict[str, Any]:
    """Return synchronous metadata for initial Jinja template rendering."""
    commit = get_git_commit()
    version = DEFAULT_VERSION if DEFAULT_VERSION.startswith("v") else f"v{DEFAULT_VERSION}"
    return {
        "version": version,
        "release": DEFAULT_RELEASE,
        "build": commit,
        "channel": DEFAULT_CHANNEL,
        "repo": GITHUB_REPO,
        "repo_url": f"https://github.com/{GITHUB_REPO}",
        "releases_url": f"https://github.com/{GITHUB_REPO}/releases",
        "latest_release_url": f"https://github.com/{GITHUB_REPO}/releases/latest",
        "latest_tag": version,
        "update_available": False,
    }


async def fetch_github_release_info() -> dict[str, Any]:
    """
    Fetch the latest release information from GitHub API.
    Caches results for 15 minutes to respect GitHub API rate limits.
    """
    global _release_cache, _cache_timestamp
    now = time.time()

    if _release_cache and (now - _cache_timestamp < CACHE_TTL):
        return _release_cache

    meta = get_static_meta()
    api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    headers = {
        "User-Agent": "SynologyGeekDashboard/1.0",
        "Accept": "application/vnd.github.v3+json",
    }

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            resp = await client.get(api_url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                latest_tag = data.get("tag_name", meta["version"])
                clean_latest = latest_tag.lstrip("v")
                clean_current = meta["version"].lstrip("v")

                meta["latest_tag"] = latest_tag
                meta["release_name"] = data.get("name") or latest_tag
                meta["latest_release_url"] = data.get("html_url") or meta["latest_release_url"]
                meta["published_at"] = data.get("published_at")
                meta["update_available"] = clean_latest != clean_current
            elif resp.status_code == 404:
                # No release published on GitHub yet
                meta["release_name"] = f"Development Build ({meta['version']})"
    except Exception as exc:
        logger.debug(f"GitHub release check skipped/failed: {exc}")

    _release_cache = meta
    _cache_timestamp = now
    return _release_cache
