import os
import asyncio
import logging
from typing import Dict, Tuple, List

from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("call-center-bot")

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    logger.critical("BOT_TOKEN не найден в .env")
    raise RuntimeError("BOT_TOKEN не найден")

dp = Dispatcher()

AGENTS: Dict[str, Tuple[str, str]] = {
    "ШЫҒАРМ": ("ОРАЛБАЕВА АРУЖАН", "oralbayeva140"),
    "ФИЗМАТ": ("ФЕРУЗА ДИХАНБАЙ", "ms_feeee"),
    "ФИЗХИМ": ("АСҚАРБЕК АСАНБАЙ", "asanbay_juz40"),
    "ДЖТАНГЛ": ("МАЙРА АҒАБЕКОВА", "dzhteng1"),
    "БИОХИМ": ("ТӘНЕН ЕРДӘУЛЕТ", "Erda_05"),
    "ГЕОДЖТ": ("ҚАЛДЫБАЙ ӘМІРХАН", "geomathdzhtsuper"),
    "ГЕОМАТ": ("ИЗБАСАР АЙГЕРІМ", "izbasaraigerim"),
    "ДЖТҚҰҚЫҚ": ("ДЮСЕГАЛИЕВА ДАЯНА", "dayanka04"),
    "ӘДЕБТІЛ": ("ЖАҚСЫБЕК АЯУЛЫМ", "ayaulym140"),
    "ГЕОБИО": ("МУХАМЕДАЛИ МЕРЕЙ", "mkhmdlm"),
    "ГЕОАНГЛ": ("РАХАТОВ МӘУЛЕН", "maulen_juz40eng"),
    "РУСЛИТ": ("БЕРЕКЕЕВА МАРИЯМ", "berekeevaa"),
    "ИНФОМАТ": ("МҰСАҒАЛИ АМИНА", "aminainfomath"),
}

MENU_ORDER: List[str] = list(AGENTS.keys())

def chunk(lst: List[str], n: int):
    return [lst[i:i + n] for i in range(0, len(lst), n)]

def main_menu() -> InlineKeyboardMarkup:
    rows = []
    for pair in chunk(MENU_ORDER, 2):
        rows.append([
            InlineKeyboardButton(text=combo, callback_data=f"agent:{combo}")
            for combo in pair
        ])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def contact_kb(username: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=f"@{username}", url=f"https://t.me/{username}")]
        ]
    )

MAIN_MENU = main_menu()

def agent_text(name: str, combo: str) -> str:
    return (
        f"{name} – {combo} комбинациясына жауапты маман.\n"
        f"Байланысу үшін мында басыңыз 👉"
    )

@dp.message(Command("start"))
async def start(message: Message):
    logger.info(
        "START | user_id=%s username=%s",
        message.from_user.id,
        message.from_user.username,
    )
    await message.answer(
        "Call Centre-ге қош келдіңіз 👋\n\nКомбинацияны таңдаңыз ⬇️",
        reply_markup=MAIN_MENU,
    )

@dp.callback_query(F.data.startswith("agent:"))
async def send_agent(callback: CallbackQuery):
    combo = callback.data.split(":", 1)[1]
    user = callback.from_user

    logger.info(
        "CLICK | user_id=%s username=%s combo=%s",
        user.id,
        user.username,
        combo,
    )

    if combo not in AGENTS:
        logger.error(
            "NOT_FOUND | user_id=%s combo=%s",
            user.id,
            combo,
        )
        await callback.answer("Комбинация табылмады", show_alert=True)
        return

    name, username = AGENTS[combo]

    await callback.message.answer(
        agent_text(name, combo),
        reply_markup=contact_kb(username),
    )
    await callback.answer()

@dp.message()
async def fallback(message: Message):
    logger.warning(
        "UNKNOWN_MESSAGE | user_id=%s text=%s",
        message.from_user.id,
        message.text,
    )
    await message.answer("Мәзірден таңдаңыз ⬇️", reply_markup=MAIN_MENU)

async def main():
    logger.info("🚀 Bot starting...")
    bot = Bot(BOT_TOKEN)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
