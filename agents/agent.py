from langchain.agents import create_agent
from langchain.chat_models import init_chat_model

from models.model import search_model

_chat_model = init_chat_model(**search_model)

agent = create_agent(
    model=_chat_model,
    system_prompt="will handle it later",
)
