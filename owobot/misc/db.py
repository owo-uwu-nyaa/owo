import peewee
from peewee import *

db_prox = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = db_prox


class Owner(BaseModel):
    snowflake = BigIntegerField(primary_key=True)


class NsflChan(BaseModel):
    channel = BigIntegerField(primary_key=True)


class OwoChan(BaseModel):
    channel = BigIntegerField(primary_key=True)


class HugShort(BaseModel):
    key = TextField(primary_key=True)
    val = TextField()


class Consent(BaseModel):
    snowflake = BigIntegerField(primary_key=True)


class HugConsent(BaseModel):
    snowflake = BigIntegerField()
    target = BigIntegerField()

    class Meta:
        primary_key = CompositeKey("snowflake", "target")


def set_db(db: peewee.Database):
    db_prox.initialize(db)
    db.create_tables([Owner, NsflChan, HugShort, Consent, HugConsent, OwoChan])
