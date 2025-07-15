from sqlmodel import Field, SQLModel
from datetime import datetime, date, timezone

class DateTimeIn(SQLModel):
    year: int = Field(default_factory= lambda : datetime.now(timezone.utc).year)
    month: int | None = None
    curr_date: date | None = None