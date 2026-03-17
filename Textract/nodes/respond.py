from services.llm import generate_answer


# --------------------------------------------------
# PROMPT BUILDER
# --------------------------------------------------
def build_prompt(query, context, person):

    return f"""
    You are Textract — a warm, intelligent AI assistant that talks like a real human.

    Your purpose:
    Help users with professional insights about people
    (GitHub, projects, skills, experience, resumes).

    STYLE:
    - Natural and conversational
    - Clear and structured
    - Friendly and professional
    - Not robotic

    RULES:
    - Use the provided context as the primary source
    - If the user asks something unrelated, answer briefly and gently guide them back
    - If the user asks a follow-up (e.g., "What tech stack does he use?"), assume it refers to the same person
    - Never mention the word "context"

    Person: {person}

    Context:
    {context}

    User question:
    {query}
    """


# --------------------------------------------------
# GENERAL CHAT (NO CONTEXT)
# --------------------------------------------------
def build_general_prompt(query):

    return f"""
    You are Textract — a friendly AI that specialises in analysing
    people’s professional profiles.

    The user asked something unrelated to that.

    Reply naturally and briefly,
    then guide the conversation back to your main capability.

    User message:
    {query}
    """


# --------------------------------------------------
# NODE
# --------------------------------------------------
def run(state):

    print("\n💬 Thinking...")

    query = state.user_query

    # --------------------------------------------------
    # 🧠 HANDLE ERRORS FIRST
    # --------------------------------------------------
    if state.error:
        state.final_answer = f"⚠️ {state.error}"
        state.error = None

        # ✅ STORE CHAT HISTORY
        state.chat_history.append({"role": "user", "content": query})
        state.chat_history.append({"role": "assistant", "content": state.final_answer})

        state.route = "brain"
        return state

    # --------------------------------------------------
    # 🧠 FOLLOW-UP MEMORY SUPPORT
    # --------------------------------------------------
    person = state.person or state.last_person or "this person"

    # --------------------------------------------------
    # 🚫 NO DATA AVAILABLE → GENERAL CHAT
    # --------------------------------------------------
    if not state.context:

        prompt = build_general_prompt(query)

        answer = generate_answer(
            prompt,
            chat_history=state.chat_history
        )

        state.final_answer = answer

        # ✅ STORE CHAT HISTORY
        state.chat_history.append({"role": "user", "content": query})
        state.chat_history.append({"role": "assistant", "content": answer})

        state.route = "brain"
        return state

    # --------------------------------------------------
    # ✅ PROFESSIONAL QA FROM RAG
    # --------------------------------------------------
    prompt = build_prompt(query, state.context, person)

    answer = generate_answer(
        prompt,
        chat_history=state.chat_history
    )

    state.final_answer = answer

    # ✅ STORE CHAT HISTORY
    state.chat_history.append({"role": "user", "content": query})
    state.chat_history.append({"role": "assistant", "content": answer})

    # clear context for next turn
    state.context = None

    state.route = "brain"
    return state