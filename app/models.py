from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)

    favorites = relationship("Favorite", back_populates="user")

class Route(Base):
    __tablename__ = "routes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    city = Column(String)
    activities = Column(String)
    distance_km = Column(Float)
    walk_time_min = Column(Integer)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    coordinates = Column(String)  # JSON string with coordinates
    is_premium = Column(Boolean, default=False)
    image_url = Column(String)
    map_url = Column(String)
    photos = Column(String)  # JSON string with photo URLs

    favorites = relationship("Favorite", back_populates="route")

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String)
    city = Column(String)
    activities = Column(String)
    distance_km = Column(Float)
    walk_time_min = Column(Integer)
    likes = Column(Integer, default=0)
    dislikes = Column(Integer, default=0)
    rating = Column(Float, default=0.0)
    coordinates = Column(String)  # JSON string with coordinates

    favorites = relationship("Favorite", back_populates="route")

class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    route_id = Column(Integer, ForeignKey("routes.id"))

    user = relationship("User", back_populates="favorites")
    route = relationship("Route", back_populates="favorites")