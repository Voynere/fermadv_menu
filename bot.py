from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "ТВОЙ_ТОКЕН"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# Клавиатура с категориями
menu_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
menu_keyboard.add(KeyboardButton("Первые блюда"))
menu_keyboard.add(KeyboardButton("Вторые блюда"))
menu_keyboard.add(KeyboardButton("Гарниры"))
menu_keyboard.add(KeyboardButton("Салаты"))
menu_keyboard.add(KeyboardButton("Хиты"))

# Данные меню
menu = {
    "Первые блюда": ["борщ", "солянка", "гороховый суп"],
    "Вторые блюда": [
        "котлета говяжья", "котлета куриная", "котлета свиная",
        "бифштекс классический", "биток куриный", "голубчики",
        "перец фаршированный", "тефтели", "тефтели из говядины",
        "оладьи из печени"
    ],
    "Гарниры": ["рис", "пюре", "гречка", "макароны"],
    "Салаты": ["винегрет", "оливье"],
    "Хиты": ["Курица гриль 🍗🔥"]
}

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("🍽 Добро пожаловать в меню! Выбери категорию:", reply_markup=menu_keyboard)

@dp.message_handler(lambda message: message.text in menu.keys())
async def show_category(message: types.Message):
    category = message.text
    dishes = "\n".join(f"🍴 {dish}" for dish in menu[category])
    await message.answer(f"<b>{category}:</b>\n{dishes}", parse_mode="HTML")

@dp.message_handler(lambda message: message.text == "Хиты")
async def show_hit(message: types.Message):
    await message.answer("🔥 <b>Хит меню:</b> 🔥\n" + menu["Хиты"][0], parse_mode="HTML")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
