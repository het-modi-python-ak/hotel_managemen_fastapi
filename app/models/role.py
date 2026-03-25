from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from database.database import Base
from models.association import user_roles, role_permissions


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=True)

    users = relationship("User", secondary=user_roles, back_populates="roles")

    permissions = relationship(
        "Permission",
        secondary=role_permissions,
        back_populates="roles"
    )