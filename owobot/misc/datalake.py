import logging
import time
from abc import ABC, abstractmethod
import csv
import threading
from os import path
from typing import NamedTuple, TextIO
from pyspark.shell import spark
from pyspark.sql.functions import from_unixtime
import pyspark.sql.types as T

log = logging.getLogger(__name__)


class DataLake(ABC):
    @abstractmethod
    def put_row(self, table, row):
        pass

    @abstractmethod
    def get_df(self, table):
        pass


class CSVHandle(NamedTuple):
    writer: csv.DictWriter
    file: TextIO
    path: str
    schema: T.StructType


class CSVDataLake(DataLake):
    def __init__(self, directory):
        msgspath = path.join(directory, "msgs.csv")
        msgsfile = open(msgspath, "a", newline="", encoding="utf-8")
        msgwriter = csv.DictWriter(
            msgsfile,
            fieldnames=[
                "msg_id",
                "author_id",
                "channel_id",
                "guild_id",
                "time",
                "msg",
            ],
            quoting=csv.QUOTE_MINIMAL,
        )
        msgschema = T.StructType(
            [
                T.StructField("msg_id", T.LongType(), False),
                T.StructField("author_id", T.LongType(), False),
                T.StructField("channel_id", T.LongType(), False),
                T.StructField("guild_id", T.LongType(), False),
                T.StructField("time", T.DoubleType(), False),
                T.StructField("msg", T.StringType(), False),
            ]
        )
        self.writers = {"msgs": CSVHandle(msgwriter, msgsfile, msgspath, msgschema)}
        self.csv_writer_lock = threading.Lock()

    def put_row(self, table, row):
        if table not in self.writers:
            return
        with self.csv_writer_lock:
            handle = self.writers[table]
            if table == "msgs":
                row["time"] = time.time()
            handle.writer.writerow(row)
            handle.file.flush()

    def get_df(self, table):
        handle = self.writers[table]
        df = (
            spark.read.schema(handle.schema)
            .options(mode="FAILFAST", multiLine=True, escape='"', header=True)
            .csv(handle.path)
        )
        if table == "msgs":
            df = df.withColumn("time", from_unixtime("time"))
        return df
