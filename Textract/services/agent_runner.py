from graph import build_graph
from state import AgentState
from db.vectorstore import init_db


class AgentSession:
    def __init__(self):
        init_db()
        self.graph = build_graph()
        self.state = self._create_initial_state()

    def _create_initial_state(self):
        return AgentState(
            turn=0,
            chat_history=[],
            final_answer="",
            context=None,
            error=None,
        )

    # ---------------- ASK ----------------
    def ask(self, user_input: str):

        self.state.user_input = user_input
        self.state = AgentState(**self.graph.invoke(self.state))

        if self.state.error:
            response = f"⚠️ {self.state.error}"
            self.state.error = None
        else:
            response = self.state.final_answer

        self.state.chat_history.append(
            {"role": "assistant", "content": response}
        )

        return response

    # ---------------- INGEST GITHUB ----------------
    def ingest_github(self, username: str):
        return self.ask(username)

    # ---------------- INGEST RESUME ----------------
    def ingest_resume(self, file_path: str, username: str | None = None):

        if username:
            self.state.github_username = username

        return self.ask(file_path)

    # ---------------- RESET ----------------
    def reset(self):
        self.state = self._create_initial_state()