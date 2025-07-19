from sqlmodel import Field, SQLModel


class StudentLogin(SQLModel):
    student_email: str = Field(min_length=1)
    password: str = Field(min_length=1)

class StudentSignup(StudentLogin):
    student_name: str = Field(min_length=1)