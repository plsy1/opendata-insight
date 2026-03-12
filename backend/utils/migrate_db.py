import sqlite3
import os
import sys

# 获取数据库路径（模拟 backend/database/base.py 的逻辑）
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
db_path = os.path.join(backend_dir, "data", "database.db")

def migrate():
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at {db_path}")
        return

    print(f"Migrating database at {db_path}...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 添加 subscribe_order 列
        try:
            cursor.execute("ALTER TABLE actor_subscribe ADD COLUMN subscribe_order INTEGER DEFAULT 0 NOT NULL")
            print("Added column: subscribe_order")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("Column subscribe_order already exists.")
            else:
                raise e

        # 添加 collect_order 列
        try:
            cursor.execute("ALTER TABLE actor_subscribe ADD COLUMN collect_order INTEGER DEFAULT 0 NOT NULL")
            print("Added column: collect_order")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e).lower():
                print("Column collect_order already exists.")
            else:
                raise e

        conn.commit()
        conn.close()
        print("Migration completed successfully.")
        
    except Exception as e:
        print(f"Migration failed: {e}")

if __name__ == "__main__":
    migrate()
