from sqlalchemy.orm import Session
from app import models, schemas
from app.auth import get_password_hash


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    db_user = models.User(
        email=user.email,
        name=user.name,
        phone=user.phone,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_routes(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Route).offset(skip).limit(limit).all()


def get_route(db: Session, route_id: int):
    return db.query(models.Route).filter(models.Route.id == route_id).first()


def get_routes_by_city(db: Session, city: str):
    return db.query(models.Route).filter(models.Route.city == city).all()


def create_route(db: Session, route: schemas.RouteCreate):
    db_route = models.Route(**route.dict())
    db.add(db_route)
    db.commit()
    db.refresh(db_route)
    return db_route


def get_favorites(db: Session, user_id: int):
    return db.query(models.Favorite).filter(models.Favorite.user_id == user_id).all()


def add_favorite(db: Session, favorite: schemas.FavoriteBase):
    db_favorite = models.Favorite(**favorite.dict())
    db.add(db_favorite)
    db.commit()
    db.refresh(db_favorite)
    return db_favorite


def remove_favorite(db: Session, user_id: int, route_id: int):
    favorite = db.query(models.Favorite).filter(
        models.Favorite.user_id == user_id,
        models.Favorite.route_id == route_id
    ).first()
    if favorite:
        db.delete(favorite)
        db.commit()
        return True
    return False


def update_route_rating(db: Session, route_id: int, like: bool):
    route = get_route(db, route_id)
    if not route:
        return None

    if like:
        route.likes += 1
    else:
        route.dislikes += 1

    total = route.likes + route.dislikes
    if total > 0:
        route.rating = (route.likes / total) * 5

    db.commit()
    db.refresh(route)
    return route