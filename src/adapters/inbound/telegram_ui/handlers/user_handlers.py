from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.app_actions import AppActions

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
    if result.get("requires_name"):
        await message.edit_text("Укажите как к вам обращаться:")
        await state.set_state(QuizStates.waiting_for_name)
        await state.update_data(quiz_id=quiz_id)
        await state.update_data(quiz_message=message)
        return
    
    if result.get("limit_reached"):
        await callback.answer("Вы уже проходили этот тест сегодня!", show_alert=True)
        return
    
    quiz_session = result["quiz_session"]
    await state.set_state(QuizStates.in_quiz)
    await state.update_data(session_id=quiz_session.id)

    await send_question(
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

    await send_question(
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
    
    answer_index = int(callback_data.split("|")[1])
    data = await state.get_data()
    session_id = data["session_id"]

    finish = await actions.submit_answer.execute(session_id, answer_index)

    if finish.is_finished:
        duration = finish.finished_at - finish.started_at
        minutes, seconds = divmod(duration.seconds, 60)

        await message.edit_text(
            f"🎉 Тест завершен!\n"
            f"Результат: *{finish.correct}/{finish.total}*\n"
            f"Время прохождения: *{minutes:02d}:{seconds:02d}*",
            parse_mode="Markdown"
        )

        await state.clear()
        return

    # fetch updated current question
    await send_question(
        message=message, 
        state=state,
        actions=actions, 
    )

async def send_question(
    *,
    message: types.Message,
    state: FSMContext,
    actions: AppActions
):
    data = await state.get_data()
    session_id = data["session_id"]

    question = await actions.get_current_question.execute(session_id)

    if question is None:
        await message.answer("Ошибка: больше нет вопросов.")
        return

    options_text = "\n".join([f"{i+1}) {opt}\n" for i, opt in enumerate(question.options)])

    message_text = f"*{question.number}. {question.question_text}*\n\n{options_text}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=str(i+1), callback_data=f"answer|{i}") for i in range(len(question.options))],
            [InlineKeyboardButton(text="Завершить", callback_data="finish_now")]
        ]
    )

    await message.edit_text(
        message_text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

@user_router.callback_query(F.data == "finish_now", QuizStates.in_quiz)
async def finish_now(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    data = await state.get_data()
    session_id = data["session_id"]

    # call UC
    result = await actions.finish_quiz.execute(session_id)

    duration = result.finished_at - result.started_at
    minutes, seconds = divmod(duration.seconds, 60)

    await callback.message.edit_text(
        f"Тест завершён досрочно\n"
        f"Результат: {result.correct}/{result.total}\n"
        f"Время: {minutes:02d}:{seconds:02d}"
    )

    await state.clear()
