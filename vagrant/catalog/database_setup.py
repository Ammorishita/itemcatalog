import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class FoodGroup(Base):
    __tablename__ = 'FoodGroup'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
        }


class FoodItem(Base):
    __tablename__ = 'FoodItem'

    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    calories = Column(String(8))
    fats = Column(String(8))
    carbs = Column(String(8))
    sugars = Column(String(8))
    foodgroup_id = Column(Integer, ForeignKey('FoodGroup.id'))
    foodGroup = relationship(FoodGroup)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in easily serializeable format"""
        return {
            'name': self.name,
            'id': self.id,
            'carbs': self.carbs,
            'calories': self.calories,
            'sugars': self.sugars,
            'fat': self.fats,
        }


engine = create_engine('sqlite:///nutritioncatalog.db')


Base.metadata.create_all(engine)