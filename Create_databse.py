import sqlite3

# Connect to the SQLite database (creates a new database if not exists)
conn = sqlite3.connect('money.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()

# Execute a SQL statement to create a new table
# cursor.execute('''CREATE TABLE IF NOT EXISTS category (
#                     id INTEGER PRIMARY KEY,
#                     name TEXT
#                 )''')

# # Create 'expense' table with a foreign key reference to 'category' table
# cursor.execute('''CREATE TABLE IF NOT EXISTS expense (
#                     id INTEGER PRIMARY KEY,
#                     date TEXT NOT NULL,
#                     price REAL NOT NULL,
#                     category_id INTEGER,
#                     comments TEXT,
#                     FOREIGN KEY (category_id) REFERENCES category(id)
#                 )''')
# cursor.execute('''ALTER TABLE expense RENAME TO expense_old''')

# # Step 2: Create a new table with updated default value for 'comments'
# cursor.execute('''CREATE TABLE expense (
#                     id INTEGER PRIMARY KEY,
#                     date TEXT NOT NULL,
#                     price REAL NOT NULL,
#                     category_id INTEGER,
#                     comments TEXT DEFAULT ''
#                 )''')

# Step 3: Copy data from the old table to the new table
# cursor.execute('''CREATE TABLE maximum
# (id integer primary key,
# value real not null)''')

# Insert 1000 as the daily budget
cursor.execute("INSERT INTO maximum (value) VALUES (?)", (1000,))

# Insert 7000 as the weekly budget
cursor.execute("INSERT INTO maximum (value) VALUES (?)", (7000,))

# Insert 30000 as the monthly budget
cursor.execute("INSERT INTO maximum (value) VALUES (?)", (30000,))

# Step 4: Drop the old table

# from datetime import datetime
# today = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# # Insert an expense into the 'expense' table
# for i in range(100):
#     price = 2000+10*i
#     category_id = 1
#     cursor.execute("INSERT INTO expense (date, price, category_id) VALUES (?, ?, ?)",
#                     (today, price, category_id))
    

# Commit the transaction
conn.commit()

# Close the cursor and the connection
cursor.close()
conn.close()