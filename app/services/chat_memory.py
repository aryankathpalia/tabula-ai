# app/services/chat_memory.py

from collections import defaultdict, deque

MAX_HISTORY = 6

# conversation_id -> message history
memory_store = defaultdict(lambda: deque(maxlen=MAX_HISTORY))


def add_message(conversation_id: str, role: str, content: str):
    memory_store[conversation_id].append({
        "role": role,
        "content": content
    })


def get_history(conversation_id: str):

    history = memory_store.get(conversation_id, [])

    formatted = ""

    for msg in history:
        role = msg["role"].capitalize()
        formatted += f"{role}: {msg['content']}\n"

    return formatted