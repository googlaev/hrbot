import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.app_actions import AppActions
from infra.logging import get_logger

user_router = Router()

# ============================ Хендлеры команд ============================
@user_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Список тестов"), types.KeyboardButton(text="Рейтинг тестов")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Привет, пользователь!", reply_markup=keyboard)

@user_router.message(Command("help"))
async def help_quiz(message: types.Message):
    help_text = (
        "📌 *Инструкция пользователя:*\n\n"
        "/quiz - Посмотреть доступные тесты\n"
        "Выберите тест и отвечайте на вопросы, нажимая кнопки с вариантами.\n"
        "Если вы хотите завершить тест досрочно, нажмите кнопку 'Завершить'.\n\n"
        "После окончания теста вы увидите количество правильных ответов и время прохождения."
    )
    await message.answer(help_text, parse_mode="Markdown")

@user_router.message(F.text == "Список тестов")
async def cmd_quiz(message: types.Message, actions: AppActions):
    quizzes = await actions.quiz_list.execute()
    if not quizzes:
        await message.answer("На данный момент нет доступных тестов.")
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"{q.id} - {q.title}", callback_data=f"quiz|{q.id}")]
            for q in quizzes
        ]
    )
    await message.answer("Выберите тест:", reply_markup=keyboard)

@user_router.message(F.text == "Рейтинг тестов")
async def rating_tests(tg_object: types.Message | types.CallbackQuery, actions: AppActions):
    quizzes = await actions.quiz_list.execute()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"{q.id} - {q.title}",
                callback_data=f"rating_quiz|{q.id}"
            )]
            for q in quizzes
        ]
    )

    if isinstance(tg_object, types.Message):
        if not quizzes:
            await tg_object.answer("Пока нет тестов.")
            return
        await tg_object.answer("Выберите тест для просмотра рейтинга:", reply_markup=keyboard)
    else:
        await tg_object.message.edit_text("Выберите тест для просмотра рейтинга:", reply_markup=keyboard)

@user_router.callback_query(F.data == "rating_back")
async def rating_back(callback: types.CallbackQuery, actions: AppActions):
    await rating_tests(callback, actions)