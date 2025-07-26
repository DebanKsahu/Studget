from typing import Any, List

import jwt
from passlib.context import CryptContext

from Utils.enum import TrendIndicator
from config import settings
from Database.Models.transaction_models import TransactionInDB


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