from typing import Literal
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import User
from auth import hash_password, require_user

router = APIRouter(prefix="/users", tags=["users"])

admin_only = require_user(required_role="admin")


class UserOut(BaseModel):
    id: UUID
    email: str
    name: str
    auth_provider: str
    role: str
    is_active: bool
    created_at: str

    @classmethod
    def from_orm(cls, u: User):
        return cls(
            id=u.id, email=u.email, name=u.name,
            auth_provider=u.auth_provider, role=u.role,
            is_active=u.is_active, created_at=u.created_at.isoformat()
        )


class UserCreate(BaseModel):
    email: EmailStr
    name: str = Field(..., min_length=2)
    auth_provider: Literal["local", "microsoft"]
    role: Literal["admin", "user"] = "user"
    password: str | None = Field(default=None, min_length=8)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    role: Literal["admin", "user"] | None = None
    is_active: bool | None = None
    password: str | None = Field(default=None, min_length=8)


@router.get("/", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_only)
):
    result = await db.execute(select(User).order_by(User.created_at))
    return [UserOut.from_orm(u) for u in result.scalars().all()]


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    body: UserCreate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_only)
):
    existing = await db.execute(select(User).where(User.email == body.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="E-mail já cadastrado")

    if body.auth_provider == "local" and not body.password:
        raise HTTPException(status_code=422, detail="Senha obrigatória para login local")

    user = User(
        email=body.email,
        name=body.name,
        auth_provider=body.auth_provider,
        role=body.role,
        password_hash=hash_password(body.password) if body.password else None
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return UserOut.from_orm(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    body: UserUpdate,
    db: AsyncSession = Depends(get_db),
    _: dict = Depends(admin_only)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")

    if body.name is not None:
        user.name = body.name
    if body.role is not None:
        user.role = body.role
    if body.is_active is not None:
        user.is_active = body.is_active
    if body.password is not None:
        user.password_hash = hash_password(body.password)

    await db.commit()
    await db.refresh(user)
    return UserOut.from_orm(user)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: dict = Depends(admin_only)
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    if user.email == current["user_id"]:
        raise HTTPException(status_code=400, detail="Não é possível remover sua própria conta")
    await db.delete(user)
    await db.commit()
