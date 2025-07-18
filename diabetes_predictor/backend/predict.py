# backend/predict.py
import os
import joblib
import pandas as pd


# 1. 加载训练好的模型

# 获取当前文件所在目录，无论从哪里执行都能定位对
current_dir = os.path.dirname(os.path.abspath(__file__))
model_path = os.path.join(current_dir, "model.pkl")
model = joblib.load(model_path)


# 2. 加载和保存 label 编码器（如果你的训练用了 LabelEncoder，也应保存并加载）
# 这里只是演示不含编码逻辑

# 3. 定义预测函数
def predict_diabetes(input_dict):
    """
    输入：字典类型的用户输入，例如：
    {
        "Age": 45,
        "Gender": "Male",
        "Glucose": 120,
        ...
    }

    输出：预测结果（风险等级）
    """
    # 转换为 DataFrame（必须保持和训练时一致的列顺序）
    input_df = pd.DataFrame([input_dict])

    # 执行预测
    probability = model.predict_proba(input_df)[0][1]  # 预测患病的概率
    prediction = model.predict(input_df)[0]            # 预测分类（0 或 1）

    # 显示风险等级
    if probability < 0.33:
        risk_level = "Low"
    elif probability < 0.66:
        risk_level = "Medium"
    else:
        risk_level = "High"

    return {
        "prediction": int(prediction),
        "probability": round(probability, 2),
        "risk_level": risk_level
    }

# 示例测试（你运行此文件会看到结果）
if __name__ == "__main__":
    test_input = {
        "Age": 45,
        "Gender": 1,           # 注意：性别要先在前端转换为数值或使用LabelEncoder
        "Glucose": 130,
        "BloodPressure": 80,
        "SkinThickness": 20,
        "Insulin": 85,
        "BMI": 30.2,
        "Polyphagia": 1,
        "delayed healing": 1,
        "Obesity": 1
    }

    result = predict_diabetes(test_input)
    print("✅ 预测结果：", result)
