from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class AgentState(BaseModel):
    """
    Global shared state that travels across all LangGraph nodes.
    Designed specifically for Textract's 2-mode architecture.
    """

    # --------------------------------------------------
    # USER INPUT
    # --------------------------------------------------
    user_input: str = ""
    turn: int = 0

    # --------------------------------------------------
    # INTENT
    # --------------------------------------------------
    intent: str = ""
    # values → professional_query | ingest_github | ingest_resume | general

    route: Optional[str] = None  # next node router

    # --------------------------------------------------
    # TARGET PERSON
    # --------------------------------------------------
    person: Optional[str] = None
    github_username: Optional[str] = None
    is_new_username: bool = False
    is_known_user: bool = False
    should_ingest: bool = False

    # --------------------------------------------------
    # QUERY UNDERSTANDING
    # --------------------------------------------------
    user_query: Optional[str] = None
    needs_web_search: bool = False

    # --------------------------------------------------
    # RETRIEVAL
    # --------------------------------------------------
    retrieved_docs: List[str] = Field(default_factory=list)
    context: Optional[str] = None

    # --------------------------------------------------
    # RESPONSE
    # --------------------------------------------------
    final_answer: str = ""

    # --------------------------------------------------
    # VECTOR DB METADATA
    # --------------------------------------------------
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # --------------------------------------------------
    # CONVERSATIONAL MEMORY
    # --------------------------------------------------
    chat_history: List[Dict[str, Optional[str]]] = Field(default_factory=list)

    last_person: Optional[str] = None
    # enables follow-ups like:
    # "What are his skills?"

    # --------------------------------------------------
    # ERROR
    # --------------------------------------------------
    error: Optional[str] = None

    # --------------------------------------------------
    # VALIDATORS
    # --------------------------------------------------
    @field_validator("chat_history", mode="before")
    @classmethod
    def clean_chat_history(cls, value):
        """
        Ensures chat_history never contains None values.
        This prevents LangGraph from crashing during state validation.
        """
        if not value:
            return []

        cleaned = []

        for item in value:
            if not isinstance(item, dict):
                continue

            role = item.get("role") or ""
            content = item.get("content") or ""

            cleaned.append(
                {
                    "role": str(role),
                    "content": str(content),
                }
            )

        return cleaned