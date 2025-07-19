from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import extract, select

from Database.Models.datetime_models import DateTimeIn
from Database.Models.info_models import StudentInDB
from Database.Models.transaction_models import TransactionIn, TransactionInDB
from Utils.dependency_container import DependencyContainer
from Utils.exceptions import Exceptions
from Utils.middleware import DashboardRoute
from Utils.response import APIResponse

home_router = APIRouter(
    prefix="/home",
    tags=["Home Dashboard"],
    route_class=DashboardRoute
)

@home_router.post("/add_transaction", response_model=APIResponse)
async def add_transaction(data: TransactionIn, request: Request, session: AsyncSession = Depends(DependencyContainer.get_session)):
    student_id = request.state.student_id
    student_info = await session.get(StudentInDB,student_id)
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
