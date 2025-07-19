from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from Dashboard.Agent.prompts import (
    expense_analyze_human_message_prompt,
    expense_analyze_system_message_prompt,
    info_extracting_human_message_prompt,
    info_extracting_system_message_prompt,
)

info_extracting_prompt_template = ChatPromptTemplate([
    SystemMessage(info_extracting_system_message_prompt),
    ("human",info_extracting_human_message_prompt), # type: ignore
])

expense_analyze_prompt_template = ChatPromptTemplate([
    ("system",expense_analyze_system_message_prompt),
    ("human",expense_analyze_human_message_prompt), # type: ignore
])