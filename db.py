import csv
import sqlite3
conn = sqlite3.connect("sherlock.db")
cursor = conn.cursor()

query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)
query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

query = "INSERT INTO sys_command VALUES (null,'anydesk', 'C:\\Program Files (x86)\\AnyDesk\\AnyDesk.exe')"
cursor.execute(query)
conn.commit()

query = "INSERT INTO web_command VALUES (null,'facebook web', 'https://www.facebook.com/')"
cursor.execute(query)
conn.commit()

query = "INSERT INTO web_command VALUES (null,'whatsapp web', 'https://www.whatsapp.com/')"
cursor.execute(query)
conn.commit()

query = "INSERT INTO web_command VALUES (null,'instagram web', 'https://www.instagram.com/')"
cursor.execute(query)
conn.commit()




cursor.execute('''CREATE TABLE IF NOT EXISTS contacts (id INTEGER PRIMARY KEY, name VARCHAR(200), Phone VARCHAR(255), email VARCHAR(255) NULL)''') 
desired_columns_indices = [0, 18]
with open('contacts.csv', 'r', encoding='latin-1') as file:
    csvreader = csv.reader(file)

    csvreader = csv.reader(file)
    for row in csvreader:
        selected_data = [row[i] for i in desired_columns_indices]
        cursor.execute(''' INSERT INTO contacts (id, 'name', 'Phone') VALUES (null, ?,? );''', tuple(selected_data))

# Commit changes and close connection
conn.commit()
conn.close()
print("data inserted successfully...")

query = "INSERT INTO contacts VALUES (null,'Sou', '8981247639', 'null')"
cursor.execute(query)
conn.commit() 

query = 'Rohan'
query = query.strip().lower()  

cursor.execute("SELECT Phone FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", 
               ('%' + query + '%', query + '%'))
results = cursor.fetchall()
print(results[0][0])