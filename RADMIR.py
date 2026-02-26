import asyncio
import logging
import random
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage

# Токен бота
BOT_TOKEN = "8220649520:AAG4A43kiZ4oAJn26Ag3HhmfE9LLpqIqNB4"

# Логирование
logging.basicConfig(level=logging.INFO)

# Инициализация
bot = Bot(token=BOT_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# ---------- Состояния для FSM ----------
class UtilStates(StatesGroup):
    waiting_for_price = State()
    waiting_for_wear = State()

# ---------- Клавиатуры ----------
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="🚗 Рассчитать утилизацию")],
        [KeyboardButton(text="🎲 Бросить кубик")],
        [KeyboardButton(text="ℹ️ Информация")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_cancel_keyboard():
    buttons = [[KeyboardButton(text="❌ Отмена")]]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

# ---------- Функция для удаления сообщения через 60 секунд ----------
async def delete_message_after_delay(chat_id: int, message_id: int, delay: int = 60):
    """Удаляет сообщение через указанное количество секунд"""
    await asyncio.sleep(delay)
    try:
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception as e:
        # Сообщение могло уже удалиться или не иметь прав на удаление
        pass

# ---------- Функция расчёта процента по износу ----------
def get_percent_from_wear(wear: int) -> int | None:
    if wear == 100:
        return 10
    elif 95 <= wear <= 99:
        return 11
    elif 90 <= wear <= 94:
        return 12
    elif 85 <= wear <= 89:
        return 13
    elif 80 <= wear <= 84:
        return 14
    elif 75 <= wear <= 79:
        return 15
    elif 70 <= wear <= 74:
        return 16
    elif 65 <= wear <= 69:
        return 17
    elif 60 <= wear <= 64:
        return 18
    elif 55 <= wear <= 59:
        return 19
    elif 50 <= wear <= 54:
        return 20
    elif 45 <= wear <= 49:
        return 21
    elif 40 <= wear <= 44:
        return 22
    elif 35 <= wear <= 39:
        return 23
    elif 30 <= wear <= 34:
        return 24
    elif 25 <= wear <= 29:
        return 25
    elif 20 <= wear <= 24:
        return 26
    elif 15 <= wear <= 19:
        return 27
    elif 10 <= wear <= 14:
        return 28
    elif 5 <= wear <= 9:
        return 29
    elif 0 <= wear <= 4:
        return 30
    else:
        return None

# ---------- Middleware для удаления сообщений пользователя ----------
@dp.message.outer_middleware()
async def delete_user_messages(handler, event: Message, data: dict):
    """Удаляет сообщение пользователя через 60 секунд (кроме команд)"""
    result = await handler(event, data)
    
    # Не удаляем команды /start и /cancel
    if event.text and event.text.startswith('/'):
        return result
    
    # Удаляем сообщение пользователя через 60 секунд
    asyncio.create_task(delete_message_after_delay(event.chat.id, event.message_id))
    return result

# ---------- Команда /start ----------
@dp.message(Command("start"))
async def cmd_start(message: Message):
    sent_msg = await message.answer(
        "👋 Привет! Я бот-помощник для игры.\n"
        "Нажимай кнопки внизу 👇",
        reply_markup=get_main_keyboard()
    )
    # Удаляем это сообщение через 60 секунд
    asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))

# ---------- Команда /cancel и кнопка отмены ----------
@dp.message(Command("cancel"))
@dp.message(lambda message: message.text == "❌ Отмена")
async def cancel_action(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    sent_msg = await message.answer(
        "❌ Действие отменено. Возвращаю в главное меню.",
        reply_markup=get_main_keyboard()
    )
    # Удаляем сообщение об отмене через 60 секунд
    asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))

# ---------- Обработка кнопки "Рассчитать утилизацию" ----------
@dp.message(lambda message: message.text == "🚗 Рассчитать утилизацию")
async def start_util(message: Message, state: FSMContext):
    await state.set_state(UtilStates.waiting_for_price)
    sent_msg = await message.answer(
        "Введите стоимость авто (только число, например: 1500000):",
        reply_markup=get_cancel_keyboard()
    )
    # Удаляем это сообщение через 60 секунд
    asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))

# ---------- Обработка кнопки "Бросить кубик" ----------
@dp.message(lambda message: message.text == "🎲 Бросить кубик")
async def roll_dice(message: Message):
    result = random.randint(1, 6)
    sent_msg = await message.answer(
        f"🎲 Тебе выпало: {result}", 
        reply_markup=get_main_keyboard()
    )
    # Удаляем результат кубика через 60 секунд
    asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))

# ---------- Обработка кнопки "Информация" ----------
@dp.message(lambda message: message.text == "ℹ️ Информация")
async def show_info(message: Message):
    sent_msg = await message.answer(
        "ℹ️ Информация об игре\n\n"
        "Здесь будут правила, ссылки или подсказки.",
        reply_markup=get_main_keyboard()
    )
    # Удаляем информационное сообщение через 60 секунд
    asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))

# ---------- Ввод цены ----------
@dp.message(UtilStates.waiting_for_price)
async def process_price(message: Message, state: FSMContext):
    try:
        price_str = message.text.replace(" ", "").replace(",", ".")
        price = float(price_str)
        if price <= 0:
            raise ValueError("Цена должна быть положительной")
        
        await state.update_data(price=price)
        await state.set_state(UtilStates.waiting_for_wear)
        sent_msg = await message.answer(
            "Теперь введите износ (число от 0 до 100):",
            reply_markup=get_cancel_keyboard()
        )
        # Удаляем это сообщение через 60 секунд
        asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))
        
    except ValueError:
        sent_msg = await message.answer(
            "❌ Некорректная цена. Введите число (например: 1500000):",
            reply_markup=get_cancel_keyboard()
        )
        # Удаляем сообщение об ошибке через 60 секунд
        asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))

# ---------- Ввод износа и расчёт ----------
@dp.message(UtilStates.waiting_for_wear)
async def process_wear(message: Message, state: FSMContext):
    try:
        wear = int(message.text)
        if wear < 0 or wear > 100:
            raise ValueError("Износ должен быть от 0 до 100")
        
        percent = get_percent_from_wear(wear)
        if percent is None:
            await message.answer("❌ Ошибка: не удалось определить процент")
            await state.clear()
            sent_menu = await message.answer("Главное меню:", reply_markup=get_main_keyboard())
            asyncio.create_task(delete_message_after_delay(message.chat.id, sent_menu.message_id))
            return
        
        data = await state.get_data()
        price = data['price']
        util_price = (price / 100) * percent
        
        # ЭТО СООБЩЕНИЕ НЕ УДАЛЯЕТСЯ - финальный результат
        await message.answer(
            f"🚗 **Результат расчёта утилизации**\n\n"
            f"💰 Стоимость авто: {price:,.0f}\n"
            f"🔧 Износ: {wear}%\n"
            f"📊 Процент: {percent}%\n"
            f"💵 **Цена утилизации: {util_price:,.0f}**",
            parse_mode="Markdown",
            reply_markup=get_main_keyboard()
        )
        
        await state.clear()
        
    except ValueError:
        sent_msg = await message.answer(
            "❌ Некорректный износ. Введите число от 0 до 100:",
            reply_markup=get_cancel_keyboard()
        )
        # Удаляем сообщение об ошибке через 60 секунд
        asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))

# ---------- Обработка всего остального ----------
@dp.message()
async def handle_unknown(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        sent_msg = await message.answer(
            "Сейчас идёт диалог. Используйте кнопку «❌ Отмена»",
            reply_markup=get_cancel_keyboard()
        )
        # Удаляем это сообщение через 60 секунд
        asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))
    else:
        sent_msg = await message.answer(
            "Используйте кнопки внизу 👇",
            reply_markup=get_main_keyboard()
        )
        # Удаляем это сообщение через 60 секунд
        asyncio.create_task(delete_message_after_delay(message.chat.id, sent_msg.message_id))

# ---------- Запуск ----------
async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())