from typing import Any

import pandas as pd

from altryx.tools.base import BaseTool


class FuzzyMatchTool(BaseTool):
    tool_type = "fuzzy_match"
    label = "Fuzzy Match"
    category = "Join"
    inputs = ["left", "right"]
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        left = inputs["left"].copy()
        right = inputs["right"].copy()
        left_key = config.get("left_key", "")
        right_key = config.get("right_key", "")
        threshold = config.get("threshold", 80)
        algorithm = config.get("algorithm", "ratio")

        if not left_key or not right_key:
            raise ValueError("Match key columns must be specified")

        try:
            from rapidfuzz import fuzz, process
        except ImportError:
            raise ImportError("Install 'rapidfuzz' for fuzzy matching: pip install rapidfuzz")

        scorer_map = {
            "ratio": fuzz.ratio,
            "partial_ratio": fuzz.partial_ratio,
            "token_sort_ratio": fuzz.token_sort_ratio,
            "token_set_ratio": fuzz.token_set_ratio,
        }
        scorer = scorer_map.get(algorithm, fuzz.ratio)

        right_values = right[right_key].astype(str).tolist()
        matches = []

        for idx, left_val in enumerate(left[left_key].astype(str)):
            result = process.extractOne(
                left_val, right_values, scorer=scorer, score_cutoff=threshold
            )
            if result:
                match_val, score, match_idx = result
                match_row = {
                    **{f"left_{c}": left.iloc[idx][c] for c in left.columns},
                    **{f"right_{c}": right.iloc[match_idx][c] for c in right.columns},
                    "match_score": score,
                }
                matches.append(match_row)
            else:
                match_row = {
                    **{f"left_{c}": left.iloc[idx][c] for c in left.columns},
                    **{f"right_{c}": None for c in right.columns},
                    "match_score": 0,
                }
                matches.append(match_row)

        result_df = pd.DataFrame(matches) if matches else pd.DataFrame()
        return {"output": result_df}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "left_key": {"type": "column_select", "label": "Left Match Column"},
            "right_key": {"type": "column_select", "label": "Right Match Column"},
            "threshold": {"type": "number", "label": "Match Threshold (0-100)", "default": 80},
            "algorithm": {
                "type": "select",
                "options": ["ratio", "partial_ratio", "token_sort_ratio", "token_set_ratio"],
                "default": "ratio",
                "label": "Algorithm",
            },
        }
