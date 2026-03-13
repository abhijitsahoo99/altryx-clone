import pandas as pd
import pytest

import altryx.tools  # noqa: F401
from altryx.config import UPLOAD_DIR
from altryx.engine.runner import run_workflow
from altryx.schemas import WorkflowDefinition


@pytest.fixture(autouse=True)
def setup_test_file():
    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie"],
        "age": [25, 35, 30],
        "salary": [50000, 80000, 60000],
    })
    df.to_csv(UPLOAD_DIR / "test_engine_data.csv", index=False)
    yield
    (UPLOAD_DIR / "test_engine_data.csv").unlink(missing_ok=True)


def test_simple_pipeline():
    definition = WorkflowDefinition(
        nodes=[
            {"id": "n1", "type": "input_data", "position": {"x": 0, "y": 0},
             "config": {"source_type": "file", "filename": "test_engine_data.csv", "file_format": "csv"}},
            {"id": "n2", "type": "filter", "position": {"x": 200, "y": 0},
             "config": {"expression": "age > 28"}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2", "sourceHandle": "output", "targetHandle": "input"},
        ],
    )
    results = run_workflow(definition)
    assert len(results) == 2
    assert results[0].status == "completed"
    assert results[0].row_count == 3
    assert results[1].status == "completed"
    assert results[1].row_count == 2  # Bob and Charlie


def test_multi_step_pipeline():
    definition = WorkflowDefinition(
        nodes=[
            {"id": "n1", "type": "input_data", "position": {"x": 0, "y": 0},
             "config": {"source_type": "file", "filename": "test_engine_data.csv", "file_format": "csv"}},
            {"id": "n2", "type": "formula", "position": {"x": 200, "y": 0},
             "config": {"output_column": "bonus", "expression": "salary * 0.1"}},
            {"id": "n3", "type": "sort", "position": {"x": 400, "y": 0},
             "config": {"columns": ["salary"], "ascending": False}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2", "sourceHandle": "output", "targetHandle": "input"},
            {"id": "e2", "source": "n2", "target": "n3", "sourceHandle": "output", "targetHandle": "input"},
        ],
    )
    results = run_workflow(definition)
    assert len(results) == 3
    assert all(r.status == "completed" for r in results)
    # After sort descending by salary, first row should be Bob (80000)
    assert results[2].preview[0]["name"] == "Bob"
    assert results[2].preview[0]["bonus"] == 8000.0


def test_cycle_detection():
    definition = WorkflowDefinition(
        nodes=[
            {"id": "n1", "type": "filter", "position": {"x": 0, "y": 0}, "config": {}},
            {"id": "n2", "type": "filter", "position": {"x": 200, "y": 0}, "config": {}},
        ],
        edges=[
            {"id": "e1", "source": "n1", "target": "n2", "sourceHandle": "output", "targetHandle": "input"},
            {"id": "e2", "source": "n2", "target": "n1", "sourceHandle": "output", "targetHandle": "input"},
        ],
    )
    with pytest.raises(ValueError, match="cycle"):
        run_workflow(definition)


def test_error_handling():
    definition = WorkflowDefinition(
        nodes=[
            {"id": "n1", "type": "input_data", "position": {"x": 0, "y": 0},
             "config": {"source_type": "file", "filename": "nonexistent.csv", "file_format": "csv"}},
        ],
        edges=[],
    )
    results = run_workflow(definition)
    assert results[0].status == "error"
    assert "not found" in results[0].error.lower()
