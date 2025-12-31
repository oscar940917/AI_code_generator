# AI Code Generator

一個功能強大的 AI 驅動程式碼生成器，支援多種程式語言和演算法模板。

## ✨ 功能特色

- 🤖 **AI 智慧生成**：使用 OpenAI GPT-4 生成高品質程式碼
- 📝 **多語言支援**：支援 Python、JavaScript、Java、C、C++ 等語言
- 🎯 **演算法模板**：內建 BFS、DFS、Dijkstra、Merge Sort 等常用演算法模板
- 📊 **複雜度分析**：自動分析時間和空間複雜度
- 🧪 **程式碼測試**：整合 JDoodle API 進行線上程式碼執行
- 🎨 **現代化 UI**：美觀的漸層設計、動畫效果和響應式佈局
- 🔍 **語法檢查**：提供基本語法檢查功能
- 💡 **優化建議**：AI 提供程式碼優化建議

## 🖼️ 介面預覽

### 首頁
![UI Homepage](https://github.com/user-attachments/assets/c279efc1-b5cc-47f0-8801-3db2a1c7ed05)

### 填寫表單
![UI Form](https://github.com/user-attachments/assets/7bc8f03d-089f-44a3-9bde-e5f65587725e)

## 🚀 快速開始

### 環境需求

- Python 3.8+
- OpenAI API Key
- JDoodle API Key (可選)

### 安裝步驟

1. 克隆專案：
```bash
git clone https://github.com/oscar940917/AI_code_generator.git
cd AI_code_generator
```

2. 安裝依賴：
```bash
pip install -r requirements.txt
```

3. 設定環境變數：
```bash
cp .env.example .env
# 編輯 .env 檔案，填入你的 API Keys
```

4. 啟動應用：
```bash
python ai.py
```

5. 開啟瀏覽器訪問：
```
http://localhost:5000
```

## ⚙️ 環境變數設定

在 `.env` 檔案中設定以下變數：

```env
# OpenAI API 配置（必填）
OPEN_API_KEY=your_openai_api_key_here

# JDoodle API 配置（可選，用於線上執行程式碼）
JDOODLE_CLIENT_ID=your_jdoodle_client_id_here
JDOODLE_CLIENT_SECRET=your_jdoodle_client_secret_here

# 除錯模式
DEBUG=False
```

## 📚 使用說明

1. **輸入需求描述**：描述你想要生成的程式碼功能
2. **選擇程式語言**：從下拉選單選擇目標程式語言
3. **提供測試輸入**（可選）：如需測試程式碼，可輸入測試資料
4. **點擊生成按鈕**：AI 會根據你的需求生成程式碼
5. **查看結果**：
   - 生成的程式碼
   - 複雜度分析
   - 優化建議
   - 測試執行結果

## 🛠️ 技術架構

### 後端
- **Flask**：Web 框架
- **OpenAI API**：AI 程式碼生成
- **JDoodle API**：線上程式碼執行
- **Python-dotenv**：環境變數管理

### 前端
- **HTML5 + CSS3**：響應式設計
- **JavaScript**：互動功能
- **Prism.js**：程式碼語法高亮
- **Font Awesome**：圖示庫

## 🎨 UI 優化項目

- ✅ 漸層背景設計
- ✅ 卡片懸浮效果
- ✅ 載入動畫
- ✅ 表單焦點效果
- ✅ 按鈕動畫
- ✅ 響應式設計
- ✅ 錯誤訊息顯示
- ✅ 程式碼複製功能

## 🔧 後端優化項目

- ✅ 修正 OpenAI API 使用（使用最新的 chat.completions API）
- ✅ 完整錯誤處理機制
- ✅ 輸入驗證和清理
- ✅ 日誌記錄系統
- ✅ 配額管理優化
- ✅ 改進的分類器
- ✅ 更好的異常處理

## 📝 支援的演算法模板

- **BFS (廣度優先搜尋)**
- **DFS (深度優先搜尋)**
- **Dijkstra (最短路徑演算法)**
- **Merge Sort (歸併排序)**
- **SQL SELECT (基本查詢)**

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License

## 👤 作者

oscar940917

## 🙏 致謝

- OpenAI 提供 GPT-4 API
- JDoodle 提供線上程式碼執行服務
- Font Awesome 提供圖示
- Prism.js 提供語法高亮