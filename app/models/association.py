from sqlalchemy import Table,Column,Integer,ForeignKey
from database.database import Base

user_roles= Table(
    "user_roles",
    Base.metadata,
    Column("user_id",Integer,ForeignKey("users.id")),
    Column("roles_id",Integer,ForeignKey("roles.id"))

)

role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column("role_id",Integer,ForeignKey("roles.id")),
    Column("permissions_id",Integer,ForeignKey("permissions.id"))
)