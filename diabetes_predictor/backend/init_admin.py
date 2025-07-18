# backend/init_admin.py

from app import db, User
from werkzeug.security import generate_password_hash
from app import app  # 确保导入 app

def create_admin():
    admin_username = "admin"
    admin_password = "admin123"  # 你可以自定义密码

    # ✅ 创建表结构（如果不存在的话）
    db.create_all()

    # 检查是否已有管理员
    if not User.query.filter_by(username=admin_username).first():
        admin = User(
            username=admin_username,
            password=generate_password_hash(admin_password),
            role='admin'
        )
        db.session.add(admin)
        db.session.commit()
        print("✅ 管理员账户创建成功！")
        print(f"👉 用户名: {admin_username}")
        print(f"👉 密码: {admin_password}")
    else:
        print("⚠️ 管理员账户已存在")

if __name__ == '__main__':
    with app.app_context():
        create_admin()
