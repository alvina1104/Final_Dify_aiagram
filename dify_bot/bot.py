from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message,InlineKeyboardMarkup,InlineKeyboardButton
from aiogram.enums import ChatAction
from dotenv import load_dotenv
from dify import ask_dify
from storage import load_data, save_data
from aiogram.types import CallbackQuery
import asyncio
import logging
import os

load_dotenv()

TOKEN = os.getenv("TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=TOKEN)
dp = Dispatcher()
router = Router()


data = load_data()


def get_user(user_id):
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "conversation_id": None,
            "history": [],
            "messages_count": 0
        }

    return data[user_id]


keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Жардам",callback_data="help"),InlineKeyboardButton(text="Жаңы диалог",callback_data="new")
        ]
    ]
)



@router.message(Command("start"))
async def start(message: Message):

    user = get_user(message.from_user.id)

    user["conversation_id"] = None
    user["history"] = []

    save_data(data)

    await message.answer(
        f"Салам, {message.from_user.first_name}! 👋\n\n"
        "Мен DreamHome AI жардамчымын.\n\n"
        "Мага сурооңузду жазыңыз.",
        reply_markup=keyboard
    )



@router.message(Command("help"))
async def help_command(message: Message):

    text = ("📚 Командалар:\n\n"
        "/start - Ботту баштоо\n"
        "/help - Командалар\n"
        "/new - Жаңы диалог\n"
        "/history - Акыркы билдирүүлөр\n"
        "/stats - Статистика\n\n"
        "Каалаган сурооңузду жазыңыз.")

    await message.answer(text)


@router.message(Command("new"))
async def new_chat(message: Message):

    user = get_user(message.from_user.id)

    user["conversation_id"] = None
    user["history"] = []

    save_data(data)

    await message.answer("Жаңы диалог башталды.")


@router.message(Command("history"))
async def history(message: Message):

    user = get_user(message.from_user.id)
    history = user["history"]

    if not history:
        await message.answer("История бош.")
        return

    last_history = history[-6:]

    text = "📜 Акыркы билдирүүлөр:\n\n"

    for item in last_history:
        if item["role"] == "user":
            text += f"Сиз: {item['text']}\n\n"
        else:
            text += f"AI: {item['text']}\n\n"

    await message.answer(text)



@router.message(Command("stats"))
async def stats(message: Message):

    user = get_user(message.from_user.id)

    await message.answer(f"📊 Статистика\n\n"
        f"Жөнөтүлгөн билдирүүлөр: {user['messages_count']}")



@router.message(F.photo)
async def photo(message: Message):

    await message.answer(
        "Кечиресиз, азырынча сүрөттөрдү окуй албайм.\n"
        "Сураныч, сурооңузду текст түрүндө жазыңыз."
    )



@router.message(F.text)
async def get_question(message: Message):

    user = get_user(message.from_user.id)

    question = message.text
    conversation_id = user["conversation_id"]

    await bot.send_chat_action(chat_id=message.chat.id, action=ChatAction.TYPING)

    result = ask_dify(question=question,user_id=message.from_user.id,conversation_id=conversation_id)

    if result.get("conversation_id"):
        user["conversation_id"] = result["conversation_id"]

    user["messages_count"] += 1

    user["history"].append({"role": "user","text": question})

    user["history"].append({"role": "assistant","text": result["answer"]})

    if len(user["history"]) > 50:
        user["history"] = user["history"][-50:]

    save_data(data)

    await message.answer(result["answer"])


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):

    await callback.message.answer(
        "📚 Командалар:\n\n"
        "/start - Ботту баштоо\n"
        "/help - Жардам\n"
        "/new - Жаңы диалог\n"
        "/history - Акыркы 6 билдирүү\n"
        "/stats - Статистика"
    )

    await callback.answer()


@router.callback_query(F.data == "new")
async def new_callback(callback: CallbackQuery):

    user = get_user(callback.from_user.id)

    user["conversation_id"] = None
    user["history"] = []

    save_data(data)

    await callback.message.answer("Жаңы диалог башталды.")

    await callback.answer()



@router.message()
async def unknown(message: Message):

    await message.answer("Мен бул билдирүүнү түшүнө алган жокмун.")


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())