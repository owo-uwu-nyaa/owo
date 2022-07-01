import peewee
from peewee import DatabaseProxy, Model, BigIntegerField, TextField, CompositeKey

db = DatabaseProxy()


class BaseModel(Model):
    class Meta:
        database = db


class Owner(BaseModel):
    snowflake = BigIntegerField(primary_key=True)


class NsflChan(BaseModel):
    channel = BigIntegerField(primary_key=True)


class OwoChan(BaseModel):
    channel = BigIntegerField(primary_key=True)


class MusicChan(BaseModel):
    channel = BigIntegerField(primary_key=True)


class KirbySpam(BaseModel):
    user_id = BigIntegerField(primary_key=True)


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


class BaaPics(BaseModel):
    picture = TextField()


class MooPics(BaseModel):
    picture = TextField()


class AwooPics(BaseModel):
    picture = TextField()


class RawwrPics(BaseModel):
    picture = TextField()


class NyaaPics(BaseModel):
    picture = TextField()


class PikaPics(BaseModel):
    picture = TextField()


class BaaUsers(BaseModel):
    snowflake = BigIntegerField()


class MooUsers(BaseModel):
    snowflake = BigIntegerField()


class AwooUsers(BaseModel):
    snowflake = BigIntegerField()


class RawwrUsers(BaseModel):
    snowflake = BigIntegerField()


class NyaaUsers(BaseModel):
    snowflake = BigIntegerField()


class PikaUsers(BaseModel):
    snowflake = BigIntegerField()


class RainbowGuild(BaseModel):
    snowflake = BigIntegerField()


def set_db(real_db: peewee.Database):
    db.initialize(real_db)
    db.create_tables(
        [
            Owner,
            NsflChan,
            HugShort,
            Consent,
            HugConsent,
            OwoChan,
            KirbySpam,
            MusicChan,
            BaaPics,
            MooPics,
            AwooPics,
            RawwrPics,
            NyaaPics,
            PikaPics,
            BaaUsers,
            MooUsers,
            AwooUsers,
            RawwrUsers,
            NyaaUsers,
            PikaUsers,
            RainbowGuild
        ]
    )
