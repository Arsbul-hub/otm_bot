from sqlalchemy.orm import DeclarativeBase, relationship
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Boolean


class BaseModel(DeclarativeBase):
    pass


class User(BaseModel):
    __tablename__ = "users"
    user_id = Column(String, primary_key=True)
    user_fio = Column(String)
    group_id = Column(Integer, ForeignKey('groups.group_id'))
    is_elder = Column(Boolean, default=False)
    group = relationship("Group", back_populates="users")
class Group(BaseModel):
    __tablename__ = "groups"
    group_id = Column(Integer, primary_key=True)
    name = Column(String)
    users = relationship("User", back_populates="group", uselist=True)

class Marker(BaseModel):
    __tablename__ = "markers"
    marker_id = Column(Integer, primary_key=True)
    user_id = Column(String, ForeignKey('users.user_id'))
    timestamp = Column(DateTime(timezone=True))
    add_timestamp = Column(DateTime(timezone=True))
    all_day = Column(Boolean)

class EditableConfig(BaseModel):
    __tablename__ = "editable_configs"
    config_id = Column(Integer, primary_key=True)
    key = Column(String)
    value = Column(String)

class Code(BaseModel):
    __tablename__ = "codes"
    code = Column(Integer, primary_key=True)
    owner_id = Column(String, ForeignKey('users.user_id'))
    expires = Column(DateTime)