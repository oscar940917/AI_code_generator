import os
import json
import logging
from datetime import datetime
from flask import Flask, render_template, request, jsonify
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
# 讀取環境變數與初始化
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# JDoodle API 相關
JDOODLE_CLIENT_ID = os.getenv("JDOODLE_CLIENT_ID")
JDOODLE_CLIENT_SECRET = os.getenv("JDOODLE_CLIENT_SECRET")
DAILY_LIMIT = 200

# 驗證必要的環境變數
if not OPENAI_API_KEY:
    logger.warning("未設定 OPENAI_API_KEY，某些功能可能無法使用")

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    logger.info("OpenAI 客戶端初始化成功")
except Exception as e:
    logger.error(f"OpenAI 客戶端初始化失敗: {e}")
    client = None

app = Flask(__name__)

# -----------------------------
# 程式碼模板（完整）
# -----------------------------
TEMPLATES = {
    "bfs": """
from collections import deque

def bfs(graph, start):
    visited = set([start])
    queue = deque([start])

    while queue:
        node = queue.popleft()
        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)
""",
    "dfs": """
def dfs(graph, node, visited=None):
    if visited is None:
        visited = set()
    visited.add(node)
    for neighbor in graph[node]:
        if neighbor not in visited:
            dfs(graph, neighbor, visited)
""",
    "dijkstra": """
import heapq

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]

    while pq:
        dist, node = heapq.heappop(pq)
        if dist > distances[node]:
            continue
        for neighbor, cost in graph[node]:
            new_dist = dist + cost
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                heapq.heappush(pq, (new_dist, neighbor))
    return distances
""",
    "merge_sort": """
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    mid = len(arr)//2
    left = merge_sort(arr[:mid])
    right = merge_sort(arr[mid:])
    return merge(left, right)

def merge(left, right):
    result = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] < right[j]:
            result.append(left[i])
            i += 1
        else:
            result.append(right[j])
            j += 1
    result.extend(left[i:])
    result.extend(right[j:])
    return result
""",
    "sql_select": """
-- 基本 SQL SELECT 模板
SELECT column1, column2
FROM table_name
WHERE condition;
"""
}

# -----------------------------
# 課程分類器（改進版）
# -----------------------------
def classify(desc):
    """根據描述分類算法類型"""
    if not desc:
        return None
    
    text = desc.lower()
    # 更精確的關鍵字匹配
    if any(k in text for k in ["bfs", "breadth", "廣度", "層序", "樹"]):
        return "bfs"
    if any(k in text for k in ["dfs", "depth", "深度"]):
        return "dfs"
    if any(k in text for k in ["dijkstra", "最短路徑", "shortest path"]):
        return "dijkstra"
    if any(k in text for k in ["sort", "排序", "merge", "歸併"]):
        return "merge_sort"
    if any(k in text for k in ["sql", "資料庫", "database", "select", "query"]):
        return "sql_select"
    
    logger.info(f"未能分類描述: {desc[:50]}...")
    return None

# -----------------------------
# GPT 生成 JSON（改進版 - 使用正確的 API）
# -----------------------------
def generate_with_gpt(template, user_desc, language):
    """使用 GPT 生成代碼和分析"""
    if not client:
        logger.error("OpenAI 客戶端未初始化")
        return {
            "code": "# Error: OpenAI API 未設定",
            "complexity": {"time": "N/A", "space": "N/A"},
            "explanation": "⚠️ OpenAI API 未正確設定，請檢查環境變數。"
        }
    
    prompt = f"""
你是一位資工系程式助教。

⚠️ 請務必輸出「完整 JSON」，格式如下：

{{
  "code": "<整份補齊後的程式碼>",
  "complexity": {{
    "time": "<時間複雜度 Big-O>",
    "space": "<空間複雜度 Big-O>"
  }},
  "explanation": "<簡要解釋（不超過 5 句）>"
}}

不要使用 ```json、``` 或任何 markdown 標記。

以下為模板，必須保留結構：
{template}

使用者需求：
{user_desc}

語言：{language}
"""
    
    try:
        # 使用正確的 OpenAI API
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一位專業的程式教學助教，擅長生成高品質程式碼。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        raw = response.choices[0].message.content.strip()
        # 清理可能的 markdown 標記
        raw = raw.replace("```json", "").replace("```", "").strip()
        
        logger.info(f"GPT 回應長度: {len(raw)} 字元")
        
        try:
            data = json.loads(raw)
            return data
        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失敗: {e}")
            return {
                "code": raw,
                "complexity": {"time": "N/A", "space": "N/A"},
                "explanation": "⚠️ JSON 解析失敗，已顯示原始輸出。"
            }
    
    except Exception as e:
        logger.error(f"GPT 生成失敗: {e}")
        return {
            "code": f"# Error: {str(e)}",
            "complexity": {"time": "N/A", "space": "N/A"},
            "explanation": f"⚠️ 生成失敗: {str(e)}"
        }

# -----------------------------
# GPT 模擬測試輸出（改進版）
# -----------------------------
def simulate_output_with_gpt(code, language, test_input):
    """使用 GPT 模擬程式執行"""
    if not test_input.strip():
        return "未提供測試輸入"
    
    if not client:
        logger.error("OpenAI 客戶端未初始化")
        return "⚠️ OpenAI API 未設定，無法模擬執行"
    
    prompt = f"""
你是一個程式助教，請幫我模擬程式執行結果。

程式語言：{language}
程式碼：
{code}

測試輸入：
{test_input}

請只輸出模擬程式輸出，不要加解釋。
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "你是一個程式執行模擬器。"},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.3
        )
        
        result = response.choices[0].message.content.strip()
        logger.info(f"GPT 模擬執行完成，輸出長度: {len(result)}")
        return result
        
    except Exception as e:
        logger.error(f"GPT 模擬執行失敗: {e}")
        return f"⚠️ 模擬執行失敗: {str(e)}"

# -----------------------------
# 語法檢查（保留提示）
# -----------------------------
def lint_code(language, code):
    return "✔ 語法檢查功能保留（可按需求擴充）"

# -----------------------------
# JDoodle 配額檢查（改進版）
# -----------------------------
QUOTA_FILE = os.path.join("code", "jdoodle_quota.json")

def check_quota():
    """檢查並更新 JDoodle API 配額"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        if os.path.exists(QUOTA_FILE):
            with open(QUOTA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        else:
            data = {}
        
        used = data.get(today, 0)
        
        if used >= DAILY_LIMIT:
            logger.warning(f"JDoodle 配額已用盡: {used}/{DAILY_LIMIT}")
            return False
        else:
            data[today] = used + 1
            os.makedirs(os.path.dirname(QUOTA_FILE), exist_ok=True)
            with open(QUOTA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"JDoodle 配額使用: {used + 1}/{DAILY_LIMIT}")
            return True
            
    except Exception as e:
        logger.error(f"配額檢查失敗: {e}")
        return True  # 失敗時允許執行

def run_jdoodle_code(code, language, test_input=""):
    """使用 JDoodle API 執行代碼"""
    if not JDOODLE_CLIENT_ID or not JDOODLE_CLIENT_SECRET:
        logger.warning("JDoodle API 憑證未設定")
        return "⚠️ JDoodle API 憑證未設定"
    
    if not check_quota():
        return "⚠️ 已達今日免費上限"
    
    lang_map = {
        "Python": "python3",
        "JavaScript": "nodejs",
        "Java": "java",
        "C": "c",
        "C++": "cpp"
    }
    
    script = {
        "clientId": JDOODLE_CLIENT_ID,
        "clientSecret": JDOODLE_CLIENT_SECRET,
        "script": code,
        "language": lang_map.get(language, "python3"),
        "versionIndex": "0",
        "stdin": test_input
    }
    
    url = "https://api.jdoodle.com/v1/execute"
    
    try:
        logger.info(f"正在執行 JDoodle API: {language}")
        response = requests.post(url, json=script, timeout=15)
        result = response.json()
        
        output = result.get("output", "")
        if not output:
            error_msg = result.get("error", "⚠️ JDoodle API 回傳錯誤")
            logger.error(f"JDoodle 執行錯誤: {error_msg}")
            return error_msg
            
        logger.info(f"JDoodle 執行成功，輸出長度: {len(output)}")
        return output
        
    except requests.Timeout:
        logger.error("JDoodle API 執行超時")
        return "⚠️ JDoodle API 執行超時"
    except Exception as e:
        logger.error(f"JDoodle API 連線錯誤: {e}")
        return f"⚠️ 無法連線到 JDoodle：{str(e)}"

# -----------------------------
# Flask 主頁（改進版 - 增強錯誤處理）
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = optimization_advice = complexity_text = lint_result = simulated_output = jdoodle_output = language = None
    quota_exceeded = False
    error_message = None

    if request.method == "POST":
        try:
            # 輸入驗證
            description = request.form.get("description", "").strip()
            language = request.form.get("language", "Python")
            test_input = request.form.get("test_input", "")
            
            if not description:
                error_message = "請提供需求描述"
                logger.warning("空的需求描述")
                return render_template(
                    "index.html",
                    error_message=error_message,
                    language=language
                )
            
            # 長度限制
            if len(description) > 1000:
                error_message = "需求描述過長（最多 1000 字元）"
                logger.warning(f"需求描述過長: {len(description)} 字元")
                return render_template(
                    "index.html",
                    error_message=error_message,
                    language=language
                )

            logger.info(f"處理請求 - 語言: {language}, 描述長度: {len(description)}")

            # 分類並獲取模板
            category = classify(description)
            template = TEMPLATES.get(category, "")
            
            # 使用 GPT 生成代碼
            ai_json = generate_with_gpt(template, description, language)

            result = ai_json.get("code", "")
            explain = ai_json.get("explanation", "")
            time_c = ai_json.get("complexity", {}).get("time", "N/A")
            space_c = ai_json.get("complexity", {}).get("space", "N/A")
            complexity_text = f"時間複雜度：{time_c}\n空間複雜度：{space_c}"
            optimization_advice = textwrap.dedent(explain).strip()

            # 語法檢查
            lint_result = lint_code(language, result)
            
            # 配額檢查
            quota_exceeded = not check_quota()

            # GPT 模擬執行
            if test_input.strip():
                simulated_output = simulate_output_with_gpt(result, language, test_input)
                # JDoodle 真正執行
                jdoodle_output = run_jdoodle_code(result, language, test_input)
            else:
                simulated_output = "未提供測試輸入"
                jdoodle_output = "未提供測試輸入"
                
            logger.info("請求處理成功")

        except Exception as e:
            logger.error(f"請求處理失敗: {e}", exc_info=True)
            error_message = f"處理失敗：{str(e)}"

    return render_template(
        "index.html",
        result=result,
        optimization_advice=optimization_advice,
        complexity=complexity_text,
        lint=lint_result,
        simulated_output=simulated_output,
        jdoodle_output=jdoodle_output,
        language=language,
        quota_exceeded=quota_exceeded,
        error_message=error_message
    )

if __name__ == "__main__":
    logger.info(f"啟動應用程式 (Debug={DEBUG})")
    app.run(debug=DEBUG, host="0.0.0.0", port=5000)
