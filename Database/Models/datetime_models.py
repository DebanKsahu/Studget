from datetime import date, datetime, timezone

from sqlmodel import Field, SQLModel


class DateTimeIn(SQLModel):
    year: int | None = Field(default_factory= lambda : datetime.now(timezone.utc).year)
    month: int | None = Field(default=None)
    curr_date: date | None = Field(default=None)