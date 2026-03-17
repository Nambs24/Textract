import os
from dotenv import load_dotenv

from graph import build_graph
from state import AgentState
from db.vectorstore import init_db

# ---------------- LOAD ENV ----------------
load_dotenv()

# ---------------- INIT DB ----------------
init_db()

# ---------------- BUILD GRAPH ----------------
graph = build_graph()


# ---------------- STATE FACTORY ----------------
def create_initial_state() -> AgentState:
    return AgentState(
        turn=0,
        chat_history=[],
        final_answer="",
        context=None,
        error=None,
    )


# ---------------- AGENT EXECUTION FUNCTION ----------------
def run_agent(user_input: str, state: AgentState | None = None) -> AgentState:
    """
    Core reusable function for CLI, Streamlit, APIs, voice, etc.
    """

    if state is None:
        state = create_initial_state()

    state.user_input = user_input

    # Invoke LangGraph
    state = AgentState(**graph.invoke(state))

    # Store assistant reply in memory
    if state.final_answer:
        state.chat_history.append(
            {"role": "assistant", "content": state.final_answer}
        )

    return state


# ---------------- CLI LOOP ----------------
def run_cli():

    print("\n🤖 Textract — AI Professional Intelligence Agent")
    print("Ask me about any developer’s GitHub or resume")
    print("Type 'exit' to quit.\n")

    state = create_initial_state()

    while True:

        user_input = input("You: ")

        if user_input.lower() in [
            "exit", "quit", "thanks", "thank you", "bye",
            "that's all", "close", "stop"
        ]:
            print("👋 Goodbye, have a nice day ahead!")
            break

        state = run_agent(user_input, state)

        if state.error:
            print(f"\n⚠️ {state.error}\n")
            state.error = None
        else:
            print(f"\nAgent: {state.final_answer}\n")


# ---------------- MAIN ----------------
if __name__ == "__main__":
    run_cli()