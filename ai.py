import os
import json
from datetime import datetime
from flask import Flask, render_template, request
from dotenv import load_dotenv
from openai import OpenAI
import requests
import textwrap

# -----------------------------
# 讀取環境變數
# -----------------------------
load_dotenv()
OPENAI_API_KEY = os.getenv("OPEN_API_KEY")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# JDoodle API 相關
JDOODLE_CLIENT_ID = os.getenv("JDOODLE_CLIENT_ID")
JDOODLE_CLIENT_SECRET = os.getenv("JDOODLE_CLIENT_SECRET")
DAILY_LIMIT = 200

client = OpenAI(api_key=OPENAI_API_KEY)
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
# 課程分類器
# -----------------------------
def classify(desc):
    text = desc.lower()
    if any(k in text for k in ["bfs", "breadth", "graph", "樹", "圖"]):
        return "bfs"
    if any(k in text for k in ["dfs", "depth"]):
        return "dfs"
    if any(k in text for k in ["dijkstra", "最短路徑"]):
        return "dijkstra"
    if "sort" in text or "排序" in text:
        return "merge_sort"
    if "sql" in text or "資料庫" in text:
        return "sql_select"
    return None

# -----------------------------
# GPT 生成 JSON
# -----------------------------
def generate_with_gpt(template, user_desc, language):
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
    response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        max_output_tokens=2000
    )
    raw = response.output_text.strip().replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(raw)
        return data
    except:
        return {
            "code": raw,
            "complexity": {"time": "N/A", "space": "N/A"},
            "explanation": "⚠️ JSON 解析失敗，已顯示原始輸出。"
        }

# -----------------------------
# GPT 程式碼補全
# -----------------------------
def complete_code_with_gpt(partial_code, language, user_desc=""):
    prompt = f"""
你是一位資工系程式助教。

使用者提供了部分程式碼，請幫助補全成完整可執行的程式碼。

⚠️ 請務必輸出「完整 JSON」，格式如下：

{{
  "code": "<補全後的完整程式碼>",
  "complexity": {{
    "time": "<時間複雜度 Big-O>",
    "space": "<空間複雜度 Big-O>"
  }},
  "explanation": "<簡要解釋補全的內容和邏輯（不超過 5 句）>"
}}

不要使用 ```json、``` 或任何 markdown 標記。

程式語言：{language}

部分程式碼：
{partial_code}

{"額外需求：" + user_desc if user_desc else ""}
"""
    response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        max_output_tokens=2000
    )
    raw = response.output_text.strip().replace("```json", "").replace("```", "").strip()
    try:
        data = json.loads(raw)
        return data
    except:
        return {
            "code": raw,
            "complexity": {"time": "N/A", "space": "N/A"},
            "explanation": "⚠️ JSON 解析失敗，已顯示原始輸出。"
        }

# -----------------------------
# GPT 模擬測試輸出
# -----------------------------
def simulate_output_with_gpt(code, language, test_input):
    if not test_input.strip():
        return ""
    prompt = f"""
你是一個程式助教，請幫我模擬程式執行結果。

程式語言：{language}
程式碼：
{code}

測試輸入：
{test_input}

請只輸出模擬程式輸出，不要加解釋。
"""
    response = client.responses.create(
        model="gpt-4.1",
        input=prompt,
        max_output_tokens=500
    )
    return response.output_text.strip()

# -----------------------------
# 語法檢查（保留提示）
# -----------------------------
def lint_code(language, code):
    return "✔ 語法檢查功能保留（可按需求擴充）"

# -----------------------------
# JDoodle 配額檢查
# -----------------------------
QUOTA_FILE = os.path.join("code", "jdoodle_quota.json")

def check_quota():
    today = datetime.now().strftime("%Y-%m-%d")
    if os.path.exists(QUOTA_FILE):
        with open(QUOTA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {}
    used = data.get(today, 0)
    if used >= DAILY_LIMIT:
        return False
    else:
        data[today] = used + 1
        os.makedirs(os.path.dirname(QUOTA_FILE), exist_ok=True)
        with open(QUOTA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        return True

def run_jdoodle_code(code, language, test_input=""):
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
        response = requests.post(url, json=script, timeout=10)
        result = response.json()
        return result.get("output", "⚠️ JDoodle API 回傳錯誤/已達每日上限")
    except requests.Timeout:
        return "⚠️ JDoodle API 執行超時"
    except Exception as e:
        return f"⚠️ 無法連線到 JDoodle：{e}"

# -----------------------------
# Flask 主頁
# -----------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = optimization_advice = complexity_text = lint_result = simulated_output = jdoodle_output = language = None
    quota_exceeded = False
    mode = "description"  # 預設模式

    if request.method == "POST":
        mode = request.form.get("mode", "description")
        language = request.form.get("language")
        test_input = request.form.get("test_input", "")
        ai_json = None

        if mode == "completion":
            # 程式碼補全模式
            partial_code = request.form.get("partial_code", "")
            description = request.form.get("description", "")
            
            # 驗證部分程式碼不為空
            if not partial_code.strip():
                result = "⚠️ 錯誤：請提供部分程式碼"
                optimization_advice = "程式碼補全模式需要輸入部分程式碼"
                complexity_text = ""
                lint_result = ""
            else:
                ai_json = complete_code_with_gpt(partial_code, language, description)
        else:
            # 描述生成模式（原有功能）
            description = request.form.get("description")
            category = classify(description)
            template = TEMPLATES.get(category, "")
            ai_json = generate_with_gpt(template, description, language)

        # 只有在成功獲得 ai_json 時才處理結果
        if ai_json:
            result = ai_json.get("code", "")
            explain = ai_json.get("explanation", "")
            time_c = ai_json.get("complexity", {}).get("time", "")
            space_c = ai_json.get("complexity", {}).get("space", "")
            complexity_text = f"時間：{time_c}\n空間：{space_c}"
            optimization_advice = textwrap.dedent(explain).strip()

            lint_result = lint_code(language, result)
            quota_exceeded = not check_quota()

            # GPT 模擬執行 → online_result
            simulated_output = simulate_output_with_gpt(result, language, test_input)

            # JDoodle 真正執行 → test_output
            if test_input.strip():
                jdoodle_output = run_jdoodle_code(result, language, test_input)

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
        mode=mode
    )

if __name__ == "__main__":
    app.run(debug=DEBUG)
