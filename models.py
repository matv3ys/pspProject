from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text
from typing import Annotated
import datetime
from werkzeug.security import generate_password_hash

Base = declarative_base()
intpk = Annotated[int, mapped_column(primary_key=True)]
str_unique = Annotated[str, mapped_column(unique=True)]
str_not_unique = Annotated[str, mapped_column(unique=False)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]

class UserTable(Base):
    __tablename__ = "UserTable"

    user_id:         Mapped[intpk]
    login:           Mapped[str_unique]
    email:           Mapped[str_not_unique]
    surname:         Mapped[str_not_unique]
    name:            Mapped[str_not_unique]
    hashed_password: Mapped[str_not_unique]
    created_at:      Mapped[created_at]
