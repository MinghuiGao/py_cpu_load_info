#!/usr/bin/python

import sqlite3

# 打开数据库连接
conn = sqlite3.connect('py-sqlite.db')
print("Opened database successfully")

# 创建一个表 - company
conn.execute('''CREATE TABLE company
       (ID INT PRIMARY KEY     NOT NULL,
       NAME           TEXT    NOT NULL,
       AGE            INT     NOT NULL,
       ADDRESS        CHAR(50),
       SALARY         REAL);''')
print("Table created successfully")

conn.close()
