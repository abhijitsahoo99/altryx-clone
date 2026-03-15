import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from altryx.database import init_db
from altryx.routers import connectors, executions, files, workflows

app = FastAPI(title="Altryx", version="0.1.0")

allowed_origins = os.environ.get(
    "ALLOWED_ORIGINS",
    "http://localhost:3000,https://*.up.railway.app",
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(workflows.router)
app.include_router(executions.router)
app.include_router(files.router)
app.include_router(connectors.router)


@app.on_event("startup")
def on_startup():
    init_db()
    # Register all tools
    import altryx.tools  # noqa: F401


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/tools")
def list_tools():
    from altryx.engine.registry import get_all_tools
    tools = get_all_tools()
    return [
        {
            "type": t.tool_type,
            "label": t.label,
            "category": t.category,
            "inputs": t.inputs,
            "outputs": t.outputs,
            "config_schema": t.get_config_schema(),
        }
        for t in tools.values()
    ]
