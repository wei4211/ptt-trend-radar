# 📡 PTT Trend Radar

> PTT 熱門話題與情緒分析平台 — 自動爬取 PTT 文章，進行 NLP 分析、BERTopic 主題建模，並以 Gemini AI 生成摘要，透過 React Dashboard 視覺化呈現。

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green?logo=fastapi)
![React](https://img.shields.io/badge/React-18-61dafb?logo=react)
![TypeScript](https://img.shields.io/badge/TypeScript-5-blue?logo=typescript)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-336791?logo=postgresql)

---

## 功能特色

| 功能 | 技術 | 說明 |
|------|------|------|
| PTT 爬蟲 | `httpx` + `BeautifulSoup` | 支援八卦、Stock、NBA、Tech_Job，自動排程 |
| 關鍵字分析 | `sklearn TF-IDF` + `jieba` | 過濾停用詞，萃取最具代表性詞彙 |
| 情緒分析 | `SnowNLP` | 正面 / 中性 / 負面分類，含每日趨勢圖 |
| 文字雲 | `wordcloud` | 依詞頻生成，支援中文字型 |
| 主題建模 | `BERTopic` + `sentence-transformers` | 自動發現熱門主題，無需預先定義 |
| AI 摘要 | `Gemini 2.5 Flash` | 每個主題自動生成 100-200 字繁中摘要 |
| Dashboard | `React` + `Recharts` | 圓餅圖、折線圖、長條圖、主題 Explorer |

---

## 系統截圖

### 總覽 Dashboard
- 文章數、平均情緒、情緒分布圓餅圖、14 天情緒趨勢折線圖、Top 15 關鍵字長條圖

### 主題分析（BERTopic）
- 自動發現主題、每個主題的情緒比例色條、熱度趨勢 Area Chart、代表文章列表、Gemini AI 摘要

---

## 技術架構

```
PTT文章 → 爬蟲(httpx) → PostgreSQL
                              ↓
                    NLP Pipeline
                    ├── jieba 斷詞
                    ├── sklearn TF-IDF 關鍵字
                    ├── SnowNLP 情緒分析
                    └── BERTopic 主題建模
                              ↓
                    FastAPI REST API
                              ↓
                    React Dashboard
                              ↓
                    Gemini 2.5 Flash AI 摘要
```

---

## 快速開始

### 方式一：Docker（推薦）

```bash
git clone https://github.com/your-username/ptt-trend-radar.git
cd ptt-trend-radar

cp .env.example .env
# 編輯 .env 填入 GEMINI_API_KEY

docker compose up --build
```

開啟 http://localhost:3000

### 方式二：本地開發

**前置需求：** Python 3.11+、Node 20+、PostgreSQL 15+

```bash
# 1. 啟動 PostgreSQL（或用 Docker）
docker compose -f docker-compose.dev.yml up -d

# 2. 安裝 Backend
cd backend
pip install -r requirements.txt
cp ../.env.example ../.env   # 填入 GEMINI_API_KEY

# 3. 啟動 Backend
DATABASE_URL="postgresql+asyncpg://ptt:pttpassword@localhost:5432/ptt_radar" \
GEMINI_API_KEY="your-key-here" \
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

# 4. 安裝 & 啟動 Frontend
cd ../frontend
npm install
npm run dev
```

**或用一鍵啟動腳本（本地開發）：**
```bash
bash start.sh
```

---

## 環境變數

複製 `.env.example` 並填入：

```env
GEMINI_API_KEY=your-gemini-api-key   # Google AI Studio 取得
DATABASE_URL=postgresql+asyncpg://ptt:pttpassword@localhost:5432/ptt_radar
SCRAPE_INTERVAL_MINUTES=60
```

> Gemini API Key 申請：https://aistudio.google.com/apikey

---

## API 文件

啟動後開啟 http://localhost:8001/docs（Swagger UI）

| Endpoint | 說明 |
|----------|------|
| `POST /api/scraper/trigger/sync` | 立即爬取（同步） |
| `GET /api/analysis/overview` | 文章數、情緒概覽 |
| `GET /api/analysis/keywords` | TF-IDF 關鍵字 |
| `GET /api/analysis/sentiment` | 情緒分布 |
| `GET /api/analysis/sentiment/trend` | 每日情緒趨勢 |
| `GET /api/analysis/wordcloud` | 文字雲（base64 PNG）|
| `POST /api/topics/compute/sync` | 執行 BERTopic 主題分析 |
| `GET /api/topics/` | 取得主題列表 |
| `GET /api/topics/{id}/trend` | 主題熱度趨勢 |
| `POST /api/topics/{id}/summary` | Gemini AI 生成摘要 |

---

## 專案結構

```
ptt-trend-radar/
├── backend/
│   ├── app/
│   │   ├── api/routes/        # FastAPI 路由
│   │   ├── core/              # 設定、排程器
│   │   ├── db/                # SQLAlchemy async
│   │   ├── models/            # ORM models
│   │   ├── nlp/               # NLP 模組
│   │   │   ├── keyword_extractor.py   # sklearn TF-IDF
│   │   │   ├── sentiment_analyzer.py  # SnowNLP
│   │   │   ├── topic_modeler.py       # BERTopic
│   │   │   └── wordcloud_generator.py
│   │   ├── scraper/           # PTT 爬蟲
│   │   └── services/          # 業務邏輯
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/             # Dashboard, Topics, Keywords...
│       ├── components/        # Charts, Cards, UI
│       └── hooks/             # useAnalysis, useTopics
├── docker-compose.yml
├── start.sh                   # 一鍵本地啟動
└── .env.example
```

---

## 開發路線圖

- [x] **MVP**：爬蟲、關鍵字、情緒分析、文字雲、Dashboard
- [x] **V2**：BERTopic 主題建模、Gemini AI 摘要、主題趨勢
- [ ] **V3**：RAG 問答、主題熱度預測、即時 WebSocket 更新

---

## License

MIT
