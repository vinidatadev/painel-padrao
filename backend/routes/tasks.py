from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_db
from models import Task
from auth import get_current_user

router = APIRouter(prefix="/tasks", tags=["tasks"])

# --- Schemas ---

class TaskOut(BaseModel):
    id: UUID
    user_id: str
    title: str
    is_completed: bool
    created_at: str

    @classmethod
    def from_orm(cls, task: Task):
        return cls(
            id=task.id,
            user_id=task.user_id,
            title=task.title,
            is_completed=task.is_completed,
            created_at=task.created_at.isoformat()
        )

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)

class TaskUpdate(BaseModel):
    is_completed: bool

# --- Rotas ---

@router.get("/", response_model=list[TaskOut])
async def list_tasks(
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    result = await db.execute(
        select(Task)
        .where(Task.user_id == current_user["user_id"])
        .order_by(Task.created_at.desc())
    )
    return [TaskOut.from_orm(t) for t in result.scalars().all()]


@router.post("/", response_model=TaskOut, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task = Task(title=body.title, user_id=current_user["user_id"])
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return TaskOut.from_orm(task)


@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: UUID,
    body: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task = await _get_own_task(db, task_id, current_user["user_id"])
    task.is_completed = body.is_completed
    await db.commit()
    await db.refresh(task)
    return TaskOut.from_orm(task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    task = await _get_own_task(db, task_id, current_user["user_id"])
    await db.delete(task)
    await db.commit()


async def _get_own_task(db: AsyncSession, task_id: UUID, user_id: str) -> Task:
    """Busca tarefa e garante que pertence ao usuário logado."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tarefa não encontrada")
    return task
