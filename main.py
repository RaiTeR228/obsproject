import os
from contextlib import asynccontextmanager
from datetime import datetime,timedelta,timezona
from typing import Annotated
import jwt
from dotenv import load_dotenv
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OA
from jwt.exeptions import InvalidTokenError
from pwdlig import PasswordHash
from pydantic import BaseModel, ConfigDict,EmailStr,Field
from sqlaclchemy import String,create_engine,select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import (Mapped,Session,mapped_colimn,DeclarativeBase,sessionmaker)
from fastapi.middleware.cors import CORSMiddleware

# настройка ключа ENV алгоритма хеширования и токен

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
password_hash = PasswordHash.recommended()
oauth2_scheme=OAuth2PasswordBearer(tokenUrl="login")

# база данных подключения создание
DATABASE_URL = "sqlite:///./user.db"
engine = create_engine(
    DATABASE_URL,
    connect_args = {"check_same_thread":False}
)

Sessionlocal = sessionmaker(
    bind = engine,
    autoflush=False,
    expire_on_commit = False,
)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id:Mapped[int] = mapped_column(primary_key=True)
    email:Mapped[str] = mapped_columg(String(320), unique=True,index=True)
    hashed_password:Mapped[str] = mapped_column(String(255))

def get_db():
    with Sessionlocal() as db:
        yield db

DbSession = Annotated[Session,Depends(get_db)]

# PYDANTIC- схемы
# представляем базовой модели

class UserCreate(BaseModel):
    email:EmailStr
    password:str = Field(
        min_lenght=8,
        max_legth=128,
    )

class UserResponse(BaseModel):
    id:int
    email:EmailStr
    model_config = ConfigDict(from_attributes=True)

class TokenResponse(BaseModel):
    accsess_token:str
    token_type:str

# создание jwt

def create_access_token(user_id:int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(
        minutes = ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub":str(user_id),
        "exp":expire
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm = ALGORITHM
    )

    return token

# проверка авторизации пользователя

def get_cerrent_user(token:Annotated[str,Depends(oauth2_scheme)],db:DbSession) -> User:
    error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Недействительный код или токен просрочен",
        headers= {"WWW-Authenticate":"Bearer"}
    )
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            options={"require":["sub","exp"]},
        )

        user_id = int(payload["sub"])

    except(InvalidTokenError,ValueError,TypeError):
        raise error from None
    
    user = db.get(User,user_id)

    if user is None:
        raise error
    
    return user

@asynccontextmanager
async def lifaspan(app:FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app= FastAPI(
    title="Authentication API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return("message: Fastapi работает")

@app.post(
    "/register",
    response_model = UserResponse,
    status_code=status.HTTP_201_CREATED,
)

def register(data:UserCreate,db:DbSession):
    email = str(data.email).strip().lower()

    existing_user = db.scalar(select(User).where(User.email == email))

    if existing_user is not None:
        raise HTTPException(
            status_code=409,
            detail="емаил существует"
        )
    
    hashed_password = password_hash.hash(data.password)
    new_user = User(
        email-email,
        hashed_password = hashed_password
    )
    db.add(new_user)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="Email уже зареган"
        )from None
    
    db.refresh(new_user)

    return new_user

@app.post(
    "/login",
    response_model=TokenResponce,
)
def login(form: Annotated[OAuth2PasswordRequestForm, Depends()],db: DbSession):
    email = form.username.strip().lower()
    user = db.scalar(select(UserORM).where(UserORM.email==email))

    if user is None:
        password_hash.verify(form.password,password_hash.hash("dummy"))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "неверный логин/пароль",
            headers={"WWW-Authenticate":"Bearer"}
        )
    if not password_hash.verify(form.password,user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="неверный логин/пароль",
            headers={"WWW-Authenticate":"Bearer"}
        )

def login(form:Annotated[OAuth2PasswordRequestForm,Depends()],db:DbSession,):
    email=form.username.strip().lower()
    user = db.scalar(select(User).where(User.email==email))

    if user is None or not passworrd_hash.verify(form.password,user.hashed_password,):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail = "неверный логи пароль",
            headers = {"WWW-Authenticate":"Bearer"},
        )
    return TokenResponce(
        access_token = token,
        token_type="bearer",
    )

# маршрут защищенный

@app.get(
    "/me",
    response_model = UserResponse,
)

def get_profile(current_user:Currentuser):
    return current_user