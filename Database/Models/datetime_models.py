from sqlmodel import Field, SQLModel
from datetime import datetime, date, timezone

class DateTimeIn(SQLModel):
    year: int | None = Field(default_factory= lambda : datetime.now(timezone.utc).year)
    month: int | None = Field(default=None)
    curr_date: date | None = Field(default=None)