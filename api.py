from fastapi import FastAPI
from main import run_agent, create_initial_state

app = FastAPI()

state = create_initial_state()


@app.post("/run")
def run(payload: dict):
    global state

    user_input = payload.get("query", "")

    state = run_agent(user_input, state)

    return {
        "response": state.final_answer
    }