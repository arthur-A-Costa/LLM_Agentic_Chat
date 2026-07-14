from app.llms.ollama import get_llm
import psycopg
import os

DB_URL = os.getenv("DATABASE_URL", "postgresql://postgres_user:postgres_password@postgres:5432/postgres")

def get_chat_title(user_message: str) -> str:
    llm = get_llm()
    
    prompt = f"""
        Read the first query sent by the user and based on what is asked, requested and said 
        create a title that will be used as the title for the conversation/chat.

        Rules: 
        - The title must have a max of 10 words.
        - Make the title concise so the user can quickly recognize a conversation based on the title.
        - Make sure to include keywords of the query in the title that allow the user to easily recognize the theme of the conversation
            Examples:
            - Consortium
            - Selic Rate
            - Simulation
        - Output only the title.
        - Do not use quotation marks.
        - Do not end with punctuation.

        User Message:
        {user_message}
    """

    response = llm.invoke(prompt)

    if hasattr(response, "content"):
        title = response.content.strip()
    else:
        title = str(response).strip()

    return title

def update_title(conversation_id: str, title: str) -> None:
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE chat_conversations
                SET title = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE conversation_id = %s
                """,
                (title, conversation_id),
            )