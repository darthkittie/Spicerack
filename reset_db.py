import os
import sqlite3


def reset_database(db_path: str = 'recipes.db') -> None:
    # Remove existing database file if present
    if os.path.exists(db_path):
        os.remove(db_path)

    # Recreate database and tables
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            nutrition_info TEXT,
            image_url TEXT,
            source_url TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS user_ingredients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ingredient_name TEXT NOT NULL,
            quantity TEXT,
            unit TEXT,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS saved_recipes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            recipe_id INTEGER,
            user_rating INTEGER,
            notes TEXT,
            saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id)
        )
    ''')

    conn.commit()
    conn.close()


if __name__ == '__main__':
    reset_database()
    print('Database reset complete: recipes.db recreated with empty tables.')
