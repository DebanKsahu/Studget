
from datetime import datetime, timezone

from langgraph.graph import END, START, StateGraph
from sqlmodel import or_, select

from Dashboard.Agent.prompt_templates import (
    expense_analyze_prompt_template,
    info_extracting_prompt_template,
)
from Database.Models.graph_states import (
    FetchDataInState,
    FetchDataOutState,
    InputState,
    OutputState,
    OverallState,
)
from Database.Models.output_formatters import ExpenseAnalyzeInfo, QueryInfo
from Database.Models.transaction_models import TransactionInDB
from Utils.factory import async_session_factory
from Utils.llm import gemini_llm
from Utils.utility_functions import UtilsContainer


async def extract_info(state: InputState) -> FetchDataInState:
    gemini_llm_with_structured_output = gemini_llm.with_structured_output(QueryInfo)
    info_parser_chain = ( info_extracting_prompt_template | gemini_llm_with_structured_output )
    result = await info_parser_chain.ainvoke(
        {
            "today": lambda : datetime.now(timezone.utc),
            "user_query": state.user_query
        }
    )
    query_info = QueryInfo.model_validate(result)
    return FetchDataInState(
        user_id=state.user_id,
        user_query=state.user_query,
        extracted_info=query_info,
    )

async def fetch_data(state: FetchDataInState) -> FetchDataOutState:
    all_categories = state.extracted_info.transaction_category.split(" ")
    all_category_conditions = [
        TransactionInDB.transaction_category == category
        for category in all_categories
    ]
    sql_query = select(TransactionInDB).where(
        TransactionInDB.student_id==state.user_id
    ).where(
        or_(*all_category_conditions)
    ).where(
        TransactionInDB.transaction_date>=state.extracted_info.start_date
    ).where(
        TransactionInDB.transaction_date<=state.extracted_info.end_date
    )
    final_result = None
    async with async_session_factory() as session:
        db_response = await session.execute(sql_query)
        all_transactions = list(db_response.scalars())
        final_result = FetchDataOutState(
            user_query=state.user_query,
            fethed_transactions=all_transactions
        )
        
    return final_result

async def expense_analyze(state: FetchDataOutState) -> OutputState:
    gemini_llm_with_structured_output = gemini_llm.with_structured_output(ExpenseAnalyzeInfo)
    expense_analyze_chain = (expense_analyze_prompt_template | gemini_llm_with_structured_output)
    result = await expense_analyze_chain.ainvoke({
        "query": state.user_query,
        "data": UtilsContainer.data_formatting_utils.format_transaction_data(state.fethed_transactions)
    })
    result = ExpenseAnalyzeInfo.model_validate(result)
    return OutputState(final_answer=result.llm_response)

graph_builder = StateGraph(OverallState, input_schema=InputState, output_schema=OutputState)
graph_builder.add_node("extract_info",extract_info)
graph_builder.add_node("fetch_data",fetch_data)
graph_builder.add_node("expense_analyze",expense_analyze)

graph_builder.add_edge(START,"extract_info")
graph_builder.add_edge("extract_info","fetch_data")
graph_builder.add_edge("fetch_data","expense_analyze")
graph_builder.add_edge("expense_analyze",END)

graph = graph_builder.compile()