<div align="center">

# 📡 PTT Trend Radar

**PTT 熱門話題與情緒分析平台**

自動爬取 PTT 文章 → NLP 分析 → BERTopic 主題建模 → Gemini AI 摘要 → React Dashboard 視覺化

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5-3178C6?style=for-the-badge&logo=typescript&logoColor=white)](https://typescriptlang.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)

</div>

---

## 📸 Screenshots

### 總覽 Dashboard
![Dashboard](assets/總攬.png)

### 主題分析（BERTopic + Gemini AI）
![Topics](assets/主題分析.png)

### 關鍵字分析
![Keywords](assets/關鍵字分析.png)

### 情緒分析
![Sentiment](assets/情緒分析.png)

### 文字雲
![WordCloud](assets/文字雲.png)

### 文章列表
![Articles](assets/文章列表.png)

---

## ✨ 功能特色

| 功能 | 技術 | 說明 |
|------|------|------|
| 🕷️ **PTT 爬蟲** | `httpx` + `BeautifulSoup` | 支援 4 個看板，APScheduler 定時自動爬取 |
| 🔑 **關鍵字分析** | `sklearn TF-IDF` + `jieba` | 中文斷詞、停用詞過濾、以內容為主的 TF-IDF |
| 💬 **情緒分析** | `SnowNLP` | 正 / 中 / 負分類，含每日趨勢折線圖 |
| ☁️ **文字雲** | `wordcloud` | 詞頻驅動，支援中文字型，base64 回傳 |
| 🧠 **主題建模** | `BERTopic` + `sentence-transformers` | 多語言 embedding，HDBSCAN 聚類，自動命名主題 |
| ✨ **AI 摘要** | `Gemini 2.5 Flash` | 每個主題生成 100-200 字繁體中文分析摘要 |
| 📊 **Dashboard** | `React` + `Recharts` + `TailwindCSS` | 暗色主題，圓餅圖 / 折線圖 / 長條圖 / Area Chart |

---

## 🏗️ 系統架構

```mermaid
graph TB
    subgraph Scraper["🕷️ 資料蒐集"]
        PTT["PTT 公開網頁"] -->|httpx + BeautifulSoup| SC[爬蟲模組]
        SC -->|定時排程| AP[APScheduler]
    end

    subgraph DB["🗄️ 資料層"]
        SC --> PG[(PostgreSQL)]
        PG --> ART[articles]
        PG --> TOP[topics]
    end

    subgraph NLP["🧠 NLP Pipeline"]
        PG --> JB[jieba 斷詞]
        JB --> TF[sklearn TF-IDF\n關鍵字分析]
        JB --> SN[SnowNLP\n情緒分析]
        JB --> WC[wordcloud\n文字雲]
        PG --> BT[BERTopic\n主題建模]
        BT --> ST[sentence-transformers\n多語言 Embedding]
    end

    subgraph API["⚡ FastAPI"]
        TF & SN & WC & BT --> API_SRV[REST API :8001]
        API_SRV --> GM[Gemini 2.5 Flash\nAI 摘要]
    end

    subgraph Frontend["🌐 React Frontend :3000"]
        API_SRV --> DB_PAGE[總覽 Dashboard]
        API_SRV --> KW_PAGE[關鍵字分析]
        API_SRV --> SENT_PAGE[情緒分析]
        API_SRV --> WC_PAGE[文字雲]
        API_SRV --> TP_PAGE[主題 Explorer]
        API_SRV --> ART_PAGE[文章列表]
    end
```

---

## 🚀 快速開始

### 方式一：Docker（推薦，一行啟動）

```bash
git clone https://github.com/wei4211/ptt-trend-radar.git
cd ptt-trend-radar

cp .env.example .env
# 編輯 .env，填入 GEMINI_API_KEY

docker compose up --build
```

啟動完成後開啟瀏覽器：

> 🌐 **http://localhost:3000** ← 主要 Dashboard（從這裡使用）
>
> 📖 http://localhost:8001/docs ← API 文件（Swagger UI）

### 方式二：本地開發腳本

```bash
git clone https://github.com/wei4211/ptt-trend-radar.git
cd ptt-trend-radar

cp .env.example .env  # 填入 GEMINI_API_KEY

# 安裝 Python 依賴
pip install -r backend/requirements.txt

# 安裝 Node 依賴
cd frontend && npm install && cd ..

# 一鍵啟動（DB + Backend + Frontend）
bash start.sh
```

啟動完成後開啟瀏覽器：

> 🌐 **http://localhost:3000** ← 主要 Dashboard（從這裡使用）
>
> 📖 http://localhost:8001/docs ← API 文件（Swagger UI）

#### 首次使用：爬取文章資料

啟動後 Dashboard 會是空的，需要先爬取一次：

```bash
# 爬取所有看板（約 3-5 分鐘）
curl -X POST "http://localhost:8001/api/scraper/trigger/sync"
```

或直接在 Dashboard 點右上角的「**立即爬取**」按鈕。

---

## ⚙️ 環境變數

| 變數 | 說明 | 必填 |
|------|------|------|
| `GEMINI_API_KEY` | Google AI Studio API Key | ✅ |
| `DATABASE_URL` | PostgreSQL 連線字串 | ✅ |
| `SCRAPE_INTERVAL_MINUTES` | 自動爬取間隔（分鐘，預設 60） | ❌ |

> 申請 Gemini API Key：https://aistudio.google.com/apikey

---

## 📡 API 文件

啟動後開啟 http://localhost:8001/docs 查看完整 Swagger 文件

<details>
<summary>查看主要 Endpoints</summary>

| Method | Endpoint | 說明 |
|--------|----------|------|
| `POST` | `/api/scraper/trigger/sync` | 立即爬取所有看板 |
| `GET` | `/api/analysis/overview` | 文章數、平均情緒概覽 |
| `GET` | `/api/analysis/keywords` | TF-IDF 關鍵字排行 |
| `GET` | `/api/analysis/sentiment` | 情緒分布（正/中/負 %） |
| `GET` | `/api/analysis/sentiment/trend` | 每日情緒趨勢 |
| `GET` | `/api/analysis/wordcloud` | 文字雲（base64 PNG） |
| `POST` | `/api/topics/compute/sync` | 執行 BERTopic 主題分析 |
| `GET` | `/api/topics/` | 取得主題列表 |
| `GET` | `/api/topics/{id}/trend` | 主題熱度趨勢 |
| `GET` | `/api/topics/{id}/articles` | 主題代表文章 |
| `POST` | `/api/topics/{id}/summary` | Gemini AI 生成摘要 |
| `GET` | `/api/articles/` | 文章列表（依推文數排序） |

</details>

---

## 📁 專案結構

```
ptt-trend-radar/
├── backend/
│   ├── app/
│   │   ├── api/routes/         # FastAPI 路由
│   │   │   ├── analysis.py     # 關鍵字、情緒、文字雲
│   │   │   ├── articles.py     # 文章列表
│   │   │   ├── scraper.py      # 爬蟲觸發
│   │   │   └── topics.py       # BERTopic 主題
│   │   ├── core/
│   │   │   ├── config.py       # 全域設定
│   │   │   └── scheduler.py    # APScheduler
│   │   ├── db/database.py      # SQLAlchemy async
│   │   ├── models/             # ORM models
│   │   ├── nlp/
│   │   │   ├── keyword_extractor.py   # sklearn TF-IDF
│   │   │   ├── sentiment_analyzer.py  # SnowNLP
│   │   │   ├── topic_modeler.py       # BERTopic
│   │   │   └── wordcloud_generator.py
│   │   ├── scraper/ptt_scraper.py     # PTT 爬蟲
│   │   └── services/           # 業務邏輯 + TTL 快取
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── pages/              # Dashboard, Topics, Keywords...
│       ├── components/
│       │   ├── Charts/         # Recharts 圖表元件
│       │   ├── Cards/          # StatCard
│       │   └── UI/             # BoardSelector, Spinner
│       └── hooks/              # useAnalysis, useTopics
├── assets/                     # README 截圖
├── docker-compose.yml
├── docker-compose.dev.yml      # 僅 DB（本地開發用）
├── start.sh                    # 一鍵本地啟動
└── .env.example
```

---

## 🗺️ 開發路線圖

- [x] **MVP**：PTT 爬蟲、TF-IDF 關鍵字、SnowNLP 情緒分析、文字雲、React Dashboard
- [x] **V2**：BERTopic 主題建模、Gemini AI 摘要、主題熱度趨勢圖
- [ ] **V3**：RAG 問答（LangChain）、主題熱度預測、WebSocket 即時更新

---

## 🛠️ Tech Stack

<div align="center">

**Backend**

![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white)

**NLP / AI**

![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white)
![HuggingFace](https://img.shields.io/badge/HuggingFace-FFD21E?style=flat-square&logo=huggingface&logoColor=black)
![Google Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)

**Frontend**

![React](https://img.shields.io/badge/React-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Recharts](https://img.shields.io/badge/Recharts-22B5BF?style=flat-square)

**DevOps**

![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)

</div>

---

## 📄 License

MIT © 2025
