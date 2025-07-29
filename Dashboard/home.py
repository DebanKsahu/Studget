from datetime import datetime, timezone

from fastapi import APIRouter, BackgroundTasks, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import extract, select

from Database.Models.datetime_models import DateTimeIn
from Database.Models.info_models import StudentInDB
from Database.Models.transaction_models import TransactionIn, TransactionInDB
from Utils.dependency_container import DependencyContainer
from Utils.enum import SpendIndicator
from Utils.exceptions import Exceptions
from Utils.middleware import DashboardRoute
from Utils.response import APIResponse
from Utils.utility_functions import UtilsContainer

home_router = APIRouter(
    prefix="/home",
    tags=["Home Dashboard"],
    route_class=DashboardRoute
)

@home_router.post("/add_transaction", response_model=APIResponse)
async def add_transaction(data: TransactionIn, request: Request, background_tasks: BackgroundTasks, session: AsyncSession = Depends(DependencyContainer.get_session)):
    student_id = request.state.student_id
    student_info = await session.get(StudentInDB,student_id)
    redis = request.app.state.redis_client
    if student_info is None:
        raise Exceptions.item_not_found_exception(item_name="Student")
    new_transaction = TransactionInDB(
        student_id=student_id,
        transaction_amount=data.transaction_amount,
        transaction_category=data.transaction_category,
        transaction_description=data.transaction_description
    )
    session.add(new_transaction)
    await session.commit()
    background_tasks.add_task(
        UtilsContainer.transactions_utils.update_cached_monthly_report,
        redis,
        student_id,
        data.transaction_amount,
        data.transaction_category
    )
    return APIResponse.success_response(message="Transaction Successfully added")

@home_router.post("/get_transactions", response_model=APIResponse)
async def get_transactions(request: Request, input_date: DateTimeIn, session: AsyncSession = Depends(DependencyContainer.get_session)):
    student_id = request.state.student_id
    student_info =  await session.get(StudentInDB,student_id)
    if student_info is None:
        raise Exceptions.item_not_found_exception(item_name="Student")
    student_transactions = None
    if (input_date.curr_date is None and input_date.month is None):
        sql_query = select(TransactionInDB).where(TransactionInDB.student_id==student_id).where(extract("year",TransactionInDB.transaction_date)==input_date.year)
        db_response = await session.execute(sql_query)
        student_transactions = list(db_response.scalars())
    elif (input_date.curr_date is  not None):
        sql_query = select(TransactionInDB).where(TransactionInDB.student_id==student_id).where(TransactionInDB.transaction_date==input_date.curr_date)
        db_response = await session.execute(sql_query)
        student_transactions = list(db_response.scalars())
    elif (input_date.month is  not None):
        sql_query = select(TransactionInDB).where(TransactionInDB.student_id==student_id).where(extract("year",TransactionInDB.transaction_date)==input_date.year).where(extract("month",TransactionInDB.transaction_date)==input_date.month)
        db_response = await session.execute(sql_query)
        student_transactions = list(db_response.scalars())
    return APIResponse.success_response(data=student_transactions,message="Successfully retrived transactions")

@home_router.post("/set_monthly_limit/{monthly_limit}")
async def set_monthly_limit(monthly_limit: int, request: Request, session: AsyncSession = Depends(DependencyContainer.get_session)):
    student_id = request.state.student_id
    student_info =  await session.get(StudentInDB,student_id)
    redis = request.app.state.redis_client
    if student_info is None:
        raise Exceptions.item_not_found_exception(item_name="Student") 
    await redis.set(f"student_id:{student_id}:monthly_limit",monthly_limit) 
    return APIResponse.success_response(message="Monthly limit successfully updated")

@home_router.get("/get_spending_indicator", response_model=APIResponse)
async def get_spending_indicator(request: Request, session: AsyncSession = Depends(DependencyContainer.get_session)):
    student_id = request.state.student_id
    student_info =  await session.get(StudentInDB,student_id)
    redis = request.app.state.redis_client
    if student_info is None:
        raise Exceptions.item_not_found_exception(item_name="Student")
    cached_monthly_total = await redis.get(f"student_id:{student_id}:monthly_total")
    cached_monthly_limit = await redis.get(f"student_id:{student_id}:monthly_limit")
    spending_indicator = SpendIndicator.GREEN
    if cached_monthly_total is None:
        sql_query = select(TransactionInDB).where(TransactionInDB.student_id==student_id).where(extract("month",TransactionInDB.transaction_date)==datetime.now(timezone.utc).month)
        db_response = await session.execute(sql_query)
        all_monthly_transactions = list(db_response.scalars())
        temp_total = 0
        for transactions in all_monthly_transactions:
            temp_total+=transactions.transaction_amount
        await redis.set(f"student_id:{student_id}:monthly_total",temp_total)
        await redis.expire(f"student_id:{student_id}:monthly_total",3600)
        cached_monthly_total = await redis.get(f"student_id:{student_id}:monthly_total")
    cached_monthly_total = int(cached_monthly_total)
    if cached_monthly_limit is None:
        cached_monthly_limit = 5000
    if cached_monthly_total>=(int(cached_monthly_limit) + 0.5*int(cached_monthly_limit)):
        spending_indicator = SpendIndicator.RED
    elif cached_monthly_total>int(cached_monthly_limit):
        spending_indicator = SpendIndicator.ORANGE
    return APIResponse.success_response(data={"spending_indicator": spending_indicator}, message="Indicator successfully retrieved")
    