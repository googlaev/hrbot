from aiogram import Bot, Dispatcher, types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.utils.keyboard import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import ReplyKeyboardRemove, Message, FSInputFile
import io
import asyncio
from aiogram import Router, F
from datetime import datetime, timedelta, time as datetime_time
import calendar
import time
import csv
from io import StringIO
from dateutil.relativedelta import relativedelta
import pytz

user_router = Router()

# =============================== Хендлеры команд ================================

@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Hello, user!")

@user_router.message(Command("help"))
async def cmd_help(message: types.Message):
    if message.chat.type in ['group', 'supergroup']:
        return
    
    try:
        help_text = (
            "📱 *Инструкция по использованию бота*\n\n"
            "🔹 *ОСНОВНОЕ МЕНЮ*\n"
            "├── 🔄 Обновить - обновить информацию\n"
            "├── 📅 График работы - показывает график работы\n"
            "├── 🛩️ Рейсы - показывает ваши рейсы\n"
            "└── 📋 ОТиТБ - показывает ваши экзамены\n\n"
            
            "🔹 *ГРАФИК РАБОТЫ*\n"
            "├── 🚨 Вахта - график вахт\n"
            "├── 🏖️ Отпуск - график отпусков\n"
            "├── 🤒 Больничный - больничные листы\n"
            "└── ✈️ Командировка - командировки\n\n"
            
            "🔹 *РЕЙСЫ*\n"
            "└── Просмотр информации о ваших рейсах\n\n"
            
            "🔹 *ОТиТБ*\n"
            "├── 📝 Отметить сдачу экзамена\n"
            "└── Просмотр сроков действия экзаменов\n\n"
            
            "🔹 *КОМАНДЫ БОТА*\n"
            "├── /start - начать работу с ботом\n"
            "└── /help - показать это сообщение\n\n"
            
            "🔹 *УВЕДОМЛЕНИЯ*\n"
            "• Бот автоматически уведомляет о:\n"
            "  - Приближающихся сроках экзаменов\n"
            "  - Новых назначенных рейсах\n"
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

# ============================ Заглушка колбэка =================================

@user_router.callback_query(F.data == "ignore")
async def ignore_callback(callback: types.CallbackQuery):
    """Игнорирует callback'и для неактивных кнопок"""
    await callback.answer()

