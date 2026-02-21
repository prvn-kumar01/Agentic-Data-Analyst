<div align="center">

# 🤖 Auto-Analyst AI

### **Your Autonomous Data Analysis Agent**

*Upload a CSV. Ask a question. Get insights, charts, and code — all powered by AI.*

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![React](https://img.shields.io/badge/React-19-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://react.dev)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent_Framework-1C3C3C?style=for-the-badge&logo=langchain&logoColor=white)](https://langchain-ai.github.io/langgraph/)
[![Llama 3.3](https://img.shields.io/badge/Llama_3.3-70B-7950F2?style=for-the-badge&logo=meta&logoColor=white)](https://groq.com)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

**Auto-Analyst AI** is a full-stack, agentic data analysis platform that turns plain English questions into complete data insights — with charts, statistical summaries, and AI-generated narratives — all without writing a single line of code.

<br/>

> 💡 *"Show me the top 10 products by revenue and their trend over time"*
> → The agent profiles your data, plans the analysis, writes Python code, executes it in a sandbox, generates multiple charts, and delivers a polished summary.

</div>

---

## ✨ Key Features

<table>
<tr>
<td width="50%">

### 🧠 Agentic AI Pipeline
- **5-node autonomous workflow** orchestrated by LangGraph
- Self-correcting with up to 3 retry attempts
- Structured output parsing with Pydantic schemas

### ⚡ Blazing Fast Inference
- Powered by **Llama 3.3 70B** via **Groq API**
- Sub-second LLM response times
- Separate models for planning (creative) vs coding (deterministic)

### 🔒 Secure Code Execution
- Sandboxed `exec()` with restricted builtins
- Dangerous patterns blocked (subprocess, shutil, etc.)
- Import stripping — libraries pre-injected

</td>
<td width="50%">

### 📊 Multi-Chart Generation
- Generates **4–5 publication-quality visualizations** per query
- Seaborn + Matplotlib with beautiful color palettes
- Distribution, correlation, comparison, and ranking charts

### 🎨 Modern React Frontend
- **React 19** + **Vite** for instant dev experience
- Drag-and-drop CSV upload with data preview
- Real-time pipeline status tracking
- Interactive chart gallery and code viewer

### 🐳 One-Command Deployment
- Multi-stage Docker build (Node + Python + Nginx)
- `docker-compose up` and you're live
- Production-ready with health checks

</td>
</tr>
</table>

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         AUTO-ANALYST AI                                │
├──────────────────────────────┬──────────────────────────────────────────┤
│        FRONTEND              │              BACKEND                    │
│   React 19 + Vite            │          FastAPI + LangGraph            │
│                              │                                        │
│  ┌────────────────────┐      │   ┌──────────────────────────────────┐  │
│  │  📂 File Upload    │──────┼──▶│  POST /api/upload                │  │
│  └────────────────────┘      │   └──────────────────────────────────┘  │
│  ┌────────────────────┐      │   ┌──────────────────────────────────┐  │
│  │  💬 Query Input    │──────┼──▶│  POST /api/analyze               │  │
│  └────────────────────┘      │   └───────────────┬──────────────────┘  │
│  ┌────────────────────┐      │                   │                    │
│  │  ⚙️ Pipeline Status│      │                   ▼                    │
│  │  📊 Chart Gallery  │◀─────┼───  LangGraph Agent Pipeline          │
│  │  💻 Code Panel     │      │   ┌────────────────────────────────┐   │
│  │  📝 Insight Panel  │      │   │  Profiler → Planner → Generator│   │
│  └────────────────────┘      │   │  → Executor → Insight          │   │
│                              │   └────────────────────────────────┘   │
└──────────────────────────────┴──────────────────────────────────────────┘
```

---

## 🔄 Agent Pipeline — How It Works

The agent operates as a **stateful graph** where each node performs a specialized task:

```mermaid
graph LR
    A["📂 Upload CSV"] --> B["🕵️ Profiler"]
    B -->|"Data loaded"| C["🧠 Planner"]
    B -->|"Error"| Z["🛑 END"]
    C --> D["⌨️ Generator"]
    D --> E["⚙️ Executor"]
    E -->|"Success"| F["📊 Insight"]
    E -->|"Error (retry ≤ 3)"| D
    F --> G["✅ Results"]
```

| Stage | Node | What It Does |
|-------|------|--------------|
| **1** | 🕵️ **Profiler** | Loads the CSV, extracts schema, generates a statistical summary |
| **2** | 🧠 **Planner** | Creates a multi-step analysis plan covering distributions, comparisons, correlations |
| **3** | ⌨️ **Generator** | Writes Python code (Pandas + Matplotlib + Seaborn) to execute the plan |
| **4** | ⚙️ **Executor** | Runs code in a secure sandbox, captures stdout and generated charts |
| **5** | 📊 **Insight** | Summarizes all findings in plain English for non-technical audiences |

> 🔄 **Self-Correcting**: If code execution fails, the agent reflects on the error and regenerates fixed code — up to 3 attempts.

---

## 🛠️ Tech Stack

<div align="center">

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **LLM** | Llama 3.3 70B (via Groq) | Reasoning, planning, code generation |
| **Agent Framework** | LangGraph | Stateful graph orchestration with conditional edges |
| **Backend API** | FastAPI + Uvicorn | REST API for upload, analysis, and chart serving |
| **Frontend** | React 19 + Vite | Modern, responsive single-page application |
| **Data Science** | Pandas, NumPy, Matplotlib, Seaborn | Data manipulation and visualization |
| **Embeddings** | HuggingFace (all-MiniLM-L6-v2) | Semantic similarity (GPU-accelerated) |
| **Structured Output** | Pydantic + LangChain JsonOutputParser | Type-safe LLM responses |
| **Deployment** | Docker + Nginx + Supervisord | Production-ready containerization |

</div>

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+** (for frontend)
- **Groq API Key** — [Get one free at groq.com](https://console.groq.com/keys)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/prvn-kumar01/Agentic-Data-Analyst.git
cd Agentic-Data-Analyst
```

### 2️⃣ Set Up Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### 3️⃣ Install Backend Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows

# Install dependencies
pip install -r requirements.txt
```

### 4️⃣ Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 5️⃣ Run the Application

**Option A — Full-Stack (React + API):**

```bash
# Terminal 1: Start the FastAPI backend
python server.py

# Terminal 2: Start the React frontend
cd frontend
npm run dev
```

Then open **http://localhost:5173** in your browser.

**Option B — CLI Mode (No UI):**

```bash
python main.py
```

---

## 🐳 Docker Deployment

Deploy the entire stack with a single command:

```bash
# Build and run
docker-compose up --build

# Access the app
open http://localhost
```

The Docker setup uses a **multi-stage build**:
1. **Stage 1**: Builds the React frontend with Node.js
2. **Stage 2**: Sets up Python runtime + Nginx reverse proxy + Supervisord process manager

---

## 📁 Project Structure

```
Auto-Analyst-AI/
│
├── 🐍 Backend (Python)
│   ├── server.py              # FastAPI REST API server
│   ├── main.py                # CLI entry point
│   ├── config.py              # LLM & embedding configuration
│   └── src/
│       ├── graph.py           # LangGraph workflow definition
│       ├── nodes.py           # 5 agent nodes (profiler → insight)
│       ├── state.py           # AgentState TypedDict schema
│       ├── schema.py          # Pydantic models for structured output
│       ├── prompts.py         # All LLM prompt templates
│       ├── tools.py           # Sandboxed code execution engine
│       └── utils.py           # CSV profiling utilities
│
├── ⚛️ Frontend (React)
│   └── frontend/
│       ├── src/
│       │   ├── App.jsx        # Main application shell
│       │   ├── index.css      # Global styles
│       │   └── components/
│       │       ├── FileUpload.jsx      # Drag-and-drop CSV upload
│       │       ├── QueryInput.jsx      # Natural language query input
│       │       ├── PipelineStatus.jsx  # Real-time agent progress
│       │       ├── ChartGallery.jsx    # Visualization gallery
│       │       ├── CodePanel.jsx       # Generated code viewer
│       │       └── InsightPanel.jsx    # AI-generated insights
│       └── vite.config.js     # Vite configuration
│
├── 🐳 Deployment
│   ├── Dockerfile             # Multi-stage build
│   ├── docker-compose.yml     # One-command deployment
│   ├── nginx.conf             # Reverse proxy config
│   └── supervisord.conf       # Process manager config
│
├── requirements.txt           # Python dependencies
└── .env                       # API keys (not committed)
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/upload` | Upload a CSV file, returns data preview with column metadata |
| `POST` | `/api/analyze` | Run the full agent pipeline, returns insights + chart URLs + code |
| `GET` | `/api/charts/{filename}` | Serve a generated chart image |
| `GET` | `/api/health` | Health check endpoint |

<details>
<summary><strong>📋 Example: Analyze Endpoint Response</strong></summary>

```json
{
  "success": true,
  "insight": "Based on the analysis, the top 5 products by revenue are...",
  "charts": ["/api/charts/output_1.png", "/api/charts/output_2.png"],
  "code": "df = pd.read_csv('data/input/sales.csv')...",
  "code_output": "Total Revenue: $1,234,567\nTop Product: Widget A",
  "plan": ["Load data", "Group by product", "Calculate revenue", "Plot top 10"],
  "node_log": [
    {"node": "profiler", "status": "completed"},
    {"node": "planner", "status": "completed", "plan": ["..."]},
    {"node": "generator", "status": "completed", "code_length": 1250},
    {"node": "executor", "status": "completed", "output": "..."},
    {"node": "insight", "status": "completed"}
  ]
}
```
</details>

---

## 🧩 How the Agent Thinks

Here's what happens under the hood when you ask *"What are the sales trends by region?"*:

```
1. 🕵️ PROFILER
   → Reads CSV, detects 12 columns, 50,000 rows
   → Identifies: Region (categorical), Sales (numeric), Date (datetime)

2. 🧠 PLANNER
   → Step 1: Load and clean data
   → Step 2: Group by Region, calculate total sales
   → Step 3: Plot time-series trends per region
   → Step 4: Create a heatmap of region × month
   → Step 5: Show top/bottom performing regions

3. ⌨️ GENERATOR
   → Writes ~80 lines of Pandas + Matplotlib code
   → Creates 4 subplots with seaborn styling

4. ⚙️ EXECUTOR
   → Runs code in sandbox → Captures 4 charts + summary stats

5. 📊 INSIGHT
   → "The Western region leads with $2.3M in total sales,
      showing a 15% growth trend. The Southern region
      underperforms with declining Q3 numbers..."
```

---

## 🔒 Security

The code execution engine includes multiple layers of protection:

- ✅ **Restricted Builtins** — Only safe Python builtins are available
- ✅ **Import Stripping** — All import statements are removed; libraries are pre-injected
- ✅ **Pattern Blocking** — `subprocess`, `shutil`, `importlib`, `__import__` are blocked
- ✅ **Isolated Scope** — Code runs in a separate namespace, not the main process
- ✅ **Output Capture** — Stdout is redirected and captured safely

---

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Commit** your changes: `git commit -m 'Add amazing feature'`
4. **Push** to the branch: `git push origin feature/amazing-feature`
5. **Open** a Pull Request

---

## 📜 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

## 🙋‍♂️ Author

<div align="center">

**Praveen Kumar**

[![GitHub](https://img.shields.io/badge/GitHub-prvn--kumar01-181717?style=for-the-badge&logo=github)](https://github.com/prvn-kumar01)

---

*If you found this project useful, please consider giving it a ⭐!*

</div>
