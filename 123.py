import os
from dotenv import load_dotenv

load_dotenv()  # 不帶路徑，用預設當前目錄

print("OPENAI_API_KEY =", os.getenv("OPENAI_API_KEY"))
print("JDOODLE_CLIENT_ID =", os.getenv("JDOODLE_CLIENT_ID"))
print("JDOODLE_CLIENT_SECRET =", os.getenv("JDOODLE_CLIENT_SECRET"))

import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request
from dotenv import load_dotenv
from openai import OpenAI
import requests
import textwrap

# -----------------------------
# 日誌設定
# -----------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -----------------------------
# 強制指定 .env 路徑並讀取
# -----------------------------
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path)

# -----------------------------
# 讀取環境變數
# -----------------------------
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # 注意 .env Key 要叫 OPENAI_API_KEY
DEBUG = os.getenv("DEBUG", "False").lower() == "true"
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
MAX_DESCRIPTION_LENGTH = int(os.getenv("MAX_DESCRIPTION_LENGTH", "1000"))

JDOODLE_CLIENT_ID = os.getenv("JDOODLE_CLIENT_ID")
JDOODLE_CLIENT_SECRET = os.getenv("JDOODLE_CLIENT_SECRET")
DAILY_LIMIT = 200

# 印出確認 Key 是否抓到
logger.info(f"OPENAI_API_KEY = {'已讀取' if OPENAI_API_KEY else None}")
logger.info(f"JDOODLE_CLIENT_ID = {'已讀取' if JDOODLE_CLIENT_ID else None}")
logger.info(f"JDOODLE_CLIENT_SECRET = {'已讀取' if JDOODLE_CLIENT_SECRET else None}")

# -----------------------------
# 驗證必要 Key
# -----------------------------
if not OPENAI_API_KEY:
    logger.warning("⚠️ 未設定 OPENAI_API_KEY，某些功能可能無法使用")
if not JDOODLE_CLIENT_ID or not JDOODLE_CLIENT_SECRET:
    logger.warning("⚠️ 未設定 JDoodle Key，相關功能可能無法使用")

# -----------------------------
# OpenAI 客戶端初始化
# -----------------------------
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI 客戶端初始化成功")
except Exception as e:
    logger.error(f"OpenAI 客戶端初始化失敗: {e}")
    client = None

# -----------------------------
# Flask 初始化
# -----------------------------
app = Flask(__name__)

# -----------------------------
# 程式碼模板
# -----------------------------
TEMPLATES = {
    "bfs": "...",          # 省略完整模板，跟你原本的一樣
    "dfs": "...",
    "dijkstra": "...",
    "merge_sort": "...",
    "sql_select": "..."
}

# -----------------------------
# 分類函數
# -----------------------------
def classify(desc):
    if not desc:
        return None
    text = desc.lower()
    if any(k in text for k in ["bfs", "breadth"]):
        return "bfs"
    if any(k in text for k in ["dfs", "depth"]):
        return "dfs"
    if "dijkstra" in text:
        return "dijkstra"
    if any(k in text for k in ["sort", "merge"]):
        return "merge_sort"
    if any(k in text for k in ["sql", "select"]):
        return "sql_select"
    return None

# -----------------------------
# Flask 主頁
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = optimization_advice = complexity_text = lint_result = simulated_output = jdoodle_output = language = None
    quota_exceeded = False
    error_message = None

    if request.method == "POST":
        try:
            description = request.form.get("description", "").strip()
            language = request.form.get("language", "Python")
            test_input = request.form.get("test_input", "")

            if not description:
                error_message = "請提供需求描述"
                return render_template("index.html", error_message=error_message)

            if len(description) > MAX_DESCRIPTION_LENGTH:
                error_message = f"需求描述過長（最多 {MAX_DESCRIPTION_LENGTH} 字元）"
                return render_template("index.html", error_message=error_message)

            category = classify(description)
            template = TEMPLATES.get(category, "")

            # 這裡你可以呼叫 generate_with_gpt(template, description, language) 等函數
            # 暫時先示範回傳模板名稱
            result = f"已分類為: {category}, 模板內容: {template[:30]}..."

        except Exception as e:
            logger.error(f"請求處理失敗: {e}", exc_info=True)
            error_message = f"處理失敗：{str(e)}"

    return render_template(
        "index.html",
        result=result,
        language=language,
        error_message=error_message
    )

if __name__ == "__main__":
    logger.info(f"啟動應用程式 (Debug={DEBUG})")
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)
