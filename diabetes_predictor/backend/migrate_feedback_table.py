import sqlite3
import os

# 正确定位数据库文件（G:/Fianl year project/instance/users.db）
db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../instance/users.db'))

def migrate_feedback():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 检查是否已存在 resolved 字段
    cursor.execute("PRAGMA table_info(feedback);")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    if 'resolved' in column_names:
        print("⚠️ resolved 字段已存在，无需迁移。")
    else:
        cursor.execute("ALTER TABLE feedback ADD COLUMN resolved BOOLEAN DEFAULT 0;")
        conn.commit()
        print("✅ 成功添加 'resolved' 字段。")

    conn.close()

if __name__ == '__main__':
    migrate_feedback()
