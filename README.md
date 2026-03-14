# Altryx — Open-Source Alteryx Alternative

A visual, drag-and-drop data pipeline platform inspired by Alteryx. Build ETL workflows by connecting nodes on a canvas, configure each tool, and execute the entire pipeline with one click.

**Stack:** Next.js 16 + React Flow (frontend) | Python FastAPI + pandas (backend) | SQLite (metadata)

---

## Features

- **Visual Workflow Designer** — Drag-and-drop canvas with React Flow, auto-snapping edges, minimap
- **21 Data Tools** across 4 categories (see below)
- **DAG Execution Engine** — Topological sort, cycle detection, per-node error isolation
- **Data Preview** — Click any node to see its output in a data grid with column profiling (nulls, uniques, min/max/mean)
- **SQL Database Support** — Connect to PostgreSQL, MySQL, SQL Server directly from the Input Data tool
- **File Uploads** — CSV, Excel (.xlsx), JSON
- **Undo/Redo** — 50-entry history stack (Ctrl+Z / Ctrl+Shift+Z)
- **Copy/Paste Nodes** — Ctrl+C / Ctrl+V
- **Keyboard Shortcuts** — Delete nodes, Ctrl+Enter to run
- **Dark Mode** — Toggle in toolbar, persisted to localStorage
- **Docker Compose** — One command to run the full stack
- **20 Backend Tests** — Covers all core tools and the execution engine

---

## Tool Palette (21 Tools)

| Category | Tools |
|---|---|
| **IO** | Input Data (CSV/Excel/JSON/SQL), Output Data |
| **Preparation** | Filter, Select, Formula, Sort, Sample, Unique, Summarize, Data Cleanse, Multi-Row Formula, Imputation, Transpose, Cross Tab, Find Replace |
| **Parse** | Text to Columns, Regex |
| **Join** | Join (inner/left/right/outer), Union, Append Fields, Fuzzy Match |

---

## Quick Start

### Prerequisites

- **Node.js 20+** and **npm**
- **Python 3.11+**

### Local Development

```bash
# 1. Clone the repo
git clone https://github.com/abhijitsahoo99/altryx-clone.git
cd altryx-clone

# 2. Start the backend
cd backend
python3 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pip install rapidfuzz           # For fuzzy matching
uvicorn altryx.main:app --reload --port 8000

# 3. Start the frontend (new terminal)
cd altryx-clone
npm install
npm run dev
```

Open **http://localhost:3000**

### Docker Compose

```bash
docker compose up --build
```

Open **http://localhost:3000** — both frontend and backend are running.

---

## Usage (End-to-End)

1. **Open the app** — http://localhost:3000 shows the Workflows list
2. **Create a workflow** — Click "New Workflow"
3. **Upload data** — Use the file upload in the sidebar (CSV, Excel, or JSON)
4. **Build the pipeline** — Drag tools from the left palette onto the canvas
5. **Connect nodes** — Drag from the right handle of one node to the left handle of the next
6. **Configure** — Click a node to open its config panel on the right (set filters, formulas, join keys, etc.)
7. **Run** — Click the green **Run** button (or Ctrl+Enter). The engine executes the full DAG.
8. **Preview results** — Click any node to see its output data. Toggle to **Profile** view for column-level stats.
9. **Save** — Click Save to persist the workflow

### Example Pipeline

```
Upload sales.csv → Input Data → Filter (amount > 100) → Formula (tax = amount * 0.08) → Sort (desc) → Output Data
```

### SQL Source Example

1. Drag "Input Data" onto the canvas
2. In the config panel, switch Source Type to **SQL**
3. Enter a connection string: `postgresql://user:pass@localhost:5432/mydb`
4. Enter a query or table name
5. Connect to downstream tools and run

---

## Project Structure

```
altryx-clone/
├── src/                          # Next.js frontend
│   ├── app/                      # Pages (/, /workflows, /workflows/[id])
│   ├── components/
│   │   ├── canvas/               # WorkflowCanvas, ToolNode, NodeConfigPanel
│   │   ├── toolbar/              # ToolPalette
│   │   ├── workflow/             # WorkflowHeader
│   │   └── preview/              # DataPreview (table + profiling)
│   ├── hooks/                    # useWorkflow, useExecution, useKeyboardShortcuts, useDarkMode
│   └── lib/                      # api.ts, toolRegistry.ts, types.ts
├── backend/
│   ├── altryx/
│   │   ├── tools/                # 21 tool implementations
│   │   ├── engine/               # DAG runner, tool registry
│   │   ├── connectors/           # SQL connector
│   │   ├── routers/              # FastAPI routes (workflows, executions, files, connectors)
│   │   ├── main.py               # FastAPI app
│   │   └── schemas.py            # Pydantic models
│   └── tests/                    # 20 pytest tests
├── docker-compose.yml
├── Dockerfile                    # Frontend
└── backend/Dockerfile            # Backend
```

---

## Running Tests

```bash
cd backend
source .venv/bin/activate
pytest tests/ -v
```

All 20 tests cover: Filter, Select, Formula, Sort, Sample, Unique, Summarize, Join, Union, Data Cleanse, Transpose, Regex, plus engine integration tests (pipeline execution, cycle detection, error handling).

---

## Keyboard Shortcuts

| Shortcut | Action |
|---|---|
| `Ctrl+Z` | Undo |
| `Ctrl+Shift+Z` / `Ctrl+Y` | Redo |
| `Ctrl+C` | Copy selected node |
| `Ctrl+V` | Paste |
| `Delete` / `Backspace` | Delete selected node |
| `Ctrl+Enter` | Run workflow |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Health check |
| GET | `/api/tools` | List all registered tools |
| POST | `/api/workflows` | Create workflow |
| GET | `/api/workflows` | List workflows |
| GET | `/api/workflows/:id` | Get workflow |
| PUT | `/api/workflows/:id` | Update workflow |
| DELETE | `/api/workflows/:id` | Delete workflow |
| POST | `/api/workflows/:id/execute` | Execute workflow |
| POST | `/api/files/upload` | Upload data file |
| GET | `/api/files` | List uploaded files |
| POST | `/api/connectors/test` | Test SQL connection |
| POST | `/api/connectors/tables` | List tables |
| POST | `/api/connectors/columns` | List columns |
| POST | `/api/connectors/preview` | Preview table data |

---

## License

MIT
