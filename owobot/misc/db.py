import peewee
from peewee import *

db_prox = DatabaseProxy()

class BaseModel(Model):
    class Meta:
        database = db_prox


class Admin(BaseModel):
    snowflake = BigIntegerField(primary_key=True)

def set_db(db: peewee.Database):
    db_prox.initialize(db)
    db.create_tables([Admin])