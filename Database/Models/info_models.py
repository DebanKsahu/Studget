from datetime import date, datetime, timezone
from typing import List

from sqlmodel import BigInteger, Column, Field, Relationship, SQLModel

from Database.Models.transaction_models import TransactionInDB


class StudentInDB(SQLModel, table=True):
    student_id: int | None = Field(
        default = None, 
        sa_column = Column(BigInteger, primary_key=True)
    )
    student_name: str
    student_email: str = Field(unique=True, index=True)
    member_since: date = Field(default_factory=lambda : datetime.now(timezone.utc))
    hashed_password: str

    student_transactions: List[TransactionInDB] = Relationship(cascade_delete=True, sa_relationship_kwargs={"foreign_keys": "[TransactionInDB.student_id]"}) # type: ignore

class StudentProfileOut(SQLModel):
    student_id: int 
    student_name: str
    student_email: str 
    member_since: date 