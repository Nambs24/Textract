from db.vectorstore import similarity_search


def run(state):

    print("\n🔎 Retrieving relevant data...")

    # --------------------------------------------------
    # 🎯 TARGET USER
    # --------------------------------------------------

    github_username = state.github_username or state.last_person

    if not github_username:
        state.context = ""
        state.error = "No target GitHub user found for retrieval."
        state.route = "respond"
        return state

    # --------------------------------------------------
    # 🧠 USER QUERY
    # --------------------------------------------------

    query = state.user_input

    # --------------------------------------------------
    # 🔎 VECTOR SEARCH (FILTERED BY PRIMARY KEY)
    # --------------------------------------------------

    results = similarity_search(
        query=query,
        github_username=github_username,
        top_k=5,
    )

    if not results:
        print("⚠️ No relevant documents found.")

        state.context = ""
        state.route = "respond"
        return state

    print(f"✅ Retrieved {len(results)} relevant sections")

    # --------------------------------------------------
    # 🧱 BUILD HIGH-QUALITY LLM CONTEXT
    # --------------------------------------------------

    context_blocks = []
    collected_metadata = {}

    for content, metadata, score in results:

        block = f"""
CONTENT:
{content}

SOURCE: {metadata.get("source", "unknown")}
SIMILARITY: {round(score, 3)}
"""
        context_blocks.append(block)

        # keep last metadata snapshot (useful for resume/github detection)
        collected_metadata = metadata

    state.context = "\n\n---\n\n".join(context_blocks)

    # store for future features (citations / export / UI)
    state.retrieved_docs = [c for c, _, _ in results]
    state.metadata = collected_metadata

    # remember the person for follow-ups
    state.last_person = github_username

    # --------------------------------------------------
    # ➡️ NEXT NODE
    # --------------------------------------------------

    state.route = "respond"
    return state