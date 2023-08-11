import uuid

from sqlalchemy import DECIMAL, Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Menu(Base):
    __tablename__ = 'menu'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(128), nullable=False, unique=True)
    description = Column(String)
    submenus = relationship('Submenu')


class Submenu(Base):
    __tablename__ = 'submenu'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(128), nullable=False, unique=True)
    description = Column(String)
    menu_id = Column(UUID, ForeignKey('menu.id', ondelete='CASCADE'), nullable=False)
    dishes = relationship('Dish')


class Dish(Base):
    __tablename__ = 'dish'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(128), nullable=False, unique=True)
    price = Column(DECIMAL(precision=8, scale=2), nullable=False)
    description = Column(String)
    submenu_id = Column(UUID, ForeignKey('submenu.id', ondelete='CASCADE'), nullable=False)
