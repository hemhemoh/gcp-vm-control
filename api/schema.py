from sqlmodel import Field, Relationship, Session, SQLModel, create_engine
from datetime import datetime
from typing import Optional
from core.enums import OperationStatus, OperationType
from sqlalchemy.orm import relationship

class ParentJob(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    zone: str = Field(index=True)
    status: OperationStatus = Field(index=True)
    type: OperationType = Field(index=True)
    is_successful: bool = Field(default=False, index=True)

    children: list["ChildJob"] = Relationship(back_populates="parent",
    sa_relationship=relationship("ChildJob", back_populates="parent"))
    
class ParentJobPublic(ParentJob):
    model_config = {"table": False}
    children: list["ChildJob"] = []
    
class ChildJob(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    is_successful: bool = Field(default=False, index=True)
    request_time: Optional[datetime] = None  
    start_time: Optional[datetime] = None 
    end_time: Optional[datetime] = None  

    parent_id: int | None = Field(default=None, foreign_key="parentjob.id")
    parent: ParentJob | None = Relationship(back_populates="children",
    sa_relationship=relationship("ParentJob", back_populates="children"))
    

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
