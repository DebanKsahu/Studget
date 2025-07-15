from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from Database.Models.info_models import StudentInDB, StudentProfileOut
from Utils.dependency_container import DependencyContainer
from Utils.exceptions import Exceptions
from Utils.middleware import DashboardRoute
from Utils.response import APIResponse

profile_router = APIRouter(
    prefix="/profile",
    tags=["Student Profile"],
    route_class=DashboardRoute
)

@profile_router.get("/student_profile",response_model=APIResponse)
async def get_profile(request: Request, session: AsyncSession = Depends(DependencyContainer.get_session)):
    student_id = request.state.student_id
    student_info = await session.get(StudentInDB,student_id)
    if student_info is None:
        raise Exceptions.item_not_found_exception(item_name="Student")
    profile_date = StudentProfileOut(
        student_id=student_id,
        student_name=student_info.student_name,
        student_email=student_info.student_email,
        member_since=student_info.member_since
    )
    return APIResponse.success_response(data=profile_date,message="Profile Successfully retrived")