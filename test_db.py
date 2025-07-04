import sqlite3;

conn = sqlite3.connect('pl.db')

c = conn.cursor()

def insert_cat(name, description, icon):
    with conn:
        c.execute(
            "INSERT INTO categories (name, description, icon) VALUES (:name, :description, :icon)",
        {'name': name, 'description': description, 'icon': icon}
)

insert_cat('Study', 'Studying away', '📚')

c.execute("SELECT * FROM categories")
rows = c.fetchall()
print(rows)

conn.close()
