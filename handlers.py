from aiogram import Dispatcher, types, F
from aiogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup  # Імпортуємо StatesGroup та State
from telegram import CallbackQuery
from db import *
from models import User, Project

class CreateUserStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_ssh = State()

class CreateProjectStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_ip = State()

class ConnectUserToProject(StatesGroup):
    choosing_project = State()
    choosing_user = State()
# /start
async def tg_start(message: Message):
    await message.answer("""
     --Master SSH Start--
    USER:                     
    Create new user: /create_user
    Delete user: /delete_user
                         
    Project:
    Create Project: /create_project
                         
                         """)
# /create_user
async def tg_create_user(message: Message, state: FSMContext):
    await message.answer("Enter name:")
    await state.set_state(CreateUserStates.waiting_for_name)

async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip()) 
    await message.answer("Enter ssh:")
    await state.set_state(CreateUserStates.waiting_for_ssh) 

async def process_ssh(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    ssh = message.text.strip()

    async with AsyncSessionLocal() as session:
        stmt = select(User).where(User.name == name)
        result = await session.execute(stmt)
        exists = result.scalar_one_or_none() is not None

        if exists:
            await message.answer("Error! User with this name already exists. Please try again")
        else:
            await create_user(session, name, ssh)
            await message.answer(f"User {name} is created.")
    
    await state.clear()

# /delete_user
async def tg_delete_user(message: Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        users = await get_all_users(session)
        if not users:
            await message.answer("User list is empty. To create new user, click /create_user.")
            return
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=user.name, callback_data=f"delete_user:{user.id}")]
                for user in users
            ]
        )
        await message.answer("Оберіть користувача для видалення:", reply_markup=keyboard)

async def delete_user_callback(callback: CallbackQuery):

    user_id = int(callback.data.split(":")[1])
    async with AsyncSessionLocal() as session:
        await delete_user(session, user_id)
    await callback.message.edit_text("Користувача видалено.")

# /create_project
async def tg_create_project(message: Message, state: FSMContext):
    await message.answer("Enter project name:")
    await state.set_state(CreateProjectStates.waiting_for_name)

async def process_project_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await message.answer("Enter ip:")
    await state.set_state(CreateProjectStates.waiting_for_ip)

async def process_project_ip(message: Message, state: FSMContext):
    data = await state.get_data()
    name = data["name"]
    ip = message.text.strip()

    async with AsyncSessionLocal() as session:
        stmt = select(Project).where(Project.name == name)
        result = await session.execute(stmt)
        exists = result.scalar_one_or_none() is not None

        if exists:
            await message.answer("Error! User with this project already exists. Please try again")
        else:
            await create_project(session, name, ip)
            await message.answer(f"Project {name} is created: {ip}")
    
    await state.clear()

async def tg_select_user(message: Message, state: FSMContext):
    async with AsyncSessionLocal() as session:
        users = await get_all_users(session)
        if not users:
            await message.answer("User list is empty. To create new user, click /create_user.")
            return
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[  
                [InlineKeyboardButton(text=user.name, callback_data=f"select_user:{user.id}")]
                for user in users
            ]
        )
        await message.answer("Choose user:", reply_markup=keyboard)
        await state.set_state(ConnectUserToProject.choosing_user)

async def tg_select_project(callback: CallbackQuery, state: FSMContext): 
    user_id = int(callback.data.split(":")[1]) 
    await state.update_data(user_id=user_id) 
    async with AsyncSessionLocal() as session:
        projects = await get_all_projects(session)

    if not projects:
        await callback.message.edit_text("No projects.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[ 
            [InlineKeyboardButton(text=p.name, callback_data=f"select_project:{p.id}")]
            for p in projects
        ]
    )

    await callback.message.edit_text("Choose project:", reply_markup=keyboard)
    await state.set_state(ConnectUserToProject.choosing_project)

async def on_project_selected(callback: CallbackQuery, state: FSMContext):
    async with AsyncSessionLocal() as session:
        try:
            project_id = int(callback.data.split(":")[1]) 
        except (IndexError, ValueError):
            await callback.message.edit_text("Error: invalid project selection.")
            await state.clear()
            return
        
        data = await state.get_data()
        user_id = data.get("user_id")  
        print(user_id)

        if not user_id:
            await callback.message.edit_text("Error: user not selected.")
            await state.clear()
            return

        await connect_user_to_project(session, user_id, project_id) 
        await callback.message.edit_text(f"User {user_id} connected to project {project_id}.")
        await state.clear()


def register_handlers(dp: Dispatcher):
    dp.message.register(tg_start, Command("start"))
    dp.message.register(tg_create_user, Command("create_user"))
    dp.message.register(tg_delete_user, Command("delete_user"))
    dp.message.register(tg_create_project, Command("create_project"))
    dp.message.register(tg_select_user, Command("connect_user"))

    dp.message.register(process_name, StateFilter(CreateUserStates.waiting_for_name))
    dp.message.register(process_ssh, StateFilter(CreateUserStates.waiting_for_ssh))
    dp.message.register(process_project_name, StateFilter(CreateProjectStates.waiting_for_name))
    dp.message.register(process_project_ip, StateFilter(CreateProjectStates.waiting_for_ip))


    dp.callback_query.register(delete_user_callback, F.data.startswith("delete_user:"))
    dp.callback_query.register(tg_select_project, StateFilter(ConnectUserToProject.choosing_user), F.data.startswith("select_user:"))
    dp.callback_query.register(on_project_selected, StateFilter(ConnectUserToProject.choosing_project), F.data.startswith("select_project:"))


