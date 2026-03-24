from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base
from models.rbac import role_permissions

class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)

    roles = relationship(
        "Role",
        secondary=role_permissions,
        back_populates="permissions"
    )
