from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder
import asyncio

# Конфигурация
BOT_TOKEN = "7850687351:AAFQB9Nb-08_8foLIJ6-rzDRAasWHEb0xjU"
ADMIN_USERNAME = "@ferma_dv25"  # Ваш аккаунт для уведомлений

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# База данных меню
menu_db = {
    "first_courses": ["Борщ", "Солянка", "Гороховый суп"],
    "main_courses": ["Котлета говяжья", "Курица гриль", "Тефтели"],
    "sides": ["Пюре", "Гречка", "Макароны"],
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
    user_carts[message.from_user.id] = []
    await message.answer(
        "🍽 <b>Добро пожаловать в FermaDv!</b>\n"
        "Выберите категорию:",
        reply_markup=main_menu_kb()
    )

# ===== ОБРАБОТКА МЕНЮ =====
@dp.message(lambda msg: msg.text in ["🍜 Первые блюда", "🍖 Вторые блюда", "🍚 Гарниры"])
async def show_menu(message: types.Message):
    category_map = {
        "🍜 Первые блюда": "first_courses",
        "🍖 Вторые блюда": "main_courses",
        "🍚 Гарниры": "sides"
    }
    
    category = category_map[message.text]
    builder = ReplyKeyboardBuilder()
    
    for item in menu_db[category]:
        builder.add(KeyboardButton(text=f"➕ {item}"))
    builder.adjust(2)
    builder.row(KeyboardButton(text="🔙 Назад"))
    
    await message.answer("Выберите блюдо:", reply_markup=builder.as_markup())

# ===== ОБРАБОТКА КОРЗИНЫ =====
@dp.message(lambda msg: msg.text.startswith("➕ "))
async def add_to_cart(message: types.Message):
    item = message.text[2:]
    user_id = message.from_user.id
    
    if user_id not in user_carts:
        user_carts[user_id] = []
    
    user_carts[user_id].append(item)
    await message.answer(f"✅ {item} добавлен в корзину!", reply_markup=back_to_menu_kb())

@dp.message(lambda msg: msg.text == "🛒 Корзина")
async def show_cart(message: types.Message):
    user_id = message.from_user.id
    cart = user_carts.get(user_id, [])
    
    if not cart:
        await message.answer("🛒 Корзина пуста", reply_markup=main_menu_kb())
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

# ===== ОФОРМЛЕНИЕ ЗАКАЗА =====
@dp.message(lambda msg: msg.text == "✅ Оформить заказ")
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
        f"📝 Заказ:\n" + 
        "\n".join(f"- {item}" for item in cart)
    )
    
    # Кнопка "Написать клиенту" для админа
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
            "✅ <b>Заказ оформлен!</b>\n"
            "Мы уже готовим ваш заказ. Скоро с вами свяжутся!",
            reply_markup=main_menu_kb()
        )
        
        user_carts[user_id] = []  # Очищаем корзину
        
    except Exception as e:
        await message.answer(
            "⚠️ Произошла ошибка при отправке заказа. Пожалуйста, попробуйте позже.",
            reply_markup=main_menu_kb()
        )
        print(f"Ошибка отправки заказа: {e}")

# ===== ЗАПУСК БОТА =====
async def main():
    print("Бот запущен!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
