from services.github import fetch_github_data
from services.websearch import find_github_username
from services.embeddings import embed_text
from db.vectorstore import upsert_profile


def build_github_profile(repos):

    blocks = []

    for repo in repos:
        block = f"""
Repo: {repo['name']}
Description: {repo['description']}
README:
{repo['readme']}
URL: {repo['url']}
"""
        blocks.append(block)

    return "\n\n".join(blocks)


def run(state):

    print("\n⚙️ Ingesting data...")

    try:

        # ===============================
        # USE DIRECT USERNAME IF PRESENT
        # ===============================
        if state.github_username:
            username = state.github_username

        # fallback → person name → websearch
        elif state.person:
            username = find_github_username(state.person)

        else:
            raise ValueError("No GitHub identity found.")

        print(f"🌐 Fetching GitHub data for {username}...")

        repos = fetch_github_data(username)

        if not repos:
            raise ValueError("No repositories found for this user.")

        content = build_github_profile(repos)

        embedding = embed_text(content)

        upsert_profile(
            github_username=username,
            person=state.person,
            content=content,
            embedding=embedding,
            github_repos=repos,
            source="github_live",
        )

        print("✅ Profile stored in vector DB")

        state.github_username = username
        state.last_person = username
        state.route = "retrieve"
        return state

    except Exception as e:
        state.error = str(e)
        state.route = "respond"
        return state