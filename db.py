from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete
from sqlmodel import SQLModel
import os
from dotenv import load_dotenv
from models import User, Project, UserProjectLink
from contextlib import asynccontextmanager

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_async_engine(DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def create_user(session: AsyncSession, name: str, pub_ssh: str = None):
    user = User(name=name, pub_ssh=pub_ssh)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

async def delete_user(session: AsyncSession, id: str):
    stmt = delete(User).where(User.id == id)
    await session.execute(stmt)
    await session.commit()

async def get_all_users(session: AsyncSession):
    stmt = select(User)
    result = await session.execute(stmt)
    users = result.scalars().all()

    return users

async def create_project(session: AsyncSession, name: str, ip: str = None):
    project = Project(name=name, ip=ip)
    session.add(project)
    await session.commit()
    await session.refresh(project)
    return project

async def get_all_projects(session: AsyncSession):
    stmt = select(Project)
    result = await session.execute(stmt)
    project = result.scalars().all()

    return project

async def connect_user_to_project(async_session: AsyncSession, user_id: int, project_id: int):
    async with async_session.begin():
        link = UserProjectLink(user_id=user_id, project_id=project_id)
        async_session.add(link)

    