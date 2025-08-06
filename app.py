from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from models import db
from routes.analysis import analysis_bp
from routes.customers import customers_bp
from routes.dashboard import dashboard_bp
from routes.contact_records import contact_bp
from routes.terminology_management import terminology_bp
from dotenv import load_dotenv
import os


load_dotenv()
print("[环境检查] DEEPSEEK_API_KEY:", os.getenv("DEEPSEEK_API_KEY"))



app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///customers.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = 's3cr3t_k3y_2025_xgy'  # ✅ 设置密钥以支持 session/flash


# 初始化数据库
db.init_app(app)

# 注册蓝图模块
app.register_blueprint(contact_bp)
app.register_blueprint(customers_bp)
app.register_blueprint(analysis_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(terminology_bp)


from flask import render_template, redirect
from datetime import datetime

@app.context_processor
def inject_now():
    return {'now': datetime.now}

@app.route("/")
def home():
    return render_template("index.html")

# 创建数据库表
with app.app_context():
    db.create_all()


if __name__ == "__main__":
    app.run(debug=True)
