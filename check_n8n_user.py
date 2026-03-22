import sqlite3
conn = sqlite3.connect(r'C:\Users\王鼎傑\.n8n\database.sqlite')
cur = conn.cursor()
cur.execute('SELECT email, firstName FROM user')
rows = cur.fetchall()
for row in rows:
    print(row)
