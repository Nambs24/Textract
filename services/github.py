import os
import base64
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Authorization": f"token {GITHUB_TOKEN}" if GITHUB_TOKEN else "",
    "Accept": "application/vnd.github+json",
}


# --------------------------------------------------
# LOW LEVEL CALLS
# --------------------------------------------------

def _get(url: str):
    response = requests.get(url, headers=HEADERS, timeout=30)

    if response.status_code == 404:
        raise ValueError("GitHub user or resource not found.")

    if response.status_code == 403:
        raise ValueError("GitHub API rate limit exceeded.")

    response.raise_for_status()
    return response.json()


# --------------------------------------------------
# FETCH ALL REPOS (WITH PAGINATION)
# --------------------------------------------------

def fetch_repos(username: str):

    repos = []
    page = 1

    while True:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&page={page}"
        data = _get(url)

        if not data:
            break

        repos.extend(data)
        page += 1

    return repos


# --------------------------------------------------
# FETCH README
# --------------------------------------------------

def fetch_readme(owner: str, repo: str):

    url = f"https://api.github.com/repos/{owner}/{repo}/readme"

    try:
        data = _get(url)
        content = base64.b64decode(data["content"]).decode("utf-8", errors="ignore")
        return content

    except Exception:
        return ""


# --------------------------------------------------
# PARALLEL README FETCHER
# --------------------------------------------------

def fetch_all_readmes(username, repos):

    readmes = {}

    with ThreadPoolExecutor(max_workers=5) as executor:

        futures = {
            executor.submit(fetch_readme, username, repo["name"]): repo["name"]
            for repo in repos
        }

        for future in as_completed(futures):
            repo_name = futures[future]
            try:
                readmes[repo_name] = future.result()
            except Exception:
                readmes[repo_name] = ""

    return readmes


# --------------------------------------------------
# MAIN PUBLIC FUNCTION
# --------------------------------------------------

def fetch_github_data(username: str, repo_limit: int | None = None):

    print(f"🌐 Fetching GitHub data for {username}...")

    repos = fetch_repos(username)

    if repo_limit:
        repos = repos[:repo_limit]

    readme_map = fetch_all_readmes(username, repos)

    results = []

    for repo in repos:

        results.append(
            {
                "name": repo["name"],
                "description": repo["description"],
                "url": repo["html_url"],
                "stars": repo["stargazers_count"],
                "language": repo["language"],
                "topics": repo.get("topics", []),
                "readme": readme_map.get(repo["name"], ""),
            }
        )

    print(f"✅ Found {len(results)} repositories")

    return results