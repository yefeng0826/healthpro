from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from predict import predict_diabetes
from datetime import datetime
import json
import os

# 🛠 回到项目根目录
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance/users.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# 用户数据模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='user')

# 用户资料模型（Profile）
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    name = db.Column(db.String(100))
    gender = db.Column(db.String(10))
    age = db.Column(db.Integer)
    contact_info = db.Column(db.String(200))

# 风险评估模型
class RiskAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    health_data = db.Column(db.Text)
    risk_level = db.Column(db.String(10))
    assessment_date = db.Column(db.DateTime)

# 反馈模型
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)
    username = db.Column(db.String(80))
    message = db.Column(db.Text)
    reply = db.Column(db.Text)
    feedback_date = db.Column(db.DateTime)

# 首页
@app.route('/')
def index():
    return render_template('index.html')

# 登录
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        user = User.query.filter_by(username=uname).first()

        if user and check_password_hash(user.password, pwd):
            session['user'] = uname
            session['user_id'] = user.id

            if user.role == 'admin':
                session['admin_logged_in'] = True
                return redirect(url_for('admin_feedback'))  # 管理员跳转反馈管理
            else:
                return redirect(url_for('profile'))  # 普通用户跳转 profile

        else:
            return "Invalid credentials. Try again."
    
    return render_template('login.html')


# 注册
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        uname = request.form['username']
        pwd = request.form['password']
        if User.query.filter_by(username=uname).first():
            return "⚠️ 用户已存在！"
        hashed_pwd = generate_password_hash(pwd)
        new_user = User(username=uname, password=hashed_pwd)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# 用户资料
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    profile = Profile.query.filter_by(user_id=user_id).first()
    if request.method == 'POST':
        name = request.form['name']
        gender = request.form['gender']
        age = request.form['age']
        contact = request.form['contact']
        if profile:
            profile.name = name
            profile.gender = gender
            profile.age = age
            profile.contact_info = contact
        else:
            profile = Profile(user_id=user_id, name=name, gender=gender, age=age, contact_info=contact)
            db.session.add(profile)
        db.session.commit()
        return redirect(url_for('form'))
    return render_template('profile.html', profile=profile)

# 表单页面
@app.route('/form')
def form():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('form.html')

# 预测处理 + 保存记录
@app.route('/predict', methods=['POST'])
def predict():
    if 'user' not in session:
        return redirect(url_for('login'))

    input_data = {
        'Age': int(request.form['age']),
        'Gender': 1 if request.form['gender'] == 'Female' else 0,
        'Glucose': float(request.form['glucose']),
        'BloodPressure': float(request.form['bloodpressure']),
        'SkinThickness': float(request.form['skinthickness']),
        'Insulin': float(request.form['insulin']),
        'BMI': float(request.form['bmi']),
        'Polyphagia': 1 if request.form.get('polyphagia') == 'Yes' else 0,
        'DelayedHealing': 1 if request.form.get('healing') == 'Yes' else 0,
        'Obesity': 1 if request.form.get('obesity') == 'Yes' else 0
    }

    result = predict_diabetes(input_data)
    risk = result['risk_level']

    # 保存评估记录
    assessment = RiskAssessment(
        user_id=session['user_id'],
        health_data=json.dumps(input_data),
        risk_level=risk,
        assessment_date=datetime.now()
    )
    db.session.add(assessment)
    db.session.commit()

    return redirect(url_for(f'result_{risk.lower()}'))

# 历史评估记录页面
@app.route('/assessment/history')
def assessment_history():
    if 'user' not in session:
        return redirect(url_for('login'))
    records = RiskAssessment.query.filter_by(user_id=session['user_id']).all()
    return render_template('history.html', records=records)

# 结果页
@app.route('/result_low')
def result_low():
    return render_template('result_low.html')

@app.route('/result_medium')
def result_medium():
    return render_template('result_medium.html')

@app.route('/result_high')
def result_high():
    return render_template('result_high.html')

# ✅ 用户反馈填写页面（用户看到的页面）
@app.route('/feedbackuser')
def feedback_user():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('feedbackuser.html')  # 专属用户表单页面

# ✅ 用户提交反馈表单（数据库保存）
@app.route('/feedback/send', methods=['POST'])
def send_feedback():
    if 'user' not in session:
        return redirect(url_for('login'))
    feedback_text = request.form['feedback']
    username = session['user']
    fb = Feedback(
        user_id=session['user_id'],
        username=username,
        message=feedback_text,
        feedback_date=datetime.now()
    )
    db.session.add(fb)
    db.session.commit()
    return "感谢你的反馈！"  # 你也可以改成 redirect(url_for('index'))

# 管理员登录页面你已有，这里略过...

#  管理员查看所有反馈（管理员页面）
@app.route('/admin/feedback')
def admin_feedback():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    feedbacks = Feedback.query.all()
    return render_template('Feedback.html', feedbacks=feedbacks)

# 管理员标记反馈为已读
@app.route('/admin/resolve', methods=['POST'])
def mark_feedback_resolved():
    if not session.get('admin_logged_in'):
        return 'Unauthorized', 403

    fb_id = request.form.get('feedback_id')
    fb = Feedback.query.get(fb_id)

    if fb:
        fb.resolved = True  # 更新字段
        db.session.commit()
        return '已标记为已读'
    else:
        return 'Feedback not found', 404


# ✅ 管理员提交回复
@app.route('/admin/reply', methods=['POST'])
def admin_reply():
    if not session.get('admin_logged_in'):
        return 'Unauthorized', 403
    fb_id = request.form['feedback_id']
    reply_text = request.form['reply']
    fb = Feedback.query.get(fb_id)
    if fb:
        fb.reply = reply_text
        db.session.commit()
        return 'Reply saved'
    else:
        return 'Feedback not found', 404


# 管理员登出
@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))

# 用户登出
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# 启动应用
if __name__ == '__main__':
    with app.app_context():
        db.create_all()

    import os
    port = int(os.environ.get("PORT", 5000))  # Render 会自动提供 PORT
    app.run(host="0.0.0.0", port=port)

