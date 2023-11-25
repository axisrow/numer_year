import os
import telebot
from telebot import types
from datetime import date
from calculate import *
from user_stat import UserStat, db
# from logger import setup_logger

# logger = setup_logger()

from dotenv import load_dotenv
load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = 169675602
bot = telebot.TeleBot(BOT_TOKEN)

# Функция для создания кнопок
def generate_markup_years(year=None):
    markup = types.InlineKeyboardMarkup()
    if year is None:
        # Кнопки по умолчанию
        years = [2022, 2023, 2024]
    else:
        # Генерация кнопок на основе выбранного года
        year = int(year)
        years = [year - 1, year + 1]
    
    for y in years:
        markup.add(types.InlineKeyboardButton(text=str(y), callback_data=str(y)))

    return markup

def register_user(user_id, username, first_name, last_name, language_code, birth_date):
    user, created = UserStat.get_or_create(
        user_id=user_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'language_code': language_code,
            'date_of_birth': birth_date,
            'message_count': 1  # устанавливаем счетчик сообщений на 1 при регистрации нового пользователя
        })

    if not created:
        user.date_of_birth = birth_date
        user.message_count += 1  # увеличиваем счетчик сообщений на 1 при каждом новом сообщении
        user.save()

def get_user(user_id):
    try:
        user = UserStat.get(UserStat.user_id == user_id)
        return user
    except UserStat.DoesNotExist:
        return None

def get_total_users():
    return UserStat.select().count()

@bot.callback_query_handler(func=lambda call: True)
def button_click(call):
    # Получаем текст кнопки
    button_text = call.data
    # Получаем ID пользователя, который нажал на кнопку
    user_id = call.from_user.id
    # Изменяем текст в существующем сообщении
    call.message.text = button_text
    # Вызываем обработчик года с модифицированным сообщением
    year_handler(call.message)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = get_user(message.chat.id)
    if user:
        try:
            year = int(message.text)  # Пытаемся интерпретировать текст сообщения как год
        except ValueError:
            year = None  # Если текст не является числом, используем значения по умолчанию
            markup_years = generate_markup_years(year)
            bot.send_message(message.chat.id, f"Здравствуйте, {user.first_name} {user.last_name}, Вы родились: {user.date_of_birth}\nВыберите год, который Вас интересует:", reply_markup=markup_years)
            bot.send_message(message.chat.id, "Или введите любой год:")
    else:
        bot.send_message(message.chat.id, "Введите вашу дату рождения в формате ДД.ММ.ГГГГ:")

@bot.message_handler(func=lambda message: not message.text.isdigit())
def birth_date_handler(message):
    chat_id = message.chat.id
    text = message.text
    
    # Теперь этот обработчик сфокусирован только на обработке даты рождения
    # Проверяем, является ли текст датой
    date_parts = text.split('.')
    if len(date_parts) != 3 or not all(part.isdigit() for part in date_parts):
        bot.send_message(chat_id, "Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.")
        return
    
    try:
        birth_date = date(int(date_parts[2]), int(date_parts[1]), int(date_parts[0]))
        register_user(
            user_id=chat_id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language_code=message.from_user.language_code,
            birth_date=birth_date
        )
        bot.send_message(chat_id, "Дата рождения успешно сохранена. Введите интересующий Вас год.")
    except ValueError:
        bot.send_message(chat_id, "Некорректный формат даты. Пожалуйста, введите дату в формате ДД.ММ.ГГГГ.")

@bot.message_handler(func=lambda message: message.text.isdigit())
def year_handler(message):
    chat_id = message.chat.id
    text = message.text

    # Обработка интересующего года
    if 1900 <= int(text) <= 2100:
        user = get_user(chat_id)
        user.message_count += 1  # увеличиваем счетчик сообщений на 1 при каждом новом сообщении
        user.save()
        if not user:
            bot.send_message(chat_id, "Сначала введите вашу дату рождения.")
            return

        year_of_interest = int(text)
        birth_date_str = user.date_of_birth.strftime('%d.%m.%Y')
        text_for_A, date_range = calculate_from_date(f"{birth_date_str.split('.')[0]}.{birth_date_str.split('.')[1]}.{year_of_interest}")
        # Генерация клавиатуры с кнопками для годов
        markup_years = generate_markup_years(year_of_interest)
        bot.send_message(chat_id, f"{text_for_A}\nДиапазон дат: {date_range}", reply_markup=markup_years)
        bot.send_message(message.chat.id, "Или введите любой год:")
    else:
        bot.send_message(chat_id, "Некорректный ввод. Введите интересующий Вас год (от 1900 до 2100).")

@bot.message_handler(commands=['stat'])
def send_stats(message):
    if message.chat.id == ADMIN_CHAT_ID:
        total_users = get_total_users()
        users = UserStat.select()

        user_info = ["Уникальных пользователей:"]
        for user in users:
            user_info.append(f"{user.user_id}, @{user.username}")

        user_info.append(f"Всего: {total_users}")
        bot.send_message(message.chat.id, '\n'.join(user_info))

print("Бот запущен")
bot.polling(non_stop=True, interval=0)