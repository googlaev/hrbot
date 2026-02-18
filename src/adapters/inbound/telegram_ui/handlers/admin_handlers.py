from aiogram import Bot, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import io
from aiogram import Router
from datetime import datetime
import pytz
from dateutil.relativedelta import relativedelta
import asyncio
from app.app_actions import AppActions

admin_router = Router()

# ============================ Хендлеры команд ============================

@admin_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello, admin!")

@admin_router.message(Command("help"))
async def cmd_help(message: types.Message):
    try:
        help_text = (
            "📱 *Панель администратора*\n\n"
            "🔹 *ОСНОВНОЕ МЕНЮ*\n"
            "├── 👤 Персонал - управление сотрудниками\n"
            "├── 🛩️ Рейсы - управление рейсами\n"
            "└── 📋 ОТиТБ - управление экзаменами\n\n"
            
            "🔹 *УПРАВЛЕНИЕ ПЕРСОНАЛОМ*\n"
            "├── Просмотр статусов сотрудников\n"
            "├── Фильтрация по участкам\n"
            "├── Просмотр графика работы\n"
            "└── Управление экзаменами сотрудников\n\n"
            
            "🔹 *УПРАВЛЕНИЕ РЕЙСАМИ*\n"
            "├── ➕ Добавление новых рейсов\n"
            "├── 🗑️ Удаление рейсов\n"
            "├── 📅 Фильтрация по датам\n"
            "└── 🏢 Фильтрация по участкам\n\n"
            
            "🔹 *УПРАВЛЕНИЕ ОТиТБ*\n"
            "└── ⚠️ Просмотр истекающих экзаменов\n"
            
            "🔹 *ЗАГРУЗКА ДАННЫХ*\n"
            "├── Загрузка Excel-файлов с данными\n"
            "└── Таблица пользователей и график работы\n\n"
            
            "🔹 *КОМАНДЫ БОТА*\n"
            "├── /start - начать работу с ботом\n"
            "├── /help - показать это сообщение\n"
            
            "🔹 *УВЕДОМЛЕНИЯ*\n"
            "• Система автоматически отправляет:\n"
            "  - Уведомления об истекающих экзаменах\n"
        )
        
        await message.answer(
            help_text,
            parse_mode="Markdown"
        )

        await message.delete()
    except Exception as e:
        await message.answer(
            "❌ Произошла ошибка при отправке справки. Попробуйте позже.",
        )

# ========================= Обработка файлов ============================

@admin_router.message(F.document)
async def handle_document(message: Message, bot: Bot, actions: AppActions, user_id: int):
    document = message.document
    if not document:
        await message.answer("Нет документа")
        return

    if document.mime_type != "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
        await message.answer("Пожалуйста, отправьте файл формата .xlsx")
        return

    mess = await message.answer("Файл получен. Начинаю обработку...")

    file = await bot.get_file(document.file_id)
    file_data = await bot.download_file(file.file_path)
    
    quiz = await actions.add_quiz_from_excel.execute(file_data.getvalue())

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="ОК", callback_data="close")]]
    )

    message = f"Name test: {quiz.title}\n id test: {quiz.id}"

    await mess.edit_text(message, reply_markup=keyboard)

# ============================ Заглушка колбэка =================================

@admin_router.callback_query(F.data == "ignore")
async def ignore_callback(callback: types.CallbackQuery):
    """Игнорирует callback'и для неактивных кнопок"""
    await callback.answer()
