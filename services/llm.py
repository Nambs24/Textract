import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash")


SYSTEM_PROMPT = """
You are Textract — an AI professional intelligence agent.

Your personality:
- Speak like a friendly, sharp human analyst.
- Be natural and conversational, not robotic.
- Keep responses clear and structured when giving professional insights.

Your job:
- Help users explore professional profiles (GitHub, resumes, skills, experience).
- Extract meaningful insights, not just raw summaries.

Conversation rules:
- If context is provided → answer ONLY from it.
- If context is missing for a professional question → say you’ll fetch the data.
- If the user asks something unrelated → answer briefly, then politely guide them back to professional analysis.
- Handle follow-up questions naturally.

Style:
- Use light formatting for readability.
- Avoid long disclaimers.
- Be concise but insightful.
"""


model = genai.GenerativeModel(
    MODEL,
    system_instruction=SYSTEM_PROMPT,
)


# --------------------------------------------------
# MAIN GENERATION FUNCTION
# --------------------------------------------------
def generate_answer(
    prompt: str,
    chat_history: list | None = None,
) -> str:

    if not prompt:
        return "I’m not sure what to answer yet."

    try:
        contents = []

        # ✅ ADD CHAT HISTORY FOR MEMORY
        if chat_history:
            for msg in chat_history[-6:]:  # last few turns only
                role = "user" if msg["role"] == "user" else "model"
                contents.append(
                    {
                        "role": role,
                        "parts": [{"text": msg["content"]}],
                    }
                )

        # ✅ CURRENT PROMPT
        contents.append(
            {
                "role": "user",
                "parts": [{"text": prompt}],
            }
        )

        response = model.generate_content(
            contents,
            request_options={"timeout": 30},
        )

        # ✅ SAFE TEXT EXTRACTION
        if response.text:
            return response.text.strip()

        if response.candidates:
            parts = response.candidates[0].content.parts
            return "".join(
                p.text for p in parts if hasattr(p, "text")
            ).strip()

        return "I couldn’t generate a proper response."

    except Exception as e:
        return f"LLM error: {str(e)}"