import time
from abc import ABC, abstractmethod
import csv
import threading
from os import path
from typing import NamedTuple, TextIO
from pyspark.shell import spark
from pyspark.sql.functions import from_unixtime
from pyspark.sql.types import *


class DataLake(ABC):

    @abstractmethod
    def put_row(self, table, row):
        pass

    @abstractmethod
    def get_df(self, table):
        pass


class KuduDataLake(DataLake):
    def __init__(self, khosts, kports, table_prefix):
        # use local import as installing kudu-python requires 50GB of Diskspace and compiling for a few hours
        import kudu
        self.khosts = khosts
        self.kports = kports
        self.client = kudu.connect(khosts, kports)
        self.session = self.client.new_session()
        self.kudu_writer_lock = threading.Lock()
        self.table_prefix = table_prefix

    def put_row(self, table, row):
        with self.kudu_writer_lock:
            table = self.client.table(f"{self.table_prefix}.{table}")
            op = table.new_insert(row)
            self.session.apply(op)
            self.session.flush()

    def get_df(self, table):
        masters = []
        for i in range(0, len(self.khosts)):
            masters.append(f"{self.khosts[i]}:{self.kports[i]}")
        optdict = {"kudu.master": ",".join(masters),
                   "kudu.table": f"{self.table_prefix}.{table}"}
        return spark.read.format('org.apache.kudu.spark.kudu').options(**optdict).load()


class CSVHandle(NamedTuple):
    writer: csv.DictWriter
    file: TextIO
    path: str
    schema: StructType


class CSVDataLake(DataLake):
    def __init__(self, dir):
        msgspath = path.join(dir, "msgs.csv")
        msgsfile = open(msgspath, "a", newline='')
        msgwriter = csv.DictWriter(msgsfile,
                                   fieldnames=["snowflake", "author_id", "channel_id", "guild_id", "time", "msg"],
                                   quoting=csv.QUOTE_MINIMAL)
        msgschema = StructType([
            StructField("snowflake", LongType(), False),
            StructField("author_id", LongType(), False),
            StructField("channel_id", LongType(), False),
            StructField("guild_id", LongType(), False),
            StructField("time", DoubleType(), False),
            StructField("msg", StringType(), False)
        ])
        self.writers = {"msgs": CSVHandle(msgwriter, msgsfile, msgspath, msgschema)}
        self.csv_writer_lock = threading.Lock()

    def put_row(self, table, row):
        with self.csv_writer_lock:
            handle = self.writers[table]
            if table == "msgs":
                row["time"] = time.time()
            handle.writer.writerow(row)
            handle.file.flush()

    def get_df(self, table):
        handle = self.writers[table]
        df = spark.read.schema(handle.schema) \
            .options(mode='FAILFAST', multiLine=True, escape='"', header=True) \
            .csv(handle.path)
        if table == "msgs":
            df = df.withColumn("time", from_unixtime("time"))
        return df
