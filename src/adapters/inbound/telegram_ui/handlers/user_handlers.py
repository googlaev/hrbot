import asyncio
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.app_actions import AppActions
from infra.logging import get_logger

user_router = Router()

# ================== FSM States ==================
class QuizStates(StatesGroup):
    waiting_for_name = State()
    in_quiz = State()
    finished = State()

# ============================ Хендлеры команд ============================
@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет! Команда /quiz чтобы увидеть доступные тесты.")

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

@user_router.message(Command("quiz"))
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

# ================== Quiz selection ==================
@user_router.callback_query(F.data.startswith("quiz|"))
async def quiz_select(callback: types.CallbackQuery, user_id: int, state: FSMContext, actions: AppActions):
    message = callback.message
    if message is None or not isinstance(message, types.Message):
        return
    
    callback_data = callback.data
    if callback_data is None:
        return
    
    quiz_id = int(callback_data.split("|")[1])

    result = await actions.start_quiz.execute(user_id, quiz_id)

    if result.get("limit_reached"):
        await callback.answer("Вы уже проходили этот тест сегодня!", show_alert=True)
        return
    
    await callback.answer()
    message = await message.answer("Загрузка...")

    if result.get("requires_name"):
        await message.edit_text("Укажите как к вам обращаться:")
        await state.set_state(QuizStates.waiting_for_name)
        await state.update_data(quiz_id=quiz_id)
        await state.update_data(quiz_message=message)
        return
    
    
    quiz_session = result["quiz_session"]
    await state.set_state(QuizStates.in_quiz)
    await state.update_data(session_id=quiz_session.id)

    await start_quiz_polling(
        message=message, 
        state=state,
        actions=actions, 
    )

# ================== Handle name input ==================
@user_router.message(QuizStates.waiting_for_name)
async def set_name(message: types.Message, user_id: int, state: FSMContext, actions: AppActions):
    message_text = message.text
    if message_text is None:
        return
    
    name = message_text.strip()

    await actions.set_user_name.execute(user_id, name)

    data = await state.get_data()
    quiz_id = data["quiz_id"]
    quiz_message = data["quiz_message"]

    result = await actions.start_quiz.execute(user_id, quiz_id)
    quiz_session = result["quiz_session"]

    await state.set_state(QuizStates.in_quiz)
    await state.update_data(session_id=quiz_session.id)

    await start_quiz_polling(
        message=quiz_message, 
        state=state,
        actions=actions, 
    )

    await message.delete()

# ================== Answer click ==================
@user_router.callback_query(F.data.startswith("answer|"), QuizStates.in_quiz)
async def handle_answer(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    message = callback.message
    if message is None or not isinstance(message, types.Message):
        return
    
    callback_data = callback.data
    if callback_data is None:
        return
    
    display_index = int(callback_data.split("|")[1])

    data = await state.get_data()
    session_id = data["session_id"]
    answer_map = data["answer_map"]
    answer_index = answer_map[display_index]

    await actions.submit_answer.execute(session_id, answer_index)
    await callback.answer("Ответ принят! Готовим следующий вопрос...")

async def start_quiz_polling(message: types.Message, state: FSMContext, actions: AppActions):
    logger = get_logger("quiz_polling")

    data = await state.get_data()
    session_id = data["session_id"]

    async def poll():
        try:
            while True:
                result = await actions.get_current_question.execute(session_id)

                if result.finished:
                    # завершение теста
                    finish_result = await actions.finish_quiz.execute(session_id)
                    duration = finish_result.finished_at - finish_result.started_at
                    minutes, seconds = divmod(duration.seconds, 60)

                    await message.edit_text(
                        f"🎉 Тест завершён!\n"
                        f"Результат: {finish_result.correct}/{finish_result.total}\n"
                        f"Время: {minutes:02d}:{seconds:02d}"
                    )
                    await state.clear()
                    break

                options = result.options
                remaining = result.remaining_seconds

                mapping = {opt.display_index: opt.index for opt in options}
                await state.update_data(answer_map=mapping)

                options_text = "\n".join(
                    f"{opt.display_index + 1}) {opt.text}\n" for opt in options
                )

                message_text = (
                    f"({result.question_index}/{result.total_questions}) *{result.question_text}*\n\n"
                    f"{options_text}\n"
                    f"Осталось: *{remaining}* секунд"
                )

                # клавиатура
                keyboard = InlineKeyboardMarkup(
                    inline_keyboard=[
                        [
                            InlineKeyboardButton(
                                text=str(opt.display_index + 1),
                                callback_data=f"answer|{opt.display_index}"
                            )
                            for opt in options
                        ],
                        [InlineKeyboardButton(text="Завершить", callback_data="finish_now")]
                    ]
                )

                try:
                    await message.edit_text(
                        message_text,
                        reply_markup=keyboard,
                        parse_mode="Markdown"
                    )
                except Exception:
                    pass

                await asyncio.sleep(3)
        except Exception as e:
            logger.error(e)

    asyncio.create_task(poll())

@user_router.callback_query(F.data == "finish_now", QuizStates.in_quiz)
async def finish_now(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    data = await state.get_data()
    session_id = data["session_id"]

    await actions.finish_quiz.execute(session_id)

    await state.clear()

    await callback.answer("Завершаем тестирование...")

