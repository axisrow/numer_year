import os
import telebot
from telebot import types
from datetime import datetime
from calculate import *
from user_stat import UserStat
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

def register_user(user_id, username, first_name, last_name, language_code, date_of_birth):
    current_time_utc = datetime.utcnow()  # Получение текущего времени в формате UTC
    user, created = UserStat.get_or_create(
        user_id=user_id,
        defaults={
            'registration_time_utc': current_time_utc,
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'language_code': language_code,
            'date_of_birth': None,  # Дата рождения изначально неизвестна
            'message_count': 0
        })

def get_user(user_id): #ищет польователя в базе данных
    try:
        user = UserStat.get(UserStat.user_id == user_id)
        return user
    except UserStat.DoesNotExist:
        return None # если не находит, возвращает None

def get_total_users():
    return UserStat.select().count()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    current_time_utc = datetime.utcnow()
    utm_source = None
    command_text = message.text.split()

    # Проверяем, есть ли параметры после команды /start
    if len(command_text) > 1:
        utm_source = command_text[1]  # Второй элемент команды считается UTM-меткой

    user, created = UserStat.get_or_create(
        user_id=message.chat.id,
        defaults={
            'registration_time_utc': current_time_utc,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
            'language_code': message.from_user.language_code,
            'date_of_birth': None,  # Дата рождения изначально неизвестна
            'utm_source': utm_source,
            'message_count': 0
        })

    if created:
        bot.send_message(message.chat.id, "Добро пожаловать в бота! Пожалуйста, введите вашу дату рождения в формате ДД.ММ.ГГГГ:")
    elif user.date_of_birth:
        year = None
        markup_years = generate_markup_years(year)
        bot.send_message(message.chat.id, f"Здравствуйте, {user.first_name} {user.last_name}, Вы родились: {user.date_of_birth}\nВыберите год, который Вас интересует:", reply_markup=markup_years)
        bot.send_message(message.chat.id, "Или введите любой год:")
    else:
        bot.send_message(message.chat.id, "Пожалуйста, введите вашу дату рождения в формате ДД.ММ.ГГГГ:")

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

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    user_id = message.chat.id
    text = message.text

    user = get_user(user_id)
    
    # Увеличиваем счетчик сообщений
    user.message_count += 1
    user.save()
    
    # Попытка преобразовать ввод в дату
    try:
        birth_date = datetime.strptime(text, '%d.%m.%Y')
        if not user:
            # Если пользователя нет, регистрируем его с новой датой рождения
            register_user(user_id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, message.from_user.language_code, birth_date)
            markup_years = generate_markup_years(None)
            bot.send_message(user_id, "Дата рождения сохранена. Выберите интересующий Вас год:" , reply_markup=markup_years)
            bot.send_message(message.chat.id, "Или введите любой год:")
        else:
            # Если пользователь существует, обновляем его дату рождения
            user.date_of_birth = birth_date
            user.save()
            markup_years = generate_markup_years(None)
            bot.send_message(user_id, "Дата рождения обновлена. Выберите интересующий Вас год:", reply_markup=markup_years)
            bot.send_message(message.chat.id, "Или введите любой год:")
    except ValueError:
        # Если ввод не соответствует формату даты
        if user and user.date_of_birth:
            # Обработка ввода года для пользователя с известной датой рождения
            if text.isdigit() and 1900 <= int(text) <= 2100:
                birth_date_str = user.date_of_birth.strftime('%d.%m.%Y')
                text_for_A, date_range = calculate_from_date(f"{birth_date_str.split('.')[0]}.{birth_date_str.split('.')[1]}.{text}")
                markup_years = generate_markup_years(int(text))
                bot.send_message(
                                user_id,
                                f"{text_for_A}\nДиапазон дат: {date_range}.\n\n<a href='https://t.me/+0GIGNtFqT-pmY2Vi'>Подпишитесь на наш ТГ-канал</a>",
                                parse_mode='HTML',
                                reply_markup=markup_years
                            )
                bot.send_message(message.chat.id, "Или введите любой год:")
            else:
                bot.send_message(user_id, "Некорректный ввод. Введите интересующий Вас год (от 1900 до 2100):")
        elif user and not user.date_of_birth:
            # Пользователь существует, но дата рождения неизвестна
            bot.send_message(user_id, "Пожалуйста, введите вашу дату рождения в формате ДД.ММ.ГГГГ.")
        else:
            # Пользователь не зарегистрирован
            bot.send_message(user_id, "Для начала использования бота, пожалуйста, введите вашу дату рождения в формате ДД.ММ.ГГГГ.")

@bot.callback_query_handler(func=lambda call: True)
def button_click(call):
    # Получаем текст кнопки
    button_text = call.data
    # Получаем ID пользователя, который нажал на кнопку
    user_id = call.from_user.id
    # Изменяем текст в существующем сообщении (так и не понял, зачем это нужно)
    call.message.text = button_text
    # Вызываем обработчик всех сообщений с модифицированным сообщением
    handle_all_messages(call.message)

print("Бот запущен")
bot.polling(non_stop=True, interval=0)