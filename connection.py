import mysql.connector as msc

def mycon():
    conn= msc.connect(
    host="sql12.freesqldatabase.com",
    username="sql12765630",
    password="etEtC47gwJ",
    database="sql12765630"
    )
    return conn

# if conn.is_connected():
#     print("Connection Established")
