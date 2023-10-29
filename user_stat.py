from peewee import Model, SqliteDatabase, CharField, IntegerField, DateField

db = SqliteDatabase('statistics.db')

class UserStat(Model):
    user_id = IntegerField(primary_key=True)
    username = CharField(null=True)
    first_name = CharField(null=True)
    last_name = CharField(null=True)
    language_code = CharField(null=True)
    date_of_birth = DateField(null=True)

    class Meta:
        database = db

def initialize_db():
    db.connect()
    db.create_tables([UserStat], safe=True)

if __name__ == "__main__":
    initialize_db()