from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from Dashboard.Agent.chatAgent import graph
from Database.Models.graph_states import InputState, OutputState, UserInput
from Database.Models.info_models import StudentInDB
from Utils.dependency_container import DependencyContainer
from Utils.exceptions import Exceptions
from Utils.middleware import DashboardRoute
from Utils.response import APIResponse

bot_router = APIRouter(
    prefix="/bot",
    tags=["Studget Chatbot"],
    route_class=DashboardRoute
)

@bot_router.post("/studgetbot", response_model=APIResponse)
async def ask_chatbot(input_data: UserInput, request: Request, session: AsyncSession = Depends(DependencyContainer.get_session)):
    student_id = request.state.student_id
    student_info = await session.get(StudentInDB,student_id)
    if student_info is None:
        raise Exceptions.item_not_found_exception(item_name="Student")
    graph_input_state = InputState(
        user_query=input_data.user_query,
        user_id=student_id
    )
    agent_result = await graph.ainvoke(input=graph_input_state)
    result = OutputState(
        final_answer = agent_result["final_answer"]
    )

    return APIResponse.success_response(data=result,message="Agent successfully answered")