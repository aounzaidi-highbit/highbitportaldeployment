import mysql.connector
database=mysql.connector.connect(
    host='localhost',
    user='root',
    passwd='123456789'
)

cursor_object=database.cursor()
cursor_object.execute("CREATE DATABASE elderco")
print("ALL DONE")