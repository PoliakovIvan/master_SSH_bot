from models import User, Project
from db import *
import asyncio
from sqlalchemy import select
import paramiko
import re

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

async def disconnect_user(user_id):
    async with async_session_maker() as session:
        result = await session.execute(
            select(UserProjectLink).where(UserProjectLink.user_id == user_id)
        )
        user_project = result.scalars().all()

        user_result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = user_result.scalar_one_or_none()

    for item in user_project:
        async with async_session_maker() as session:
            result = await session.execute(
                select(Project).where(Project.id == item.project_id)
            )
            print('id:', item.project_id)
            project = result.scalar_one_or_none()
        print(project)
        pattern = re.escape(user.pub_ssh)
        
        host = project.ip
        password = '' # add password functionality
        host = host
        username='root'
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(hostname=host, username=username, password=password, port=22, look_for_keys=False,allow_agent=False,timeout=5)
        cmd = f"sed -i '\\|{user.pub_ssh}|d' /root/.ssh/authorized_keys"
        print(user.pub_ssh)
        stdin, stdout, stderr = ssh.exec_command(cmd)
        err = stderr.read().decode()
        if err:
            print("Error:", err)
        ssh.close()
    async with AsyncSessionLocal() as session:
        await delete_user(session, user.id)

if __name__ == '__main__':
    asyncio.run(disconnect_user(4))