from altryx.tools.input_data import InputDataTool
from altryx.tools.filter import FilterTool
from altryx.tools.output_data import OutputDataTool
from altryx.tools.select import SelectTool
from altryx.tools.formula import FormulaTool
from altryx.tools.sort import SortTool
from altryx.tools.sample import SampleTool
from altryx.tools.unique import UniqueTool
from altryx.tools.summarize import SummarizeTool
from altryx.tools.data_cleanse import DataCleanseTool
from altryx.tools.join import JoinTool
from altryx.tools.union import UnionTool
from altryx.engine.registry import register_tool

_all_tools = [
    InputDataTool(),
    FilterTool(),
    OutputDataTool(),
    SelectTool(),
    FormulaTool(),
    SortTool(),
    SampleTool(),
    UniqueTool(),
    SummarizeTool(),
    DataCleanseTool(),
    JoinTool(),
    UnionTool(),
]

for t in _all_tools:
    register_tool(t)
