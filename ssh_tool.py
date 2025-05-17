from models import User, Project
from db import *
import asyncio
from sqlalchemy import select
import paramiko

async def connect_user(user_id, project_id):
    async with async_session_maker() as session:
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
    print (user.pub_ssh)
    key = user.pub_ssh.strip()
    #get user
    async with async_session_maker() as session:
        result = await session.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
    print (project.ip)
    host = project.ip
    password = '' # add password functionality
    host = host
    username='root'
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, port=22, look_for_keys=False,allow_agent=False,timeout=5)
    print(key)
    cmd = f"bash -c \"echo '{key}' >> /root/.ssh/authorized_keys\""
    ssh.exec_command(cmd)
    ssh.close()
