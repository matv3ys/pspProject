from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import text, Table, Column, ForeignKey, Integer
from typing import Annotated, List
import datetime
from werkzeug.security import check_password_hash
from flask_login import UserMixin

Base = declarative_base()
intpk = Annotated[int, mapped_column(primary_key=True)]
int_not_unique = Annotated[int, mapped_column(unique=False)]
str_unique = Annotated[str, mapped_column(unique=True)]
str_not_unique = Annotated[str, mapped_column(unique=False)]
bool_not_unique = Annotated[bool, mapped_column(unique=False, nullable=False)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]


class UserGroupTable(Base):
    __tablename__ = "UserGroupTable"
    user_id: Mapped[intpk] = mapped_column(ForeignKey("UserTable.user_id"))
    group_id: Mapped[intpk] = mapped_column(ForeignKey("GroupTable.group_id"))
    status: Mapped[int_not_unique]


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
    is_organizer:    Mapped[bool_not_unique]
    hashed_password: Mapped[str_not_unique]
    created_at:      Mapped[created_at]
    groups: Mapped[List[lambda: GroupTable]] = relationship(   # lambda for cross declaration
        secondary="UserGroupTable", back_populates="members"
    )

class GroupTable(Base):
    __tablename__ = "GroupTable"

    group_id:        Mapped[intpk]
    group_name:      Mapped[str_unique]
    owner_id:        Mapped[int_not_unique] = mapped_column(ForeignKey("UserTable.user_id"))
    members: Mapped[List[UserTable]] = relationship(
        secondary="UserGroupTable", back_populates="groups"
    )


# https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many