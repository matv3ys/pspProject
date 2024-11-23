from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import text
from typing import Annotated
import datetime
from werkzeug.security import check_password_hash
from flask_login import UserMixin

Base = declarative_base()
intpk = Annotated[int, mapped_column(primary_key=True)]
str_unique = Annotated[str, mapped_column(unique=True)]
str_not_unique = Annotated[str, mapped_column(unique=False)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]

class UserTable(Base, UserMixin):
    __tablename__ = "UserTable"

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def get_id(self):
           return self.user_id

    user_id:         Mapped[intpk]
    login:           Mapped[str_unique]
    email:           Mapped[str_not_unique]
    surname:         Mapped[str_not_unique]
    name:            Mapped[str_not_unique]
    hashed_password: Mapped[str_not_unique]
    created_at:      Mapped[created_at]
