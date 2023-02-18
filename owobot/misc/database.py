import peewee
from peewee import DatabaseProxy, Model, BigIntegerField, TextField, CompositeKey
from playhouse.migrate import migrate, SchemaMigrator, Field
from playhouse.reflection import Introspector

db = DatabaseProxy()


def _model_meta(model):
    # this field *is* documented
    return model._meta


def _add_column(model: Model, column: Field, introspector: Introspector, migrator: SchemaMigrator):
    table_name = _model_meta(model).name
    column_name = column.column_name
    models = introspector.generate_models(table_names=[table_name])
    # table doesn't exist yet, will be created normally
    if table_name not in models:
        return
    if column_name not in _model_meta(models[table_name]).columns:
        # column needs to be added
        yield migrator.add_column(table_name, column_name, column)


class BaseModel(Model):
    class Meta:
        database = db


class Owner(BaseModel):
    snowflake = BigIntegerField(primary_key=True)


class NsflChan(BaseModel):
    channel = BigIntegerField(primary_key=True)


class OwoChan(BaseModel):
    channel = BigIntegerField(primary_key=True)
    last_author = BigIntegerField(null=True)
    last_message = BigIntegerField(null=True)


def _owochan_last_author_migration(introspector: Introspector, migrator: SchemaMigrator):
    yield from _add_column(OwoChan, OwoChan.last_author, introspector, migrator)
    yield from _add_column(OwoChan, OwoChan.last_message, introspector, migrator)


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


class QuackUsers(BaseModel):
    snowflake = BigIntegerField()


class QuackPics(BaseModel):
    picture = TextField()


class RainbowGuild(BaseModel):
    snowflake = BigIntegerField()


class Calendar(BaseModel):
    guild = BigIntegerField()
    user = BigIntegerField()
    token = TextField(unique=True)

    class Meta:
        primary_key = CompositeKey("guild", "user")


def set_db(real_db: peewee.Database, migrator: SchemaMigrator):
    db.initialize(real_db)
    introspector = Introspector.from_database(db)
    with db.atomic():
        migrate(
            *_owochan_last_author_migration(introspector, migrator)
        )
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
            QuackPics,
            QuackUsers,
            RainbowGuild,
            Calendar
        ]
    )
