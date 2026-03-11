from aiogram import Bot, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Router
from aiogram.types import BufferedInputFile
from aiogram.fsm.state import StatesGroup, State

from app.app_actions import AppActions

admin_router = Router()

class AddQuiz(StatesGroup):
    waiting_for_file = State()

class QuizSettingsStates(StatesGroup):
    waiting_for_new_question_count = State()
    waiting_for_new_attempt_limit = State()

# ============================ Хендлеры команд ============================

@admin_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="Посмотреть тесты"), types.KeyboardButton(text="Добавить тест")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    await message.answer("Привет, администратор!", reply_markup=keyboard)

@admin_router.message(Command("help"))
async def admin_help(message: Message):
    help_text = (
        "📌 *Инструкция администратора:*\n\n"
        "/quiz - Меню управления тестами\n"
        "/add\\_quiz - Добавить новый тест через .xlsx файл\n\n"
        "*Функции меню теста:*\n"
        "- Просмотр всех попыток пользователей\n"
        "- Удаление теста\n"
        "- Экспорт результатов в Excel\n\n"
    )

    await message.answer(help_text, parse_mode="Markdown")

@admin_router.message(F.text == "Посмотреть тесты")
async def list_quizzes(tg_object: types.Message | types.CallbackQuery, state: FSMContext, actions: AppActions):
    await state.clear()
    quizzes = await actions.quiz_list.execute()

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"(id: {q.id}) {q.title}", callback_data=f"quiz_menu|{q.id}")] for q in quizzes
        ]
    )

    await state.update_data(menu_stack=["list_quiz"])

    if isinstance(tg_object, types.Message):
        if not quizzes:
            await tg_object.answer("Тестов пока нет.")
            return
        await tg_object.answer("Список тестов:", reply_markup=keyboard)
    else:
        await tg_object.message.edit_text("Список тестов:", reply_markup=keyboard)

@admin_router.message(F.text == "Добавить тест")
async def show_add_quiz_menu(message: types.Message, state: FSMContext):
    await state.set_state(AddQuiz.waiting_for_file)
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="Шаблон Excel", callback_data="template_excel"), 
             types.InlineKeyboardButton(text="Шаблон CSV", callback_data="template_csv")]
        ]
    )
    await message.answer(
        "Отправьте файл с тестом (Excel, CSV):",
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data.startswith("quiz_menu|"))
async def quiz_menu(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    await state.set_state(None)

    quiz_id: int | None = None

    if callback.data and "|" in callback.data:
        parts = callback.data.split("|")
        if len(parts) > 1 and parts[1].isdigit():
            quiz_id = int(parts[1])
    
    data = await state.get_data()

    if quiz_id is None:
        data = await state.get_data()
        quiz_id = data.get("selected_quiz_id")
    
    menu_stack = data.get("menu_stack", [])
    menu_stack.append("quiz_menu")
    await state.update_data(menu_stack=menu_stack)

    await state.update_data(selected_quiz_id=quiz_id)

    quiz = await actions.get_quiz.execute(quiz_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Просмотр всех попыток", callback_data="view_attempts")],
            [InlineKeyboardButton(text="Пройти тест", callback_data=f"quiz|{quiz_id}")],
            [InlineKeyboardButton(text=f"Кол-во вопросов: {quiz.question_count}", callback_data=f"edit_qcount|{quiz_id}")],
            [InlineKeyboardButton(text=f"Кол-во попыток в день: {quiz.daily_attempt_limit}", callback_data=f"edit_attempts|{quiz_id}")],
            [InlineKeyboardButton(text="Удалить тест", callback_data="delete_quiz")],
            [InlineKeyboardButton(text="Назад", callback_data="back")],
        ]
    )

    await callback.message.edit_text(
        text=f"(id: {quiz_id}) Тест: `{quiz.title}`", 
        parse_mode="Markdown",
        reply_markup=keyboard
    )

# ========================= Quiz settings ==============================
@admin_router.callback_query(F.data.startswith("edit_qcount|"))
async def edit_question_count(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    quiz_id = int(callback.data.split("|")[1])

    await state.update_data(edit_quiz_id=quiz_id)
    await state.update_data(quiz_menu_callback=callback)
    await state.set_state(QuizSettingsStates.waiting_for_new_question_count)

    data = await state.get_data()
    menu_stack = data.get("menu_stack", [])
    menu_stack.append("edit_question_menu")
    await state.update_data(menu_stack=menu_stack)

    quiz = await actions.get_quiz.execute(quiz_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=f"quiz_menu|{quiz_id}")]
        ]
    )

    await callback.message.edit_text(
        text=f"Введите кол-во вопросов в тесте(1-{quiz.questions_len}):",
        reply_markup=keyboard
    )

@admin_router.message(QuizSettingsStates.waiting_for_new_question_count)
async def set_new_question_count(message: types.Message, state: FSMContext, actions: AppActions):
    if not message.text.isdigit():
        await message.reply("Введите число.")
        return
    
    value = int(message.text)
    data = await state.get_data()
    quiz_id = data["edit_quiz_id"]

    await actions.quiz_settings.update_quiz_question_count(quiz_id, value)

    callback = data["quiz_menu_callback"]

    await back_callback(callback, state, actions)
    await message.delete()

@admin_router.callback_query(F.data.startswith("edit_attempts|"))
async def edit_attempts_limit(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    quiz_id = int(callback.data.split("|")[1])

    await state.update_data(edit_quiz_id=quiz_id)
    await state.update_data(quiz_menu_callback=callback)
    await state.set_state(QuizSettingsStates.waiting_for_new_attempt_limit)

    data = await state.get_data()
    menu_stack = data.get("menu_stack", [])
    menu_stack.append("edit_question_menu")
    await state.update_data(menu_stack=menu_stack)
    
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Назад", callback_data=f"quiz_menu|{quiz_id}")]
        ]
    )

    await callback.message.edit_text(
        text="Введите макс. кол-во попыток в день(1-100):",
        reply_markup=keyboard
    )

@admin_router.message(QuizSettingsStates.waiting_for_new_attempt_limit)
async def set_new_daily_attempt_limit(message: types.Message, state: FSMContext, actions: AppActions):
    if not message.text.isdigit():
        await message.reply("Введите число.")
        return
    
    value = int(message.text)
    data = await state.get_data()
    quiz_id = data["edit_quiz_id"]

    await actions.quiz_settings.update_quiz_attempt_limit(quiz_id, value)

    callback = data["quiz_menu_callback"]

    await back_callback(callback, state, actions)
    await message.delete()

@admin_router.callback_query(F.data.startswith("view_attempts"))
async def view_attempts(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    data = await state.get_data()
    
    menu_stack = data.get("menu_stack", [])
    menu_stack.append("view_attempts")
    await state.update_data(menu_stack=menu_stack)

    quiz_id = data.get("selected_quiz_id")
    if not quiz_id:
        await callback.answer("Ошибка: не выбран тест", show_alert=True)
        return

    quizzes = await actions.get_completed_quizzes.execute(quiz_id)

    text = "📊 Все попытки:\n\n"

    if not quizzes:
        text += "Нет завершенных попыток для этого теста."

    for q in quizzes:
        percent = q.percent
        start_str = q.started_at.strftime("%d %b %Y %H:%M")
        finish_str = q.finished_at.strftime("%d %b %Y %H:%M")
        text += (f"👤 (id: {q.user_id}) {q.name}\n"
                 f"Правильность ответов: {q.correct}/{q.total} ({percent:.1f}%)\n"
                 f"Пройден - с: {start_str}  по: {finish_str}\n\n")

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Экспорт попыток в Excel", callback_data="export_attempts")],
            [InlineKeyboardButton(text="Назад", callback_data="back")],
        ]
    )

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data.startswith("delete_quiz"))
async def delete_quiz(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quiz_id = data["selected_quiz_id"]
    
    menu_stack = data.get("menu_stack", [])
    menu_stack.append("delete_quiz")
    await state.update_data(menu_stack=menu_stack)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="delete_confirm")],
            [InlineKeyboardButton(text="Нет", callback_data="back")]
        ]
    )
    await callback.message.edit_text(f"Вы уверены, что хотите удалить тест {quiz_id}?", reply_markup=keyboard)

@admin_router.callback_query(F.data.startswith("delete_confirm"))
async def delete_confirm(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    data = await state.get_data()
    quiz_id = data["selected_quiz_id"]

    await actions.delete_quiz.execute(quiz_id)

    await list_quizzes(callback.message, state, actions)
    await callback.message.delete()

@admin_router.callback_query(F.data.startswith("export_attempts"))
async def export_attempts(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    data = await state.get_data()
    quiz_id = data["selected_quiz_id"]

    file_bytes = await actions.excel_export_attempts.execute(quiz_id)
    if file_bytes is None:
        await callback.answer("Нет прохождений теста для экспорта", show_alert=True)
        return

    tg_file = BufferedInputFile(
        file_bytes,
        filename=f"quiz_{quiz_id}_results.xlsx"
    )

    await callback.message.answer_document(tg_file)
    await callback.answer()

@admin_router.callback_query(F.data.startswith("back"))
async def back_callback(callback: types.CallbackQuery, state: FSMContext, actions: AppActions):
    data = await state.get_data()
    menu_stack = data.get("menu_stack", [])
    if len(menu_stack) <= 1:
        await callback.answer("Вы уже в главном меню", show_alert=True)
        return
    
    previous_menu = menu_stack[-2]
    menu_stack = menu_stack[:-2]
    await state.update_data(menu_stack=menu_stack)

    # Render previous menu based on type
    if previous_menu == "list_quiz":
        await list_quizzes(callback, state, actions)
    elif previous_menu == "quiz_menu":
        await quiz_menu(callback, state, actions)

# ========================= Обработка файлов ============================

@admin_router.message(AddQuiz.waiting_for_file, F.document)
async def add_quiz_file(
    message: Message,
    bot: Bot,
    state: FSMContext,
    actions: AppActions,
    user_id: int
):
    document = message.document
    if not document:
        await message.answer("Нет документа")
        return

    mess = await message.answer("Файл получен. Начинаю обработку...")

    file = await bot.get_file(document.file_id)
    file_data = await bot.download_file(file.file_path)  # type: ignore
    content = file_data.getvalue()  # type: ignore

    if document.file_name.endswith(".xlsx"):  # type: ignore
        result = await actions.add_quiz.from_excel(content, user_id)
    elif document.file_name.endswith(".csv"):  # type: ignore
        result = await actions.add_quiz.from_csv(content, user_id)
    else:
        await mess.edit_text("Пожалуйста, отправьте файл формата .xlsx или .csv")
        return

    if isinstance(result, list):
        error_text = "Ошибки при импорте:\n" + "\n".join(result)
        await mess.edit_text(error_text)
        await state.clear()
        return

    quiz = result  # type: ignore
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="ОК", callback_data="close")]]
    )

    text = (
        f"Тест успешно импортирован!\n\n"
        f"id: {quiz.id}\n"
        f"Название теста: {quiz.title}"
    )
    await mess.edit_text(text, reply_markup=keyboard)
    await state.set_state()

# ==================== Кнопки шаблонов ====================
@admin_router.callback_query(F.data == "template_excel")
async def send_template_excel(callback: types.CallbackQuery, actions: AppActions):
    await callback.answer()
    file_bytes = await actions.get_quiz_template.from_excel()
    await callback.message.answer_document( #type: ignore
        types.BufferedInputFile(file_bytes, filename="quiz_template.xlsx")
    )

@admin_router.callback_query(F.data == "template_csv")
async def send_template_csv(callback: types.CallbackQuery, actions: AppActions):
    await callback.answer()
    file_bytes = await actions.get_quiz_template.from_csv()
    await callback.message.answer_document( #type: ignore
        types.BufferedInputFile(file_bytes, filename="quiz_template.csv")
    )

# ============================ Заглушка колбэка =================================

@admin_router.callback_query(F.data == "close")
async def close_callback(callback: types.CallbackQuery):
    await callback.message.delete()

