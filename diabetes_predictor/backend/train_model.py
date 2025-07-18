# backend/train_model.py

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report
import joblib

# 1. 读取数据
data_path = os.path.join(os.path.dirname(__file__), "../data/diabetes_Dataset_cleaned.csv")
df = pd.read_csv(data_path)

# 2. 简单预处理（填补空值，编码类别变量）
df['Polyphagia'].fillna('No', inplace=True)

# 3. 对 Gender, Polyphagia, delayed healing, Obesity 等类别变量进行编码
categorical_cols = ['Gender', 'Polyphagia', 'delayed healing', 'Obesity']
label_encoders = {}

for col in categorical_cols:
    le = LabelEncoder()
    df[col] = le.fit_transform(df[col])
    label_encoders[col] = le

# 4. 特征和标签分离
X = df.drop(columns=['Outcome'])  # 特征
y = df['Outcome']                 # 标签

# 5. 拆分训练集和测试集
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 6. 训练随机森林模型
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 7. 模型评估
y_pred = model.predict(X_test)
print("模型评估报告：")
print(classification_report(y_test, y_pred))

# 8. 保存模型
joblib.dump(model, "model.pkl")
print("模型已保存为 model.pkl")
