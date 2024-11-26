select * from "GroupTable"

select * from "UserGroupTable"

select * from "UserTable"

select * from "TaskTable"

select * from "TestTable"

select "GroupTable".group_id, "UserGroupTable".user_id, "UserGroupTable".status
from "GroupTable"
left join "UserGroupTable"
on "GroupTable".group_id = "UserGroupTable".group_id and "UserGroupTable".user_id = 12