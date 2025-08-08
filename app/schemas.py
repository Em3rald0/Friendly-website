from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class RouteBase(BaseModel):
    title: str
    description: str
    city: str
    activities: str
    distance_km: float
    walk_time_min: int

class RouteCreate(RouteBase):
    pass

class Route(RouteBase):
    id: int
    likes: int
    dislikes: int
    rating: float
    coordinates: str

    class Config:
        from_attributes = True


class FavoriteBase(BaseModel):
    user_id: int
    route_id: int


class Favorite(FavoriteBase):
    id: int

    class Config:
        from_attributes = True