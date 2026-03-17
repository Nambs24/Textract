from langgraph.graph import StateGraph, END

from state import AgentState

from nodes.brain import run as brain
from nodes.ingest import run as ingest
from nodes.retrieve import run as retrieve
from nodes.respond import run as respond


def build_graph():

    graph = StateGraph(AgentState)

    # ---------------- NODES ----------------
    graph.add_node("brain", brain)
    graph.add_node("ingest", ingest)
    graph.add_node("retrieve", retrieve)
    graph.add_node("respond", respond)

    # ---------------- ENTRY ----------------
    graph.set_entry_point("brain")

    # ---------------- ROUTER ----------------
    def router(state: AgentState):
        return state.route

    graph.add_conditional_edges(
        "brain",
        router,
        {
            "ingest": "ingest",
            "retrieve": "retrieve",
            "respond": "respond",
        },
    )

    # ---------------- FLOW ----------------
    graph.add_edge("ingest", "retrieve")
    graph.add_edge("retrieve", "respond")

    # ✅ STOP AFTER RESPONSE
    graph.add_edge("respond", END)

    return graph.compile()