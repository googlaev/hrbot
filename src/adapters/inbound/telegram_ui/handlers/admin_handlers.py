from aiogram import Bot, types, F
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram import Router
from app.app_actions import AppActions

admin_router = Router()

# ============================ Хендлеры команд ============================

@admin_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Привет, администратор! /list_quiz для меню тестов.")

@admin_router.message(Command("list_quiz"))
async def list_quizzes(message: types.Message, state: FSMContext, actions: AppActions):
    quizzes = await actions.quiz_list.execute()

    if not quizzes:
        await message.answer("Тестов пока нет.")
        await message.delete()
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"id: {q.id} - {q.title}", callback_data=f"quiz|{q.id}")] for q in quizzes
        ]
    )
    await state.clear()
    await state.update_data(menu_stack=["list_quiz"])
    await message.answer("Список тестов:", reply_markup=keyboard)
    await message.delete()

@admin_router.callback_query(F.data.startswith("quiz|"))
async def quiz_menu(callback: types.CallbackQuery, state: FSMContext):
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

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Просмотр всех попыток", callback_data="view_attempts")],
            [InlineKeyboardButton(text="Удалить тест", callback_data="delete_quiz")],
            [InlineKeyboardButton(text="Назад", callback_data="back")],
        ]
    )
    await callback.message.edit_text(
        text=f"Меню теста id={quiz_id}", 
        reply_markup=keyboard
    )

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
        return

    for q in quizzes:
        percent = q.percent
        start_str = q.started_at.strftime("%d %b %Y %H:%M")
        finish_str = q.finished_at.strftime("%d %b %Y %H:%M")
        text += (f"👤 Айди юзера: {q.user_id}\n"
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
async def delete_confirm(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quiz_id = data["selected_quiz_id"]

    await delete_quiz_by_id(quiz_id)
    await callback.message.edit_text(f"Тест {quiz_id} удален.")

@admin_router.callback_query(F.data.startswith("export_attempts"))
async def export_attempts(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    quiz_id = data["selected_quiz_id"]

    sessions = await get_completed_sessions(quiz_id)
    if not sessions:
        await callback.message.answer("Нет завершенных попыток для этого теста.")
        return

    output = io.BytesIO()
    workbook = xlsxwriter.Workbook(output, {'in_memory': True})
    worksheet = workbook.add_worksheet("Quiz Results")
    worksheet.write_row(0, 0, ["User ID", "Session ID", "Correct", "Total", "Percent", "Started at", "Finished at"])

    row_num = 1
    for s in sessions:
        score = await get_score(s.id)
        percent = (score[0] / score[1] * 100) if score[1] > 0 else 0
        worksheet.write_row(row_num, 0, [s.user_id, s.id, score[0], score[1], f"{percent:.1f}%", str(s.started_at), str(s.finished_at)])
        row_num += 1

    workbook.close()
    output.seek(0)

    await callback.message.answer_document(InputFile(output, filename=f"quiz_{quiz_id}_results.xlsx"))

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
        await list_quizzes(callback.message, state, actions)
    elif previous_menu == "quiz_menu":
        await quiz_menu(callback, state)

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
    
    quiz = await actions.add_quiz_from_excel.execute(file_data.getvalue(), user_id)

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="ОК", callback_data="close")]]
    )

    message = f"Тест успешно импортирован!\n\nid: {quiz.id}\nНазвание теста: {quiz.title}"

    await mess.edit_text(message, reply_markup=keyboard)

# ============================ Заглушка колбэка =================================

@admin_router.callback_query(F.data == "close")
async def close_callback(callback: types.CallbackQuery):
    await callback.message.delete()

@admin_router.callback_query(F.data == "ignore")
async def ignore_callback(callback: types.CallbackQuery):
    """Игнорирует callback'и для неактивных кнопок"""
    await callback.answer()
