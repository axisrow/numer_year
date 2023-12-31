#user_stat.py - только создает пустую базу данных
from peewee import Model, SqliteDatabase, CharField, IntegerField, DateField, DateTimeField

db = SqliteDatabase('userstat.db')

class UserStat(Model):
    user_id = IntegerField(primary_key=True)
    registration_time_utc = DateTimeField(null=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    language_code = CharField(null=True)
    date_of_birth = DateField(null=True)
    utm_source = CharField(null=True)
    message_count = IntegerField(default=0)

    class Meta:
        database = db

def initialize_db():
    db.connect()
    db.create_tables([UserStat], safe=True)

if __name__ == "__main__":
    initialize_db()