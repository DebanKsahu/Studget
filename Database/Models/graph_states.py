from typing import List

from pydantic import BaseModel, Field

from Database.Models.output_formatters import QueryInfo
from Database.Models.transaction_models import TransactionInDB


class UserInput(BaseModel):
    user_query: str = Field(min_length=1)

class InputState(BaseModel):
    user_query: str
    user_id: int

class FetchDataInState(BaseModel):
    user_id: int
    user_query: str
    extracted_info: QueryInfo

class FetchDataOutState(BaseModel):
    user_query: str
    fethed_transactions: List[TransactionInDB]

class OutputState(BaseModel):
    final_answer: str | None

class OverallState(InputState,FetchDataInState,FetchDataOutState,OutputState):
    pass