from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from Database.Models.auth_models import StudentLogin, StudentSignup
from Database.Models.info_models import StudentInDB
from Database.Models.token_models import Token
from Utils.dependency_container import DependencyContainer
from Utils.exceptions import Exceptions
from Utils.response import APIResponse
from Utils.utility_functions import UtilsContainer

auth_router = APIRouter(
    prefix = "/auth",
    tags = ["Authetication"]
)

@auth_router.post("/login", response_model=APIResponse)
async def login(login_data: StudentLogin, session: AsyncSession = Depends(DependencyContainer.get_session)):
    sql_statement = select(StudentInDB).where(StudentInDB.student_email==login_data.student_email)
    student_results =  await session.execute((sql_statement))
    student_info = student_results.scalar()
    if student_info is None:
        raise Exceptions.item_not_found_exception(item_name=f"Student with {login_data.student_email} email")
    if (not UtilsContainer.password_utils.verify_password(login_data.password,student_info.hashed_password)):
        raise Exceptions.wrong_authentication_exception(reason="Password Don't match")
    payload = {"student_id": student_info.student_id}
    access_token = UtilsContainer.jwt_utils.create_jwt(payload)
    return APIResponse.success_response(data=Token(access_token=access_token,token_type="bearer"), message="Login Successful")

@auth_router.post("/signup", response_model=APIResponse)
async def signup(signup_data: StudentSignup, session: AsyncSession = Depends(DependencyContainer.get_session)):
    sql_statement = select(StudentInDB).where(StudentInDB.student_email==signup_data.student_email)
    student_results = await session.execute((sql_statement))
    student_info = list(student_results.scalars().all())
    if (len(student_info)>0):
        raise Exceptions.item_already_exists_exception(item_name=f"{signup_data.student_email}")
    new_student_info = StudentInDB(
        student_name = signup_data.student_name,
        student_email = signup_data.student_email,
        hashed_password = UtilsContainer.password_utils.hash_password(signup_data.password)
    )
    session.add(new_student_info)
    await session.commit()
    return APIResponse.success_response(message="Signup Successful")
    