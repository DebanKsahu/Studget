from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, List

import jwt
from passlib.context import CryptContext
from redis.asyncio import Redis
from sqlmodel import extract, select

from config import settings
from Database.Models.transaction_models import TransactionInDB
from Utils.enum import TCategory, TrendIndicator
from Utils.factory import async_session_factory


class PasswordUtils():
    pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str):
        return PasswordUtils.pwdContext.verify(secret=plain_password,hash=hashed_password)
    
    @staticmethod
    def hash_password(plain_password: str):
        return PasswordUtils.pwdContext.hash(plain_password)
    
class JwtUtils():

    @staticmethod
    def create_jwt(data: dict[str,Any]):
        copied_data = data.copy()
        encoded_jwt = jwt.encode(copied_data,key=settings.secret_key,algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def decode_jwt(token: str) -> dict[str,Any]:
        payload: dict = jwt.decode(jwt=token,key=settings.secret_key,algorithms=[settings.algorithm])
        return payload
    
class DataFormattingUtils():

    @staticmethod
    def format_transaction_data(data: List[TransactionInDB]) -> str:
        preprocessed_data = [
            f"Transaction Amount = {transaction.transaction_amount}, Transaction Category = {transaction.transaction_category.value}, Transaction Date = {transaction.transaction_date}, Transaction Description = {transaction.transaction_description} "
            for transaction in data
        ]
        result = ("\n").join(preprocessed_data)
        return result
    
    @staticmethod
    def extract_transaction_description(data: List[TransactionInDB]) -> str:
        preprocessed_data = [
            f"Transaction Description = {transaction.transaction_description}"
            for transaction in data
        ]
        result = ("\n").join(preprocessed_data)
        return result
    
class TransactionsUtils():

    @staticmethod
    async def update_cached_monthly_report(redis: Redis, student_id: int, new_amount: int, new_category: TCategory) -> None:
        cached_monthly_total = await redis.get(f"student_id:{student_id}:monthly_total")
        cached_monthly_report_dict = await redis.hgetall(f"student_id:{student_id}") # type: ignore
        if cached_monthly_total is not None and cached_monthly_report_dict is not None:
            await redis.set(f"student_id:{student_id}:monthly_total",cached_monthly_total+new_amount)
            await redis.expire(f"student_id:{student_id}:monthly_total",3600)
        else:
            async with async_session_factory() as session:
                statement = select(TransactionInDB).where(
                    TransactionInDB.student_id==student_id,
                    extract("month",TransactionInDB.transaction_date)==datetime.now(timezone.utc).month
                    )
                transactions = list((await session.execute(statement)).scalars())
                monthly_total = 0
                monthly_report_dict = defaultdict(int)
                for transaction in transactions:
                    monthly_total+=transaction.transaction_amount
                    monthly_report_dict[f"{student_id}:{transaction.transaction_category.value}"]+=transaction.transaction_amount
                monthly_report_dict["cached_monthly_spending"]=monthly_total
                cached_monthly_report_dict = monthly_report_dict
                monthly_total+=new_amount
                await redis.set(f"student_id:{student_id}:monthly_total",monthly_total)
                await redis.expire(f"student_id:{student_id}:monthly_total",3600)
                
        if cached_monthly_report_dict is not None:
            cached_monthly_report_dict[f"{student_id}:{new_category.value}"] = cached_monthly_report_dict.get(f"{student_id}:{new_category.value}",0) + new_amount
            cached_monthly_report_dict["cached_monthly_spending"] = cached_monthly_report_dict.get("cached_monthly_spending",0) + new_amount
            await redis.hset(f"student_id:{student_id}",cached_monthly_report_dict) # type: ignore
            await redis.expire(f"student_id:{student_id}",3600)

class UtilsContainer:

    @staticmethod
    def get_trend(num: int,prev_spending: int,curr_spending: int) -> TrendIndicator:
        match num:
            case _ if num>0:
                return TrendIndicator.INC
            case 0:
                return TrendIndicator.STABLE
            case _ if num<0:
                return TrendIndicator.DEC
            case _ if prev_spending==0:
                return TrendIndicator.NEW
            case _ if curr_spending==0:
                return TrendIndicator.STOP
        return TrendIndicator.STOP

    jwt_utils = JwtUtils()
    password_utils = PasswordUtils()
    data_formatting_utils = DataFormattingUtils()
    transactions_utils = TransactionsUtils()