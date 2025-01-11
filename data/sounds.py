import datetime
import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Sound(SqlAlchemyBase):
    __tablename__ = 'sounds'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    data_sound = sqlalchemy.Column(sqlalchemy.TEXT, nullable=False)

    def __repr__(self):
        return f'{self.id};;{self.name};;{self.description};;{self.data_sound}'