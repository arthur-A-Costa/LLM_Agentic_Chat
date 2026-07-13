import os
import psycopg
import uuid

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres_user:postgres_password@postgres:5432/postgres"
)

def create_conversation(conversation_id: str | None = None) -> str:
    conversation_id = conversation_id or str(uuid.uuid4())

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(""" 
                INSERT INTO chat_conversations (conversation_id)
                VALUES (%s)
                ON CONFLICT (conversation_id) DO NOTHING
            """,
            (conversation_id,),
            )

    return conversation_id

def save_message(conversation_id: str, role: str, content: str, agent: str | None = None) -> None:
    conversation_id = conversation_id or str(uuid.uuid4())

    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_messages (conversation_id, role, content, agent)
                VALUES (%s, %s, %s, %s)
            """,
            (conversation_id, role, content, agent)
            )

        with conn.cursor() as cur:
            cur.execute("""
                UPDATE chat_conversations
                SET updated_at = CURRENT_TIMESTAMP
                WHERE conversation_id = %s
            """,
            (conversation_id,)
            )

def load_messages(conversation_id: str) -> list[dict]:
    with psycopg.connect(DB_URL) as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT role, content, agent, created_at
                FROM chat_messages
                WHERE conversation_id = %s
                ORDER BY created_at ASC, message_id ASC
            """,
            (conversation_id,),
            )

            rows = cur.fetchall()
        
    return [
        {
            "role" : row[0],
            "content" : row[1],
            "agent" : row[2],
            "created_at" : row[3].isoformat(),
        } 
        for row in rows
    ]