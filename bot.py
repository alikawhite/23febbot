import os
import asyncio
import random
from pathlib import Path
from aiogram import Bot, Dispatcher, Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.types import FSInputFile
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

TOKEN = os.getenv("BOT_TOKEN")

router = Router()


class Quiz(StatesGroup):
    in_progress = State()


QUESTIONS = [
    {
        "image": "images/q1.png",
        "text": "Кто это?",
        "options": ["Аня", "Ваня", "Саша", "Олег"],
        "correct": 0,
        "hint": "Это женское имя на букву «А».",
    },
        {
        "image": "images/q2.png",
        "text": "Кто это?",
        "options": ["Аня", "Ваня", "Саша", "Олег"],
        "correct": 0,
        "hint": "Это женское имя на букву «А».",
    },
        {
        "image": "images/q3.png",
        "text": "Кто это?",
        "options": ["Аня", "Ваня", "Саша", "Олег"],
        "correct": 0,
        "hint": "Это женское имя на букву «А».",
    },
        {
        "image": "images/q4.png",
        "text": "Кто это?",
        "options": ["Аня", "Ваня", "Саша", "Олег"],
        "correct": 0,
        "hint": "Это женское имя на букву «А».",
    },
        {
        "image": "images/q5.png",
        "text": "Кто это?",
        "options": ["Аня", "Ваня", "Саша", "Олег"],
        "correct": 0,
        "hint": "Это женское имя на букву «А».",
    },
        {
        "image": "images/q6.png",
        "text": "Кто это?",
        "options": ["Аня", "Ваня", "Саша", "Олег"],
        "correct": 0,
        "hint": "Это женское имя на букву «А».",
    },
        {
        "image": "images/q7.png",
        "text": "Кто это?",
        "options": ["Аня", "Ваня", "Саша", "Олег"],
        "correct": 0,
        "hint": "Это женское имя на букву «А».",
    },
        {
        "image": "images/q1.png",
        "text": "Кто это?",
        "options": ["Аня", "Ваня", "Саша", "Олег"],
        "correct": 0,
        "hint": "Это женское имя на букву «А».",
    },
]

CERTIFICATES = {
    "1646691629": "certs/alex.png",
    "136735168": "certs/kirill.png",
    "VG_Vladimir": "certs/vova.png",
    "191124817": "certs/andrey.png",
    "233457787": "certs/artem.png",
    "huhguz": "certs/ilya.png",
    "rgolub": "certs/rostik.png",
    "997244612": "certs/sasha.png",
}

DEFAULT_CERT = "certs/vova.png"


async def send_question(bot: Bot, chat_id: int, state: FSMContext):
    data = await state.get_data()
    q_index = data.get("question_index", 0)

    question = QUESTIONS[q_index]

    image_path = BASE_DIR / question["image"]
    if not image_path.exists():
        await bot.send_message(chat_id, f"Ошибка: не найдена картинка {question['image']}")
        return
    photo = FSInputFile(image_path)

    progress = f"Вопрос {q_index + 1}/{len(QUESTIONS)}"
    await bot.send_photo(
        chat_id=chat_id,
        photo=photo,
        caption=f"{question['text']}\n\n{progress}",
    )



# Новый обработчик для /start с одной кнопкой "Начать викторину"
@router.message(F.text == "/start")
async def start(message: Message, state: FSMContext):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Начать викторину", callback_data="start_quiz")]
    ])
    await message.answer("Готова проверить себя? Нажми кнопку, чтобы начать викторину.", reply_markup=kb)


# Callback handler для старта викторины
@router.callback_query(F.data == "start_quiz")
async def start_quiz(callback: CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(Quiz.in_progress)
    await state.update_data(question_index=0, attempts=0, attempts_in_question=0)
    await callback.message.answer("Напиши свой ответ текстом для первого вопроса.")
    await send_question(bot, callback.message.chat.id, state)
    await callback.answer()


@router.message(Quiz.in_progress)
async def handle_answer(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    current_q = data.get("question_index", 0)
    attempts = data.get("attempts", 0)
    attempts_in_question = data.get("attempts_in_question", 0)

    user_answer = message.text.strip().lower()
    correct_answer = QUESTIONS[current_q]["options"][QUESTIONS[current_q]["correct"]].lower()

    attempts_in_question += 1
    attempts += 1
    await state.update_data(attempts=attempts, attempts_in_question=attempts_in_question)

    if user_answer != correct_answer:
        if attempts_in_question < 3:
            await bot.send_message(message.chat.id, "❌ Неверно. Попробуй ещё раз.")
        elif attempts_in_question == 3:
            hint_text = QUESTIONS[current_q].get("hint", "Подсказка пока не задана для этого вопроса.")
            await bot.send_message(message.chat.id, f"💡 Подсказка: {hint_text}")
        elif attempts_in_question == 5:
            correct_option = QUESTIONS[current_q]["options"][QUESTIONS[current_q]["correct"]]
            await bot.send_message(message.chat.id, f"🧠 Ответ: {correct_option}")
        else:
            await bot.send_message(message.chat.id, "❌ Неверно. Попробуй ещё раз.")
        return

    await state.update_data(attempts_in_question=0)
    next_q = current_q + 1
    if next_q >= len(QUESTIONS):
        await state.clear()

        user_id_str = str(message.from_user.id)
        username = message.from_user.username

        # Сначала проверяем id, потом username, потом DEFAULT_CERT
        cert_rel_path = CERTIFICATES.get(user_id_str) or CERTIFICATES.get(username) or DEFAULT_CERT
        cert_path = BASE_DIR / cert_rel_path

        if not cert_path.exists():
            await bot.send_message(message.chat.id, f"Ошибка: не найден сертификат {cert_rel_path}")
            return

        cert = FSInputFile(cert_path)
        caption = f"Поздравляем! Ты прошел викторину.\nПопыток: {attempts}"
        await bot.send_photo(message.chat.id, cert, caption=caption)
        return

    await state.update_data(question_index=next_q)
    await send_question(bot, message.chat.id, state)


async def main():
    bot = Bot(TOKEN)
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
