import time
import pymysql
import csv

specific_val = "SPECIFIC_VALUE"

start_file = time.time()
with open("very_big_db.csv", "r") as db:
    for row in csv.reader(db):
        if row[0] == specific_val:
            break
time_file = time.time() - start_file

start_db = time.time()
conn = pymysql.connect(host="localhost", user="root", password="", db="db_test", charset="utf8")
cur = conn.cursor()
sql = f"select * from very_big_table where col0='{specific_val}'"
cur.execute(sql)
conn.close()
time_db = time.time() - start_db

print(f"time_file: {time_file}, time_db: {time_db}")
