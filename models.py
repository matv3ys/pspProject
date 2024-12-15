from enum import unique

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
int_not_unique_nullable = Annotated[int, mapped_column(unique=False, nullable=True)]
int_unique = Annotated[int, mapped_column(unique=True)]
float_not_unique = Annotated[float, mapped_column(unique=False)]
str_unique = Annotated[str, mapped_column(unique=True)]
str_not_unique = Annotated[str, mapped_column(unique=False)]
str_not_unique_nullable = Annotated[str, mapped_column(unique=False, nullable=True)]
bool_not_unique = Annotated[bool, mapped_column(unique=False, nullable=False)]
created_at = Annotated[datetime.datetime, mapped_column(server_default=text("TIMEZONE('utc', now())"))]
contest_date = Annotated[datetime.datetime, mapped_column(nullable=False)]


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

class ContestGroupTable(Base):
    __tablename__ = "ContestGroupTable"

    contest_id: Mapped[intpk] = mapped_column(ForeignKey("ContestTable.contest_id"))
    group_id: Mapped[intpk] = mapped_column(ForeignKey("GroupTable.group_id"))

class GroupTable(Base):
    __tablename__ = "GroupTable"

    group_id:        Mapped[intpk]
    group_name:      Mapped[str_unique]
    owner_id:        Mapped[int_not_unique] = mapped_column(ForeignKey("UserTable.user_id"))
    created_at:      Mapped[created_at]
    members: Mapped[List[UserTable]] = relationship(
        secondary="UserGroupTable", back_populates="groups"
    )
    contests: Mapped[List[lambda: ContestTable]] = relationship(  # lambda for cross declaration
        secondary="ContestGroupTable", back_populates="groups"
    )

class ContestTaskTable(Base):
    __tablename__ = "ContestTaskTable"

    contest_id: Mapped[intpk] = mapped_column(ForeignKey("ContestTable.contest_id"))
    task_id: Mapped[intpk] = mapped_column(ForeignKey("TaskTable.task_id"))
    num: Mapped[int_not_unique]

class TaskTable(Base):
    __tablename__ = "TaskTable"

    task_id:        Mapped[intpk]
    author_id:      Mapped[int_not_unique] = mapped_column(ForeignKey("UserTable.user_id"))
    title:          Mapped[str_not_unique]
    time_limit:     Mapped[int_not_unique]
    description:    Mapped[str_not_unique]
    input_info:     Mapped[str_not_unique]
    output_info:    Mapped[str_not_unique]
    created_at:     Mapped[created_at]
    contests: Mapped[List[lambda: ContestTable]] = relationship(   # lambda for cross declaration
        secondary="ContestTaskTable", back_populates="tasks"
    )

class TestTable(Base):
    __tablename__ = "TestTable"

    test_id:        Mapped[intpk]
    task_id:        Mapped[int_not_unique] = mapped_column(ForeignKey("TaskTable.task_id"))
    test_num:       Mapped[int_not_unique]
    input_data:     Mapped[str_not_unique]
    output_data:    Mapped[str_not_unique]
    is_open:        Mapped[bool_not_unique]
    created_at:     Mapped[created_at]



class ContestTable(Base):
    __tablename__ = "ContestTable"

    contest_id: Mapped[intpk]
    name: Mapped[str_not_unique]
    description: Mapped[str_not_unique]
    start_time: Mapped[contest_date]
    end_time: Mapped[contest_date]
    author_id: Mapped[int_not_unique] = mapped_column(ForeignKey("UserTable.user_id"))
    created_at: Mapped[created_at]
    tasks: Mapped[List[TaskTable]] = relationship(
        secondary="ContestTaskTable", back_populates="contests"
    )
    groups: Mapped[List[GroupTable]] = relationship(
        secondary="ContestGroupTable", back_populates="contests"
    )

class SubmissionTable(Base):
    __tablename__ = "SubmissionTable"

    submission_id: Mapped[intpk]
    task_id: Mapped[int_not_unique] = mapped_column(ForeignKey("TaskTable.task_id"))
    user_id: Mapped[int_not_unique] = mapped_column(ForeignKey("UserTable.user_id"))
    contest_id: Mapped[int_not_unique] = mapped_column(ForeignKey("ContestTable.contest_id"))
    code: Mapped[str_not_unique]
    language: Mapped[int_not_unique]
    status: Mapped[int_not_unique]
    output: Mapped[str_not_unique_nullable]
    created_at: Mapped[created_at]


# https://stackoverflow.com/questions/5756559/how-to-build-many-to-many-relations-using-sqlalchemy-a-good-example
# https://docs.sqlalchemy.org/en/20/orm/basic_relationships.html#many-to-many