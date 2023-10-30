import os
import telebot
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from user_stat import UserStat, db
from logger import setup_logger

logger = setup_logger()

try:
    from dotenv import load_dotenv
    load_dotenv()
    IS_DEV = os.getenv('ENV') == 'DEVELOPMENT'
except ImportError:
    IS_DEV = False

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_CHAT_ID = 169675602
bot = telebot.TeleBot(BOT_TOKEN)

def register_user(user_id, username, first_name, last_name, language_code, birth_date):
    user, created = UserStat.get_or_create(
        user_id=user_id,
        defaults={
            'username': username,
            'first_name': first_name,
            'last_name': last_name,
            'language_code': language_code,
            'date_of_birth': birth_date
        })
    
    if not created:
        user.date_of_birth = birth_date
        user.save()

def get_user(user_id):
    try:
        user = UserStat.get(UserStat.user_id == user_id)
        return user
    except UserStat.DoesNotExist:
        return None

def get_total_users():
    return UserStat.select().count()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = get_user(message.chat.id)
    if user:
        bot.send_message(message.chat.id, f"Здравствуйте, {user.first_name} {user.last_name}, Вы родились: {user.date_of_birth}\nВведите год, который Вас интересует:")
    else:
        bot.send_message(message.chat.id, "Введите вашу дату рождения в формате ДД.ММ.ГГГГ:")

@bot.message_handler(func=lambda message: True)
def birth_date_handler(message):
    chat_id = message.chat.id
    text = message.text
    
    # Добавим здесь проверку на админский ID
    if text == '/stat' and chat_id == ADMIN_CHAT_ID:
        return send_stats(message)
    
    user = get_user(chat_id)
    
    if not user:
        # Обработка даты рождения
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
    else:
        # Обработка интересующего года
        if text.isdigit() and 1900 <= int(text) <= 2100:
            year_of_interest = int(text)
            birth_date_str = user.date_of_birth.strftime('%d.%m.%Y')
            text_for_A, date_range = calculate_from_date(f"{birth_date_str.split('.')[0]}.{birth_date_str.split('.')[1]}.{year_of_interest}")
            bot.send_message(chat_id, f"{text_for_A}\nДиапазон дат: {date_range}")
        else:
            bot.send_message(chat_id, "Некорректный ввод. Введите интересующий Вас год (от 1900 до 2100).")

def calculate_from_date(date_str):
    day, month, year = map(int, date_str.split('.'))
    
    D1, D2 = divmod(day, 10)
    M1, M2 = divmod(month, 10)
    Y1, Y2 = divmod(year // 100, 10)
    Y3, Y4 = divmod(year % 100, 10)

    R = D1 + D2 + M1 + M2 + Y1 + Y2 + Y3 + Y4
    R1, R2 = divmod(R, 10)
    A = R1 + R2
    if A > 9:
        A1, A2 = divmod(A, 10)
        A = A1 + A2

    texts = [
        "1-ый ЛИЧНЫЙ ГОД\nНАЧИНАНИЕ\nГод новых идей. Необходимо продумать план на 9 лет. Положиться на себя, быть независимым. Прокладывать новые пути",
        "2-ой ЛИЧНЫЙ ГОД\nТЕРПЕНИЕ\nБлагоприятна совместная работа в команде, обучение, накопление знаний. Необходимо проявлять дипломатию, тактичность, думать, сохранять душевный покой. Удача в любви",
        "3-ий ЛИЧНЫЙ ГОД\nРАДОСТЬ\nЛичный год для радости. Необходимо больше самовыражаться в творчестве, верить в себя, позволить себе отдохнуть",
        "4-ый ЛИЧНЫЙ ГОД\nПРАКТИЧНОСТЬ\nБыть организованным и производительным, строить прочный фундамент, избегать лени, опираться на самодисциплину. Всё делать охотно, тогда придёт энергия. Усилия приведут к успеху",
        "5-ый ЛИЧНЫЙ ГОД\nИЗМЕНЕНИЕ\nГод перемен, свободы. Надо сделать решительный шаг вперёд. Нарушить заведённый распорядок. Измениться, создавать перемены – в себе, в своём доме, в образе жизни, но не во вред другим. Не терять бдительности и собранности.",
        "6-ой ЛИЧНЫЙ ГОД\nОТВЕТСТВЕННОСТЬ\nСделать дом центром своей жизни. Быть честным и справедливым к другим и себе. Принимать свои обязанности с готовностью и желанием. Это лучший год для брака, для улучшения жилищных условий. Всем помогать, давать советы.",
        "7-ой ЛИЧНЫЙ ГОД\nВЕРА\nГод духовного роста. Уделить время размышлениям, самоанализу, учёбе, профессиональному росту. Анализировать свои мысли, поступки – что бы Вы хотели изменить в себе? Продумать своё отношение к жизни. Проявлять интерес к науке, эзотерике.  Необходимо научиться работать со своими ошибками",
        "8-ой ЛИЧНЫЙ ГОД\nУСПЕХ\nВремя «сбора урожая». Успех в бизнесе. Идти за тем, чего желаете. Быть деловитым, организованным, уверенным в себе. Можно надеяться на неожиданные деньги. Благоприятны деловые поездки.",
        "9-ый ЛИЧНЫЙ ГОД\nЗАВЕРШЕНИЕ, РАЗРУШЕНИЕ\nОтпустить ненужные идеи, отношения, вещи. Не начинать ничего нового. Уступать. Быть великодушным и сострадательным. Можно с успехом путешествовать."
    ]
    text_for_A = texts[A - 1]
    start_date = datetime.strptime(date_str, '%d.%m.%Y')

    end_date = start_date + relativedelta(years=+1)  # Добавляем один год
    end_date -= timedelta(days=1)  # Вычитаем один день
    
    date_range = f"{start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}"

    return text_for_A, date_range

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


if not IS_DEV:
    from background import keep_alive
    keep_alive()

if __name__ == '__main__':
    bot.polling(none_stop=True)