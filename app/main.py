from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional
import requests
import json

from app import models, schemas, crud, auth
from app.database import SessionLocal, engine
from app.config import settings

models.Base.metadata.create_all(bind=engine)

app = FastAPI()
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, db: Session = Depends(get_db)):
    routes = crud.get_routes(db)
    return templates.TemplateResponse("index.html", {
        "request": request,
        "routes": routes
    })




@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login", response_class=HTMLResponse)
async def login(
        request: Request,
        email: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    user = auth.authenticate_user(db, email, password)
    if not user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Invalid email or password"}
        )

    access_token_expires = timedelta(minutes=auth.settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    response = RedirectResponse(url="/", status_code=303)
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


@app.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@app.post("/register", response_class=HTMLResponse)
async def register(
        request: Request,
        name: str = Form(...),
        email: str = Form(...),
        phone: str = Form(...),
        password: str = Form(...),
        db: Session = Depends(get_db)
):
    db_user = crud.get_user_by_email(db, email=email)
    if db_user:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Email already registered"}
        )

    user = schemas.UserCreate(
        name=name,
        email=email,
        phone=phone,
        password=password
    )
    crud.create_user(db=db, user=user)

    return RedirectResponse(url="/login", status_code=303)


@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("access_token")
    return response


@app.get("/routes", response_class=HTMLResponse)
async def read_routes(
        request: Request,
        city: Optional[str] = None,
        db: Session = Depends(get_db),
        current_user: Optional[models.User] = Depends(auth.get_current_user_optional)
):
    if city:
        routes = crud.get_routes_by_city(db, city=city)
    else:
        routes = crud.get_routes(db)

    favorite_ids = []
    if current_user:
        favorites = crud.get_favorites(db, user_id=current_user.id)
        favorite_ids = [fav.route_id for fav in favorites]

    return templates.TemplateResponse("routes.html", {
        "request": request,
        "routes": routes,
        "city": city,
        "favorite_ids": favorite_ids
    })



@app.get("/routes/{route_id}", response_class=HTMLResponse)
async def read_route(
        request: Request,
        route_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
):
    route = crud.get_route(db, route_id=route_id)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")

    # Get Yandex Map for the route
    coordinates = json.loads(route.coordinates)
    yandex_map_url = f"https://static-maps.yandex.ru/1.x/?l=map&pt={'~'.join([f'{c[0]},{c[1]},pm2rdm' for c in coordinates])}&size=600,400"

    return templates.TemplateResponse(
        "route_detail.html",
        {
            "request": request,
            "route": route,
            "yandex_map_url": yandex_map_url,
            "user_id": current_user.id
        }
    )


@app.post("/routes/{route_id}/like")
async def like_route(
        route_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
):
    route = crud.update_route_rating(db, route_id=route_id, like=True)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return RedirectResponse(url=f"/routes/{route_id}", status_code=303)


@app.post("/routes/{route_id}/dislike")
async def dislike_route(
        route_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
):
    route = crud.update_route_rating(db, route_id=route_id, like=False)
    if not route:
        raise HTTPException(status_code=404, detail="Route not found")
    return RedirectResponse(url=f"/routes/{route_id}", status_code=303)


@app.get("/favorites", response_class=HTMLResponse)
async def read_favorites(
        request: Request,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
):
    favorites = crud.get_favorites(db, user_id=current_user.id)
    routes = [fav.route for fav in favorites]
    return templates.TemplateResponse(
        "favorites.html",
        {"request": request, "routes": routes}
    )


@app.post("/favorites/add/{route_id}")
async def add_to_favorites(
        route_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
):
    favorite = schemas.FavoriteBase(
        user_id=current_user.id,
        route_id=route_id
    )
    crud.add_favorite(db, favorite=favorite)
    return RedirectResponse(url=f"/routes/{route_id}", status_code=303)


@app.post("/favorites/remove/{route_id}")
async def remove_from_favorites(
        route_id: int,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
):
    crud.remove_favorite(db, user_id=current_user.id, route_id=route_id)
    return RedirectResponse(url=f"/routes/{route_id}", status_code=303)


@app.get("/profile", response_class=HTMLResponse)
async def read_profile(
        request: Request,
        db: Session = Depends(get_db),
        current_user: models.User = Depends(auth.get_current_active_user)
):
    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": current_user}
    )