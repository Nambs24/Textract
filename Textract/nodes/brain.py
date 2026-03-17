import re
from db.vectorstore import person_exists

KNOWN_SELF = ["siddharth", "nambiar", "nambs24"]


def extract_github_username(text: str):
    if not text:
        return None

    text = text.strip()

    match = re.search(r"github\.com/([A-Za-z0-9_-]+)", text, re.IGNORECASE)
    if match:
        return match.group(1)

    match = re.search(r"username\s+([A-Za-z0-9_-]{3,39})", text, re.IGNORECASE)
    if match:
        return match.group(1)

    words = text.split()

    for word in words:
        clean = re.sub(r"[^\w-]", "", word)

        if not clean:
            continue

        if clean.lower() in KNOWN_SELF:
            return "Nambs24"

        if 3 <= len(clean) <= 39 and re.match(r"^[A-Za-z][A-Za-z0-9-]*$", clean):
            return clean

    return None


def detect_person_name(text: str):
    if not text:
        return None

    text = text.lower()

    if any(name in text for name in KNOWN_SELF):
        return "Siddharth Nambiar"

    return None


def classify_intent(text: str):
    if not text:
        return "general"

    text = text.lower()

    if any(x in text for x in ["github", "repo", "repository", "project", "code"]):
        return "professional_query"

    if any(x in text for x in ["resume", "cv", ".pdf"]):
        return "resume"

    if any(x in text for x in ["who are you", "hi", "hello", "how are you"]):
        return "general"

    return "professional_query"


def run(state):

    state.user_query = state.user_input
    user_input = state.user_input or ""
    state.turn += 1

    if user_input.strip():
        state.chat_history.append({"role": "user", "content": user_input})

    state.intent = classify_intent(user_input)

    extracted_username = extract_github_username(user_input)

    state.is_new_username = False

    if extracted_username:
        if extracted_username != state.last_person:
            state.is_new_username = True

        state.github_username = extracted_username

    elif state.last_person:
        state.github_username = state.last_person

    person_name = detect_person_name(user_input)
    if person_name:
        state.person = person_name

    if state.intent == "general":
        state.route = "respond"
        return state

    if not state.github_username:
        state.route = "respond"
        return state

    # ⭐ KEY FIX
    if state.is_new_username:

        if person_exists(state.github_username):
            state.route = "retrieve"
        else:
            state.route = "ingest"

    else:
        state.route = "retrieve"

    state.last_person = state.github_username

    return state