import uuid
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import Column, String, ForeignKey, DECIMAL
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Menu(Base):
    __tablename__ = 'menu'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(128), nullable=False, unique=True)
    description = Column(String)


class Submenu(Base):
    __tablename__ = 'submenu'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4) 
    title = Column(String(128), nullable=False, unique=True)
    description = Column(String)
    menu_id = Column(UUID, ForeignKey('menu.id', ondelete="CASCADE"), nullable=False)



class Dish(Base):
    __tablename__ = 'dish'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(128), nullable=False, unique=True)
    price = Column(DECIMAL(precision=8, scale=2), nullable=False)
    description = Column(String)
    submenu_id = Column(UUID, ForeignKey('submenu.id', ondelete="CASCADE"), nullable=False)
