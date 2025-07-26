from langchain_core.messages import SystemMessage
from langchain_core.prompts import ChatPromptTemplate

from Dashboard.Agent.prompts import (
    expense_analyze_human_message_prompt,
    expense_analyze_system_message_prompt,
    info_extracting_human_message_prompt,
    info_extracting_system_message_prompt,
    category_mapping_human_message_prompt,
    category_mapping_system_message_prompt,
    summary_making_human_message_prompt,
    summary_making_system_message_prompt
)

info_extracting_prompt_template = ChatPromptTemplate([
    SystemMessage(info_extracting_system_message_prompt),
    ("human",info_extracting_human_message_prompt), # type: ignore
])

expense_analyze_prompt_template = ChatPromptTemplate([
    ("system",expense_analyze_system_message_prompt),
    ("human",expense_analyze_human_message_prompt), # type: ignore
])

category_mapping_prompt_template = ChatPromptTemplate([
    ("system",category_mapping_system_message_prompt),
    ("human",category_mapping_human_message_prompt) # type: ignore
])

summary_making_prompt_template = ChatPromptTemplate([
    ("system",summary_making_system_message_prompt),
    ("human",summary_making_human_message_prompt), # type: ignore
])