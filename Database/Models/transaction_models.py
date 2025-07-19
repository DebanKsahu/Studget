from datetime import date, datetime, timezone
from typing import Any, Dict, Self

from pydantic import model_validator
from sqlmodel import BigInteger, Column, Field, ForeignKey, SQLModel

from Utils.enum import TCategory
from Utils.exceptions import Exceptions


class TransactionInDB(SQLModel, table=True):
    transation_id: int | None = Field(default=None, sa_column=Column(BigInteger, primary_key=True))
    student_id: int = Field(sa_column=Column(BigInteger,ForeignKey("studentindb.student_id",ondelete="CASCADE")))
    transaction_amount: int = Field(ge=1)
    transaction_category: TCategory
    transaction_description: str = Field(nullable=False)
    transaction_date: date = Field(default_factory=lambda : datetime.now(timezone.utc))

    
class TransactionIn(SQLModel):
    transaction_amount: int = Field(ge=1)
    transaction_category: TCategory
    transaction_description: str = Field(nullable=False)

    @model_validator(mode="after")
    def validate_category(self) -> Self:
        expected_types = (TCategory.ENTERTAINMENT, TCategory.FOOD, TCategory.HEALTH, TCategory.SHOPPING, TCategory.TRANSPORTATION)
        if (self.transaction_category not in expected_types):
            raise Exceptions.invalid_input_type_exception(field_name="transaction_category", expected_type=f"{(" ").join(expected_types)}")
        return self
    
class MonthlyReportOut(SQLModel):
    monthly_spending: int 
    monthly_categorywise_spending: Dict[str,Any]