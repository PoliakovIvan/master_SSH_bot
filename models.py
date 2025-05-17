from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Table, Column, Integer, ForeignKey

class UserProjectLink(SQLModel, table=True):
    user_id: int = Field(foreign_key="user.id", primary_key=True)
    project_id: int = Field(foreign_key="project.id", primary_key=True)


class User(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    pub_ssh: str

    projects: list["Project"] = Relationship(back_populates="users", link_model=UserProjectLink)


class Project(SQLModel, table=True):# add password functionality
    id: int = Field(default=None, primary_key=True)
    name: str
    ip: str

    users: list[User] = Relationship(back_populates="projects", link_model=UserProjectLink)