import time
import pymysql
import csv

start_file = time.time()
with open("very_big_db.csv", "r") as db:
        for row in db: