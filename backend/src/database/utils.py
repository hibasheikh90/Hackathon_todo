from sqlmodel import select, func
from sqlalchemy.exc import IntegrityError
from typing import List, Optional, Generic, TypeVar, Type
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_


T = TypeVar('T')


class CRUDBase(Generic[T]):
    """Generic CRUD utility class for database operations"""

    def __init__(self, model: Type[T]):
        self.model = model

    def create(self, db: Session, obj: T) -> T:
        """Create a new record in the database"""
        try:
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except IntegrityError:
            db.rollback()
            raise

    def create_sync(self, db: Session, obj: T) -> T:
        """Create a new record in the database (sync version)"""
        try:
            db.add(obj)
            db.commit()
            db.refresh(obj)
            return obj
        except IntegrityError:
            db.rollback()
            raise

    def get_by_id(self, db: Session, id) -> Optional[T]:
        """Get a record by its ID"""
        from sqlmodel import select

        # Handle the case where id might be an empty dict, string representation of dict, or other unexpected type
        if id is None or id == {} or id == '{}' or (isinstance(id, str) and id.strip() == '{}'):
            return None

        # Convert to string for comparison, assuming string-based IDs
        id_str = str(id) if id is not None else ""

        statement = select(self.model).where(self.model.id == id_str)
        result = db.execute(statement)
        return result.scalar_one_or_none()

    def get_by_id_sync(self, db: Session, id) -> Optional[T]:
        """Get a record by its ID (sync version)"""
        from sqlmodel import select

        # Handle the case where id might be an empty dict, string representation of dict, or other unexpected type
        if id is None or id == {} or id == '{}' or (isinstance(id, str) and id.strip() == '{}'):
            return None

        # Convert to string for comparison, assuming string-based IDs
        id_str = str(id) if id is not None else ""

        statement = select(self.model).where(self.model.id == id_str)
        result = db.execute(statement)
        return result.scalar_one_or_none()

    def get_multi(
        self,
        db: Session,
        *,
        skip: int = 0,
        limit: int = 100
    ) -> List[T]:
        """Get multiple records with pagination"""
        statement = select(self.model).offset(skip).limit(limit)
        result = db.execute(statement)
        return result.scalars().all()

    def update(
        self,
        db: Session,
        *,
        db_obj: T,
        obj_update
    ) -> T:
        """Update a record in the database"""
        for field, value in obj_update.dict(exclude_unset=True).items():
            setattr(db_obj, field, value)

        try:
            db.commit()
            db.refresh(db_obj)
            return db_obj
        except IntegrityError:
            db.rollback()
            raise

    def remove(self, db: Session, *, id: int) -> T:
        """Remove a record from the database"""
        obj = self.get_by_id(db, id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj


from ..models.user import User
from ..models.task import Task


class UserCRUD(CRUDBase):
    """CRUD operations specific to User model"""

    def __init__(self):
        super().__init__(model=User)

    def get_by_email(self, db: Session, email: str):
        """Get a user by email"""
        statement = select(User).where(User.email == email)
        result = db.execute(statement)
        return result.scalar_one_or_none()

    def get_by_email_sync(self, db: Session, email: str):
        """Get a user by email (sync version)"""
        statement = select(User).where(User.email == email)
        result = db.execute(statement)
        return result.scalar_one_or_none()

    def get_by_id(self, db: Session, id) -> Optional[User]:
        """Get a user by their ID, handling string ID lookup"""
        from sqlmodel import select

        # Handle the case where id might be an empty dict, string representation of dict, or other unexpected type
        if id is None or id == {} or id == '{}' or (isinstance(id, str) and id.strip() == '{}'):
            return None

        if not isinstance(id, str):
            # Convert to string if it's not already
            id = str(id)

        statement = select(User).where(User.id == id)
        result = db.execute(statement)
        return result.scalar_one_or_none()

    def create_user(self, db: Session, user_data):
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
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise ValueError("Email already registered")

    def authenticate_user(self, db: Session, email: str, password: str):
        """Authenticate user with email and password"""
        from passlib.context import CryptContext

        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        user = self.get_by_email(db, email)

        if not user or not pwd_context.verify(password, user.password_hash):
            return None
        return user


class TaskCRUD(CRUDBase):
    """CRUD operations specific to Task model"""

    def __init__(self):
        super().__init__(model=Task)

    def get_tasks_by_user(
        self,
        db: Session,
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
        result = db.execute(statement)
        return result.scalars().all()

    def get_task_by_id_and_user(
        self,
        db: Session,
        task_id,
        user_id
    ) -> Optional[Task]:
        """Get a specific task by its ID and user ID"""
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = db.execute(statement)
        return result.scalar_one_or_none()

    def create_task_for_user(
        self,
        db: Session,
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
            db.commit()
            db.refresh(db_task)
            return db_task
        except IntegrityError:
            db.rollback()
            raise

    def update_task_for_user(
        self,
        db: Session,
        task_id,
        task_data,
        user_id
    ) -> Optional[Task]:
        """Update a task if it belongs to the specified user"""
        # First get the task to ensure it belongs to the user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = db.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            return None

        # Update the task with the new data
        for field, value in task_data.dict(exclude_unset=True).items():
            setattr(db_task, field, value)

        try:
            db.commit()
            db.refresh(db_task)
            return db_task
        except IntegrityError:
            db.rollback()
            raise

    def get_by_id(self, db: Session, id) -> Optional[Task]:
        """Get a task by its ID, handling string ID lookup"""
        from sqlmodel import select

        # Handle the case where id might be an empty dict, string representation of dict, or other unexpected type
        if id is None or id == {} or id == '{}' or (isinstance(id, str) and id.strip() == '{}'):
            return None

        if not isinstance(id, str):
            # Convert to string if it's not already
            id = str(id)

        statement = select(Task).where(Task.id == id)
        result = db.execute(statement)
        return result.scalar_one_or_none()

    def delete_task_for_user(
        self,
        db: Session,
        task_id,
        user_id
    ) -> bool:
        """Delete a task if it belongs to the specified user"""
        # First get the task to ensure it belongs to the user
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = db.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            return False

        try:
            db.delete(db_task)
            db.commit()
            return True
        except IntegrityError:
            db.rollback()
            return False


# Initialize the CRUD instances
user_crud = UserCRUD()
task_crud = TaskCRUD()