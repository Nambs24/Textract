import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

from services.github import fetch_github_data
from services.embeddings import embed_texts
from db.vectorstore import init_db, upsert_profile
from utils.file_loader import load_file

PERSON_NAME = "Siddharth Nambiar"


# ---------------- GITHUB ----------------
def ingest_github(username: str):

    print(f"\n🔹 Preloading GitHub → {username}")

    repos = fetch_github_data(username)

    if not repos:
        print("❌ No repositories found.")
        return

    combined_content = ""

    for repo in repos:
        combined_content += f"""
        Repo: {repo['name']}
        Description: {repo['description']}
        README:
        {repo['readme']}
        URL: {repo['url']}
        """

    embedding = embed_texts([combined_content])[0]

    upsert_profile(
        github_username=username,
        person=PERSON_NAME,
        content=combined_content,
        embedding=embedding,
        github_repos=repos,
        source="github",
    )

    print("✅ GitHub profile stored.\n")


# ---------------- RESUME ----------------
def ingest_resume(username: str, file_path: str):

    file_path = file_path.strip('"')

    if not Path(file_path).exists():
        print("❌ File not found.")
        return

    print(f"\n🔹 Preloading resume → {file_path}")

    text = load_file(file_path)

    embedding = embed_texts([text])[0]

    upsert_profile(
        github_username=username,
        person=PERSON_NAME,
        content=text,
        embedding=embedding,
        resume=Path(file_path).name,
        source="resume",
    )

    print("✅ Resume stored.\n")


# ---------------- MAIN ----------------
def run_preload():

    init_db()

    print("\n🚀 PRELOAD MODE")
    print("1 → GitHub preload")
    print("2 → Resume preload\n")

    choice = input("Select option: ").strip()

    if choice == "1":
        username = input("Enter GitHub username: ").strip()
        ingest_github(username)

    elif choice == "2":
        username = input("Enter GitHub username for this resume: ").strip()
        file_path = input("Enter file path: ")
        ingest_resume(username, file_path)

    else:
        print("❌ Invalid choice.")


if __name__ == "__main__":
    run_preload()