import calendar
from datetime import date, datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from Dashboard.Agent.summarize_agent import summarize_graph
from Database.Models.graph_states import FinalOutputState, SummarizeAgentInputState
from Database.Models.info_models import StudentInDB
from Database.Models.transaction_models import TransactionInDB
from Utils.dependency_container import DependencyContainer
from Utils.exceptions import Exceptions
from Utils.middleware import DashboardRoute
from Utils.response import APIResponse

agent_router = APIRouter(
    prefix="/agent",
    tags=["Studget Agents"],
    route_class=DashboardRoute  
)

@agent_router.get("/prev_month_summary", response_model=APIResponse)
async def get_summarize_report(request: Request, session: AsyncSession = Depends(DependencyContainer.get_session)):
    student_id = request.state.student_id
    student_info = await session.get(StudentInDB,student_id)
    if (student_info is None):
        raise Exceptions.item_not_found_exception(item_name="Student")
    redis = request.app.state.redis_client
    cached_result = await redis.get(f"summary:{student_id}")
    curr_date = datetime.now(timezone.utc)
    if (cached_result is not None):
        return APIResponse.success_response(data = FinalOutputState.model_validate_json(cached_result), message="Summary Successfully Created")
    month_1 = curr_date.month-1
    year_1 = curr_date.year
    month_2 = month_1-1
    year_2 = year_1
    if (month_1==0):
        month_1 = 12
        year_1 -= 1
        month_2 = 11
        year_2 -= 1
    elif (month_2==0):
        month_2 = 12
        year_2 -= 1
    month_1_start = date(year_1,month_1,1)
    month_1_end = date(year_1,month_1,calendar.monthrange(year_1,month_1)[1])
    month_2_start = date(year_2,month_2,1)
    month_2_end = date(year_2,month_2,calendar.monthrange(year_2,month_2)[1])
    sql_query = select(TransactionInDB).where(TransactionInDB.student_id==student_id).where(TransactionInDB.transaction_date>=month_1_start).where(TransactionInDB.transaction_date<=month_1_end)
    db_response = await session.execute(sql_query)
    month_1_transactions = list(db_response.scalars())
    if (len(month_1_transactions)==0):
        month_1_transactions = None
    sql_query = select(TransactionInDB).where(TransactionInDB.student_id==student_id).where(TransactionInDB.transaction_date>=month_2_start).where(TransactionInDB.transaction_date<=month_2_end)
    db_response = await session.execute(sql_query)
    month_2_transactions = list(db_response.scalars())
    if (len(month_2_transactions)==0):
        month_2_transactions = None
    agent_input = SummarizeAgentInputState(
        month1_transactions=month_2_transactions,
        month2_transactions=month_1_transactions
    )
    agent_response = await summarize_graph.ainvoke(input = agent_input)
    final_result = FinalOutputState(
        executive_summary=agent_response.get("executive_summary",""),
        key_observations=agent_response.get("key_observations",[""]),
        notable_changes=agent_response.get("notable_changes",""),
        new_spending_areas=agent_response.get("notable_changes",""),
        spending_to_watch=agent_response.get("spending_to_watch",""),
        transaction_report=agent_response.get("transaction_report","")
    )
    await redis.setex(f"summary:{student_id}",value=final_result.model_dump_json(),time=3600)
    return APIResponse.success_response(data = final_result, message="Summary Successfully Created")
    