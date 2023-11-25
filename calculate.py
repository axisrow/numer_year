from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

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