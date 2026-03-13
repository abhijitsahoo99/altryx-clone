import pandas as pd
import pytest

import altryx.tools  # noqa: F401 - registers tools
from altryx.engine.registry import get_tool


@pytest.fixture
def sample_df():
    return pd.DataFrame({
        "name": ["Alice", "Bob", "Charlie", "Diana", "Eve"],
        "age": [25, 35, 30, 28, None],
        "city": ["NYC", "LA", "NYC", "SF", "LA"],
        "salary": [50000, 80000, 60000, 70000, 55000],
    })


class TestFilterTool:
    def test_basic_filter(self, sample_df):
        tool = get_tool("filter")
        result = tool.execute({"input": sample_df}, {"expression": "age > 28"})
        assert len(result["output"]) == 2  # Bob (35) and Charlie (30)

    def test_empty_expression(self, sample_df):
        tool = get_tool("filter")
        result = tool.execute({"input": sample_df}, {"expression": ""})
        assert len(result["output"]) == 5


class TestSelectTool:
    def test_select_columns(self, sample_df):
        tool = get_tool("select")
        result = tool.execute({"input": sample_df}, {"columns": ["name", "age"]})
        assert list(result["output"].columns) == ["name", "age"]

    def test_rename_columns(self, sample_df):
        tool = get_tool("select")
        result = tool.execute({"input": sample_df}, {"columns": ["name"], "rename": {"name": "full_name"}})
        assert "full_name" in result["output"].columns


class TestFormulaTool:
    def test_formula(self, sample_df):
        tool = get_tool("formula")
        result = tool.execute({"input": sample_df}, {"output_column": "bonus", "expression": "salary * 0.1"})
        assert "bonus" in result["output"].columns
        assert result["output"]["bonus"].iloc[0] == 5000.0


class TestSortTool:
    def test_sort_ascending(self, sample_df):
        tool = get_tool("sort")
        result = tool.execute({"input": sample_df}, {"columns": ["salary"], "ascending": True})
        assert result["output"]["salary"].iloc[0] == 50000

    def test_sort_descending(self, sample_df):
        tool = get_tool("sort")
        result = tool.execute({"input": sample_df}, {"columns": ["salary"], "ascending": False})
        assert result["output"]["salary"].iloc[0] == 80000


class TestSampleTool:
    def test_first_n(self, sample_df):
        tool = get_tool("sample")
        result = tool.execute({"input": sample_df}, {"method": "first_n", "n": 2})
        assert len(result["output"]) == 2

    def test_random_n(self, sample_df):
        tool = get_tool("sample")
        result = tool.execute({"input": sample_df}, {"method": "random_n", "n": 3})
        assert len(result["output"]) == 3


class TestUniqueTool:
    def test_unique_on_column(self, sample_df):
        tool = get_tool("unique")
        result = tool.execute({"input": sample_df}, {"columns": ["city"]})
        assert len(result["output"]) == 3  # NYC, LA, SF


class TestSummarizeTool:
    def test_group_and_aggregate(self, sample_df):
        tool = get_tool("summarize")
        result = tool.execute({"input": sample_df}, {
            "group_by": ["city"],
            "aggregations": [{"column": "salary", "function": "sum"}],
        })
        assert "city" in result["output"].columns
        assert len(result["output"]) == 3


class TestJoinTool:
    def test_inner_join(self):
        left = pd.DataFrame({"id": [1, 2, 3], "name": ["A", "B", "C"]})
        right = pd.DataFrame({"id": [2, 3, 4], "value": [20, 30, 40]})
        tool = get_tool("join")
        result = tool.execute(
            {"left": left, "right": right},
            {"join_type": "inner", "left_key": "id", "right_key": "id"},
        )
        assert len(result["output"]) == 2  # id 2 and 3


class TestUnionTool:
    def test_union_by_name(self):
        df1 = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
        df2 = pd.DataFrame({"a": [5, 6], "b": [7, 8]})
        tool = get_tool("union")
        result = tool.execute({"input_1": df1, "input_2": df2}, {"mode": "by_name"})
        assert len(result["output"]) == 4


class TestDataCleanseTool:
    def test_trim_and_lowercase(self):
        df = pd.DataFrame({"text": ["  Hello  ", " WORLD ", "  Test  "]})
        tool = get_tool("data_cleanse")
        result = tool.execute({"input": df}, {"trim_whitespace": True, "change_case": "lower"})
        assert result["output"]["text"].iloc[0] == "hello"


class TestTransposeTool:
    def test_transpose(self, sample_df):
        tool = get_tool("transpose")
        result = tool.execute({"input": sample_df[["name", "age"]].head(2)}, {})
        assert len(result["output"]) >= 2  # At least name and age rows


class TestRegexTool:
    def test_extract(self):
        df = pd.DataFrame({"text": ["abc123", "def456", "ghi789"]})
        tool = get_tool("regex")
        result = tool.execute({"input": df}, {
            "column": "text",
            "pattern": r"(\d+)",
            "mode": "extract",
            "output_column": "numbers",
        })
        assert result["output"]["numbers"].iloc[0] == "123"
