from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command, Text
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.enums import ParseMode
import asyncio

# Настройки
BOT_TOKEN = "**********************************************"
ADMIN_USERNAME = "78689787876"  # Ваш аккаунт для уведомлений

bot = Bot(token=BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# База данных меню
menu_db = {
    "first_courses": ["Борщ", "Солянка", "Гороховый суп"],
    "main_courses": [
        "Котлета куриная",
        "Котлета свиная", 
        "Бифштекс классический",
        "Биток куриный",
        "Голубчики",
        "Тефтели из говядины",
        "Оладьи из печени"
    ],
    "sides": ["Пюре", "Гречка", "Макароны", "Рис"],
    "salads": ["Винегрет", "Оливье"],
    "specials": ["Курица гриль 🍗🔥"]
}

# Корзины пользователей
user_carts = {}

# ===== КЛАВИАТУРЫ =====
def main_menu_kb():
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="🍜 Первые блюда"),
        KeyboardButton(text="🍖 Вторые блюда")
    )
    builder.row(
        KeyboardButton(text="🍚 Гарниры"),
        KeyboardButton(text="🥗 Салаты")
    )
    builder.row(KeyboardButton(text="🔥 Хиты дня"))
    builder.row(KeyboardButton(text="🛒 Корзина"))
    return builder.as_markup(resize_keyboard=True)

def back_to_menu_kb():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🔙 Назад")]],
        resize_keyboard=True
    )

# ===== КОМАНДЫ =====
@dp.message(Command("start"))
async def start(message: types.Message):
    user_id = message.from_user.id
    user_carts[user_id] = []
    await message.answer(
        "🍽 <b>Добро пожаловать в FermaDv!</b>\n"
        "Выберите категорию:",
        reply_markup=main_menu_kb()
    )

# ===== ОБРАБОТКА МЕНЮ =====
@dp.message(Text(text=["🍜 Первые блюда", "🍖 Вторые блюда", "🍚 Гарниры", "🥗 Салаты"]))
async def show_menu(message: types.Message):
    category_map = {
        "🍜 Первые блюда": "first_courses",
        "🍖 Вторые блюда": "main_courses", 
        "🍚 Гарниры": "sides",
        "🥗 Салаты": "salads"
    }
    
    category = category_map[message.text]
    builder = ReplyKeyboardBuilder()
    
    for item in menu_db[category]:
        builder.add(KeyboardButton(text=f"➕ {item}"))
    builder.adjust(2)
    builder.row(KeyboardButton(text="🔙 Назад"))
    
    await message.answer(
        f"Меню {message.text}:",
        reply_markup=builder.as_markup()
    )

@dp.message(Text(text="🔥 Хиты дня"))
async def show_specials(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=f"➕ {menu_db['specials'][0]}"))
    builder.row(KeyboardButton(text="🔙 Назад"))
    
    await message.answer(
        "🔥 <b>Хит дня!</b>",
        reply_markup=builder.as_markup()
    )

# ===== ОБРАБОТКА КОРЗИНЫ =====
@dp.message(Text(startswith="➕ "))
async def add_to_cart(message: types.Message):
    item = message.text[2:]
    user_id = message.from_user.id
    
    if user_id not in user_carts:
        user_carts[user_id] = []
    
    user_carts[user_id].append(item)
    await message.answer(
        f"✅ {item} добавлен в корзину!",
        reply_markup=back_to_menu_kb()
    )

@dp.message(Text(text="🛒 Корзина"))
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    
    if not cart:
        await message.answer(
            "🛒 Ваша корзина пуста",
            reply_markup=main_menu_kb()
        )
        return
    
    cart_text = "\n".join(f"• {item}" for item in cart)
    await message.answer(
        f"🛒 <b>Ваша корзина:</b>\n{cart_text}\n\n"
        "Выберите действие:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Оформить заказ")],
                [KeyboardButton(text="❌ Очистить корзину")],
                [KeyboardButton(text="🔙 Назад")]
            ],
            resize_keyboard=True
        )
    )

@dp.message(Text(text="❌ Очистить корзина"))
async def clear_cart(message: types.Message):
    user_id = message.from_user.id
    user_carts[user_id] = []
    await message.answer(
        "🗑 Корзина очищена!",
        reply_markup=main_menu_kb()
    )

# ===== ОФОРМЛЕНИЕ ЗАКАЗА =====
@dp.message(Text(text="✅ Оформить заказ"))
async def process_order(message: types.Message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    
    if not cart:
        await message.answer("❌ Корзина пуста!")
        return
    
    # Формируем текст заказа
    order_text = (
        f"📦 <b>Новый заказ!</b>\n\n"
        f"👤 Клиент: @{message.from_user.username}\n"
        f"🆔 ID: {user_id}\n"
        f"📞 Имя: {message.from_user.full_name}\n\n"
        "🍽 <b>Заказ:</b>\n" + 
        "\n".join(f"- {item}" for item in cart)
    )
    
    # Кнопка для связи с клиентом
    contact_btn = InlineKeyboardButton(
        text="Написать клиенту",
        url=f"tg://user?id={user_id}"
    )
    
    try:
        # Отправляем админу
        await bot.send_message(
            chat_id=ADMIN_USERNAME,
            text=order_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[contact_btn]])
        )
        # Подтверждение пользователю
        await message.answer(
            "✅ <b>Заказ оформлен!</b>\n\n"
            "Скоро с вами свяжутся для подтверждения.\n"
            "Приятного аппетита! 🍴",
            reply_markup=main_menu_kb()
        )
        
        # Очищаем корзину
        user_carts[user_id] = []
        
    except Exception as e:
        await message.answer(
            "⚠️ Произошла ошибка при отправке заказа. Пожалуйста, попробуйте позже.",
            reply_markup=main_menu_kb()
        )
        print(f"Ошибка отправки заказа: {e}")

# ===== ОБРАБОТКА КНОПКИ "НАЗАД" =====
@dp.message(Text(text="🔙 Назад"))
async def back_handler(message: types.Message):
    await message.answer(
        "Главное меню:",
        reply_markup=main_menu_kb()
    )

# ===== ЗАПУСК БОТА =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

if __name__ == "__main__":
    asyncio.run(main())
