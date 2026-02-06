from sqlmodel import select, func
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Generic, TypeVar, Type
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, or_
from backend.src.models.user import User
from backend.src.models.task import Task


T = TypeVar('T')


class AsyncCRUDBase(Generic[T]):
    """Generic async CRUD utility class for database operations"""

    def __init__(self, model: Type[T]):
        self.model = model

    async def create(self, db: AsyncSession, obj: T) -> T:
        """Create a new record in the database"""
        try:
            db.add(obj)
            await db.commit()
            await db.refresh(obj)
            return obj
        except IntegrityError:
            await db.rollback()
            raise

    async def get_by_id(self, db: AsyncSession, id) -> Optional[T]:
        """Get a record by its ID"""
        from sqlmodel import select

        # Handle the case where id might be an empty dict, string representation of dict, or other unexpected type
        if id is None or id == {} or id == '{}' or (isinstance(id, str) and id.strip() == '{}'):
            return None

        # Convert to string for comparison, assuming string-based IDs
        id_str = str(id) if id is not None else ""

        statement = select(self.model).where(self.model.id == id_str)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        db: AsyncSession,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[T]:
        """Get multiple records with pagination"""
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: T,
        obj_update
    ) -> T:
        """Update a record in the database"""
        for field, value in obj_update.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)

        try:
            await db.commit()
            await db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            await db.rollback()
            raise

    async def remove(self, db: AsyncSession, *, id: int) -> T:
        """Remove a record from the database"""
        obj = await self.get_by_id(db, id)
        if obj:
            db.delete(obj)
            await db.commit()
        return obj


class AsyncUserCRUD(AsyncCRUDBase):
    """Async CRUD operations specific to User model"""

    def __init__(self):
        super().__init__(model=User)

    async def get_by_email(self, db: AsyncSession, email: str):
        """Get a user by email"""
        statement = select(User).where(User.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def get_by_id(self, db: AsyncSession, id) -> Optional[User]:
        """Get a user by their ID, handling string ID lookup"""
        from sqlmodel import select

        # Handle the case where id might be an empty dict, string representation of dict, or other unexpected type
        if id is None or id == {} or id == '{}' or (isinstance(id, str) and id.strip() == '{}'):
            return None

        if not isinstance(id, str):
            # Convert to string if it's not already
            id = str(id)

        statement = select(User).where(User.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create_user(self, db: AsyncSession, user_data):
        """Create a new user with password hashing"""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

        hashed_password = pwd_context.hash(user_data.password)
        db_user = User(
            email=user_data.email,
            password_hash=hashed_password
        )

        try:
            db.add(db_user)
            await db.commit()
            await db.refresh(db_user)
            return db_user
        except IntegrityError:
            await db.rollback()
            raise ValueError("Email already registered")

    async def authenticate_user(self, db: AsyncSession, email: str, password: str):
        """Authenticate user with email and password"""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user = await self.get_by_email(db, email)

        if not user or not pwd_context.verify(password, user.password_hash):
            return None
        return user


class AsyncTaskCRUD(AsyncCRUDBase):
    """Async CRUD operations specific to Task model"""

    def __init__(self):
        super().__init__(model=Task)

    async def get_tasks_by_user(
        self,
        db: AsyncSession,
        user_id,
        *,
        skip: int = 0,
        limit: int = 100,
        completed: Optional[bool] = None
    ) -> List:
        """Get all tasks for a specific user with optional filters"""
        statement = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            statement = statement.where(Task.is_completed == completed)

        statement = statement.offset(skip).limit(limit)
        result = await db.execute(statement)
        return result.scalars().all()

    async def get_task_by_id_and_user(
        self,
        db: AsyncSession,
        task_id,
        user_id
    ) -> Optional[Task]:
        """Get a specific task by its ID and user ID"""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create_task_for_user(
        self,
        db: AsyncSession,
        task_data,
        user_id
    ):
        """Create a new task for a specific user"""
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            is_completed=getattr(task_data, 'is_completed', False),
            user_id=user_id
        )

        try:
            db.add(db_task)
            await db.commit()
            await db.refresh(db_task)
            return db_task
        except IntegrityError:
            await db.rollback()
            raise

    async def update_task_for_user(
        self,
        db: AsyncSession,
        task_id,
        task_data,
        user_id
    ) -> Optional[Task]:
        """Update a task if it belongs to the specified user"""
        # First get the task to ensure it belongs to the user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await db.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            return None

        # Update the task with the new data
        for field, value in task_data.dict(exclude_unset=True).items():
            setattr(db_task, field, value)

        try:
            await db.commit()
            await db.refresh(db_task)
            return db_task
        except IntegrityError:
            await db.rollback()
            raise

    async def get_by_id(self, db: AsyncSession, id) -> Optional[Task]:
        """Get a task by its ID, handling string ID lookup"""
        from sqlmodel import select

        # Handle the case where id might be an empty dict, string representation of dict, or other unexpected type
        if id is None or id == {} or id == '{}' or (isinstance(id, str) and id.strip() == '{}'):
            return None

        if not isinstance(id, str):
            # Convert to string if it's not already
            id = str(id)

        statement = select(Task).where(Task.id == id)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def delete_task_for_user(
        self,
        db: AsyncSession,
        task_id,
        user_id
    ) -> bool:
        """Delete a task if it belongs to the specified user"""
        # First get the task to ensure it belongs to the user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await db.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            return False

        try:
            db.delete(db_task)
            await db.commit()
            return True
        except IntegrityError:
            await db.rollback()
            return False


# Initialize the async CRUD instances
async_user_crud = AsyncUserCRUD()
async_task_crud = AsyncTaskCRUD()