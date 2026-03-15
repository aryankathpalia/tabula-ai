from groq import Groq
from app.core.config import settings

client = Groq(api_key=settings.GROQ_API_KEY)


def generate_answer(query: str, context: str, history: str = ""):

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
         {
            "role": "system",
            "content": (
                "You are an AI assistant specialized in analyzing legal contracts. "
                "Your job is to help users understand the document excerpts provided. "

                "You should answer questions about the document using the excerpts. "
                "If the user asks follow-up questions, clarifications, or asks you to explain something again, "
                "you should respond conversationally and helpfully based on the previous discussion and document excerpts. "

                "If the user asks something like 'what?', 'explain again', or 'I didn't understand', "
                "you should clarify your previous answer in simpler terms. "

                "Only say 'The document does not contain enough information' if the answer truly cannot be found "
                "in the provided document excerpts."
            )
        },
            {
                "role": "user",
                "content": f"""
Coversation so far:
{history}
                
Document excerpts:
{context}

Question:
{query}
"""
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content