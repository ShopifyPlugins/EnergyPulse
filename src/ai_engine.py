import logging

from openai import OpenAI

from src.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL, BUSINESS_NAME, MAX_HISTORY
from src import db
from src.knowledge_base import KnowledgeBase

logger = logging.getLogger(__name__)

SYSTEM_PROMPT_TEMPLATE = """You are a helpful customer service assistant for {business_name}.
{custom_instructions}

Answer customer questions based on the following knowledge base.
If the answer is not in the knowledge base, politely say you don't have that information and suggest typing /human to speak with a team member.

Be concise, friendly, and professional. Reply in the same language the customer uses.

{context}"""


class AIEngine:
    """LLM-powered response generation with RAG."""

    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base
        self.client = OpenAI(api_key=LLM_API_KEY, base_url=LLM_BASE_URL)

    def generate_reply(self, chat_id: int, user_message: str) -> str:
        relevant = self.kb.search(user_message)
        context = ""
        if relevant:
            context = "Knowledge base:\n" + "\n---\n".join(relevant)

        custom = db.get_setting("system_prompt", "")
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            business_name=BUSINESS_NAME,
            custom_instructions=f"\n{custom}\n" if custom else "",
            context=context,
        )

        history = db.get_history(chat_id, limit=MAX_HISTORY)
        messages = [{"role": "system", "content": system_prompt}]
        for msg in history:
            messages.append({"role": msg["role"], "content": msg["message"]})
        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=LLM_MODEL,
                messages=messages,
                max_tokens=1024,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error("LLM API error: %s", e)
            return (
                "I'm sorry, I'm having trouble processing your request right now. "
                "Please try again later or type /human to speak with a team member."
            )
