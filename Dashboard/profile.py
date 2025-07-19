from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import extract, select

from Database.Models.info_models import StudentInDB, StudentProfileOut
from Database.Models.transaction_models import MonthlyReportOut, TransactionInDB
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

@profile_router.get("/monthly_report", response_model=APIResponse)
async def get_monthly_report(request: Request, session: AsyncSession = Depends(DependencyContainer.get_session)):
    student_id = request.state.student_id
    student_info = await session.get(StudentInDB,student_id)
    if student_info is None:
        raise Exceptions.item_not_found_exception(item_name="Student")
    redis = request.app.state.redis_client
    cached_monthly_spending = await redis.hget(f"student_id:{student_id}",key="cached_monthly_spending")
    if (cached_monthly_spending is None):
        sql_query = select(TransactionInDB).where(TransactionInDB.student_id==student_id).where(extract("month",TransactionInDB.transaction_date)==datetime.now(timezone.utc).month)
        db_response = await session.execute(sql_query)
        all_monthly_transactions = list(db_response.scalars())
        in_memory_mapp = defaultdict(int)
        total_spending = 0
        for transaction in all_monthly_transactions:
            total_spending+=transaction.transaction_amount
            in_memory_mapp[f"{student_id}:{transaction.transaction_category.value}"]+=transaction.transaction_amount
        in_memory_mapp["cached_monthly_spending"]=total_spending
        await redis.hset(
            f"student_id:{student_id}",
            mapping = in_memory_mapp,
        )
        await redis.expire(f"student_id:{student_id}",70)
    student_monthly_report_dict = await redis.hgetall(f"student_id:{student_id}")
    cached_monthly_spending = student_monthly_report_dict["cached_monthly_spending"]
    student_monthly_report_dict.pop("cached_monthly_spending")
    result_data = MonthlyReportOut(
        monthly_spending=cached_monthly_spending,
        monthly_categorywise_spending=student_monthly_report_dict
    )
    return APIResponse.success_response(data = result_data, message="Monthly report successfully retrieved")
