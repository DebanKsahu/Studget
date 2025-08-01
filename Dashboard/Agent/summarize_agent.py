import json
from collections import defaultdict
from typing import List

from pydantic import BaseModel, Field
from langgraph.graph import StateGraph, START, END
from Dashboard.Agent.prompt_templates import (
    category_mapping_prompt_template,
    summary_making_prompt_template,
)
from Database.Models.graph_states import (
    FinalOutputState,
    SummarizeAgentInputState,
    SummarizeAgentIntermediateState,
    SummarizeAgentOutputState,
    SummarizeAgentOverallState,
)
from Utils.enum import TrendIndicator
from Utils.llm import gemini_llm
from Utils.utility_functions import UtilsContainer


class OutputFormatter(BaseModel):
    """
    Output format for extracted categories from transaction descriptions.
    """
    categories: List[str] = Field(description="""List of extracted category names.""")


def default_value():
    return {
        "previous_month_spending": 0.0,
        "previous_to_previous_month_spending": 0.0,
        "absolute_change": 0.0,
        "percentage_change": 0.0,
        "trend_indicator": None,
        "significance_flag": False,
        "transaction_count_previous_month": 0,
        "transaction_count_previous_to_previous_month": 0
    }

async def category_mapping(state: SummarizeAgentInputState) -> SummarizeAgentIntermediateState:
    gemini_llm_with_structured_output = gemini_llm.with_structured_output(OutputFormatter)
    category_mapping_chain = ( category_mapping_prompt_template | gemini_llm_with_structured_output )
    month_1_categories = None
    month_2_categories = None
    if state.month1_transactions is not None:
        llm_response = await category_mapping_chain.ainvoke(
            {
                "transaction_data": UtilsContainer.data_formatting_utils.extract_transaction_description(state.month1_transactions)
            }
        )
        month_1_categories = OutputFormatter.model_validate(llm_response)
    if state.month2_transactions is not None:
        llm_response = await category_mapping_chain.ainvoke(
            {
                "transaction_data": UtilsContainer.data_formatting_utils.extract_transaction_description(state.month2_transactions)
            }
        )
        month_2_categories = OutputFormatter.model_validate(llm_response)

    final_transaction_report = defaultdict(lambda : default_value())
    if state.month1_transactions is not None and month_1_categories is not None and month_2_categories is not None:
        for index in range(len(state.month1_transactions)):
            final_transaction_report[month_1_categories.categories[index]]["previous_to_previous_month_spending"]+=state.month1_transactions[index].transaction_amount
            final_transaction_report[month_1_categories.categories[index]]["transaction_count_previous_to_previous_month"]+=1
            final_transaction_report[month_2_categories.categories[index]]["trend_indicator"] = TrendIndicator.STOP
            final_transaction_report[month_2_categories.categories[index]]["percentage_change"] = -100
    if state.month2_transactions is not None and month_2_categories is not None:
        if month_1_categories is None:
            month_1_categories = month_2_categories
        for index in range(len(state.month2_transactions)):
            final_transaction_report[month_2_categories.categories[index]]["previous_month_spending"]+=state.month2_transactions[index].transaction_amount
            final_transaction_report[month_2_categories.categories[index]]["transaction_count_previous_month"]+=1
            final_transaction_report[month_2_categories.categories[index]]["absolute_change"] = final_transaction_report[month_2_categories.categories[index]]["previous_month_spending"] - final_transaction_report[month_1_categories.categories[index]]["previous_to_previous_month_spending"]
            final_transaction_report[month_2_categories.categories[index]]["trend_indicator"] = UtilsContainer.get_trend(
                final_transaction_report[month_2_categories.categories[index]]["absolute_change"],
                final_transaction_report[month_1_categories.categories[index]]["previous_to_previous_month_spending"],
                final_transaction_report[month_2_categories.categories[index]]["previous_month_spending"]
            )
            if (final_transaction_report[month_1_categories.categories[index]]["previous_to_previous_month_spending"]==0):
                final_transaction_report[month_2_categories.categories[index]]["percentage_change"] = 100
            else:
                final_transaction_report[month_2_categories.categories[index]]["percentage_change"] = (final_transaction_report[month_2_categories.categories[index]]["absolute_change"]/final_transaction_report[month_1_categories.categories[index]]["previous_to_previous_month_spending"])*100
            if (final_transaction_report[month_2_categories.categories[index]]["percentage_change"]>50.00):
                final_transaction_report[month_2_categories.categories[index]]["significance_flag"] = True

    return SummarizeAgentIntermediateState(
        transaction_report=final_transaction_report
    )

async def summarize_spending(state: SummarizeAgentIntermediateState) -> FinalOutputState:
    gemini_llm_with_structured_output = gemini_llm.with_structured_output(SummarizeAgentOutputState)
    summarize_chain = (summary_making_prompt_template | gemini_llm_with_structured_output)
    formatted_category_data = [{key:value} for key,value in state.transaction_report.items()]
    llm_response = await summarize_chain.ainvoke(
        {
            "category_data": json.dumps(formatted_category_data, indent=2)
        }
    )
    llm_summary = SummarizeAgentOutputState.model_validate(llm_response)
    result = FinalOutputState(
        executive_summary=llm_summary.executive_summary,
        key_observations=llm_summary.key_observations,
        notable_changes=llm_summary.notable_changes,
        new_spending_areas=llm_summary.notable_changes,
        spending_to_watch=llm_summary.spending_to_watch,
        transaction_report=state.transaction_report
    )
    return result

graph_builder = StateGraph(
    state_schema=SummarizeAgentOverallState,
    input_schema=SummarizeAgentInputState,
    output_schema=FinalOutputState
)
graph_builder.add_node("category_mapping",category_mapping)
graph_builder.add_node("summarize_spending",summarize_spending)

graph_builder.add_edge(START,"category_mapping")
graph_builder.add_edge("category_mapping","summarize_spending")
graph_builder.add_edge("summarize_spending",END)

summarize_graph = graph_builder.compile()