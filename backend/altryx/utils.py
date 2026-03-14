"""
Reusable DataFrame utility functions for migrating workflows to Python.
All common operations are centralized here so project scripts stay clean.
Import and call these instead of writing inline filter, join, summarize, or union logic.
"""
import pandas as pd
import numpy as np
import re
import os
import glob
from typing import Union, Optional


# ---------------------------------------------------------------------------
# Input / Output helpers
# ---------------------------------------------------------------------------
def read_excel_sheet(
    filepath: str,
    sheet_name: str = "Sheet1",
    **kwargs,
) -> pd.DataFrame:
    """Read a single sheet from an Excel workbook."""
    return pd.read_excel(filepath, sheet_name=sheet_name, **kwargs)


def read_csv_file(filepath: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(filepath, **kwargs)


def read_all_files_in_directory(
    directory: str,
    file_pattern: str = "*.*",
    include_subdirs: bool = False,
    reader: str = "csv",
    add_filename_column: bool = True,
    **read_kwargs,
) -> pd.DataFrame:
    """Scan a directory for files matching *file_pattern*, read each into a
    DataFrame, and vertically stack them.  Optionally adds a ``FileName``
    column with the source file name.

    Parameters
    ----------
    reader : str
        ``"csv"``, ``"excel"``, or ``"parquet"``.
    """
    search_path = os.path.join(directory, "**", file_pattern) if include_subdirs else os.path.join(directory, file_pattern)
    files = glob.glob(search_path, recursive=include_subdirs)

    readers = {
        "csv": pd.read_csv,
        "excel": pd.read_excel,
        "parquet": pd.read_parquet,
    }
    read_fn = readers.get(reader, pd.read_csv)

    frames = []
    for f in files:
        frame = read_fn(f, **read_kwargs)
        if add_filename_column:
            frame["FileName"] = os.path.basename(f)
        frames.append(frame)

    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, ignore_index=True)


def write_csv(df: pd.DataFrame, filepath: str, **kwargs) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_csv(filepath, index=False, **kwargs)


def write_excel(
    df: pd.DataFrame,
    filepath: str,
    sheet_name: str = "Sheet1",
    **kwargs,
) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_excel(filepath, sheet_name=sheet_name, index=False, **kwargs)


def write_parquet(df: pd.DataFrame, filepath: str, **kwargs) -> None:
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    df.to_parquet(filepath, index=False, **kwargs)


# ---------------------------------------------------------------------------
# Filtering
# ---------------------------------------------------------------------------
def filter_rows(
    df: pd.DataFrame,
    column: str,
    operator: str,
    value,
    case_sensitive: bool = True,
) -> pd.DataFrame:
    """Return rows that satisfy a single condition.

    Supported operators
    -------------------
    ``"=="``, ``"!="``, ``">"``, ``">="``, ``"<"``, ``"<="``,
    ``"in"``, ``"not_in"``, ``"contains"``, ``"not_contains"``,
    ``"is_null"``, ``"is_not_null"``.

    For ``"in"`` / ``"not_in"`` pass *value* as a list or set.
    """
    col = df[column]

    if not case_sensitive and col.dtype == object:
        col = col.str.lower()
        if isinstance(value, str):
            value = value.lower()
        elif isinstance(value, (list, set, tuple)):
            value = [v.lower() if isinstance(v, str) else v for v in value]

    ops = {
        "==": lambda: col == value,
        "!=": lambda: col != value,
        ">": lambda: col > value,
        ">=": lambda: col >= value,
        "<": lambda: col < value,
        "<=": lambda: col <= value,
        "in": lambda: col.isin(value),
        "not_in": lambda: ~col.isin(value),
        "contains": lambda: col.str.contains(str(value), na=False, case=case_sensitive),
        "not_contains": lambda: ~col.str.contains(str(value), na=False, case=case_sensitive),
        "is_null": lambda: col.isna(),
        "is_not_null": lambda: col.notna(),
    }

    mask = ops[operator]()
    return df.loc[mask].reset_index(drop=True)


def filter_by_expression(df: pd.DataFrame, expression: str) -> pd.DataFrame:
    """Filter rows using a pandas query expression string."""
    if not expression:
        return df.copy()
    return df.query(expression).reset_index(drop=True)


def filter_custom(df: pd.DataFrame, mask: pd.Series) -> pd.DataFrame:
    """Apply an arbitrary boolean mask and return the matching rows."""
    return df.loc[mask].reset_index(drop=True)


def split_by_filter(
    df: pd.DataFrame,
    column: str,
    operator: str,
    value,
    case_sensitive: bool = True,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split a DataFrame into (true_branch, false_branch) based on a condition.
    Mirrors the two-output behaviour of a filter tool.
    """
    true_branch = filter_rows(df, column, operator, value, case_sensitive)
    false_branch = df.loc[~df.index.isin(true_branch.index)].reset_index(drop=True)
    return true_branch, false_branch


# ---------------------------------------------------------------------------
# Joining
# ---------------------------------------------------------------------------
def join_dataframes(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_on: Union[str, list[str]],
    right_on: Union[str, list[str]],
    how: str = "inner",
    suffixes: tuple[str, str] = ("_left", "_right"),
) -> pd.DataFrame:
    """Merge two DataFrames on specified key columns."""
    return pd.merge(
        left,
        right,
        left_on=left_on,
        right_on=right_on,
        how=how,
        suffixes=suffixes,
    )


def join_with_unmatched(
    left: pd.DataFrame,
    right: pd.DataFrame,
    left_on: Union[str, list[str]],
    right_on: Union[str, list[str]],
    suffixes: tuple[str, str] = ("_left", "_right"),
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Full outer join returning (matched, left_unmatched, right_unmatched)."""
    merged = pd.merge(
        left,
        right,
        left_on=left_on,
        right_on=right_on,
        how="outer",
        suffixes=suffixes,
        indicator=True,
    )
    matched = merged[merged["_merge"] == "both"].drop(columns="_merge").reset_index(drop=True)
    left_only = merged[merged["_merge"] == "left_only"].drop(columns="_merge").reset_index(drop=True)
    right_only = merged[merged["_merge"] == "right_only"].drop(columns="_merge").reset_index(drop=True)
    return matched, left_only, right_only


# ---------------------------------------------------------------------------
# Selecting / Renaming / Reordering columns
# ---------------------------------------------------------------------------
def select_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Keep only the listed columns, in the order given."""
    return df[columns].copy()


def rename_columns(
    df: pd.DataFrame,
    rename_map: dict[str, str],
) -> pd.DataFrame:
    """Rename columns according to *rename_map* ``{old: new}``."""
    return df.rename(columns=rename_map)


def drop_columns(df: pd.DataFrame, columns: list[str]) -> pd.DataFrame:
    """Drop columns that exist in the DataFrame; silently ignores missing."""
    return df.drop(columns=[c for c in columns if c in df.columns])


def reorder_columns(
    df: pd.DataFrame,
    leading_columns: list[str],
) -> pd.DataFrame:
    """Move *leading_columns* to the front, keeping the rest in original order."""
    remaining = [c for c in df.columns if c not in leading_columns]
    return df[leading_columns + remaining]


# ---------------------------------------------------------------------------
# Sorting
# ---------------------------------------------------------------------------
def sort_rows(
    df: pd.DataFrame,
    by: Union[str, list[str]],
    ascending: Union[bool, list[bool]] = True,
) -> pd.DataFrame:
    return df.sort_values(by=by, ascending=ascending).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Summarize / Aggregate
# ---------------------------------------------------------------------------
def summarize(
    df: pd.DataFrame,
    group_by: Union[str, list[str]],
    agg_dict: dict[str, Union[str, list[str]]],
) -> pd.DataFrame:
    """Group and aggregate.

    Parameters
    ----------
    agg_dict : dict
        ``{column: agg_func}`` where *agg_func* is ``"sum"``, ``"count"``,
        ``"mean"``, ``"min"``, ``"max"``, ``"first"``, ``"last"``, or a list
        of those.

    Example
    -------
    >>> summarize(df, "Company", {"Amount": "sum", "Account": "count"})
    """
    result = df.groupby(group_by, as_index=False).agg(agg_dict)

    if isinstance(result.columns, pd.MultiIndex):
        result.columns = [
            "_".join(str(c) for c in col).rstrip("_") for col in result.columns
        ]

    return result


def summarize_no_group(
    df: pd.DataFrame,
    agg_dict: dict[str, Union[str, list[str]]],
) -> pd.DataFrame:
    """Aggregate without grouping, returning a single-row DataFrame."""
    result = df.agg(agg_dict)
    if isinstance(result, pd.Series):
        result = result.to_frame().T
    if isinstance(result.columns, pd.MultiIndex):
        result.columns = [
            f"{col}_{func}" for col, func in result.columns
        ]
    return result.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Union (vertical stack)
# ---------------------------------------------------------------------------
def union_dataframes(
    *dataframes: pd.DataFrame,
    by_name: bool = True,
) -> pd.DataFrame:
    """Vertically stack multiple DataFrames.

    Parameters
    ----------
    by_name : bool
        When True (default), columns are aligned by name.  When False, columns
        are aligned by position.
    """
    frames = [df for df in dataframes if df is not None and not df.empty]
    if not frames:
        return pd.DataFrame()

    if by_name:
        return pd.concat(frames, ignore_index=True, sort=False)
    return pd.concat(frames, ignore_index=True, sort=False, join="inner")


# ---------------------------------------------------------------------------
# Formula / Calculated columns
# ---------------------------------------------------------------------------
def add_formula_column(
    df: pd.DataFrame,
    column_name: str,
    expression,
) -> pd.DataFrame:
    """Add or overwrite a column.

    *expression* can be:
      - a scalar (broadcast to all rows)
      - a ``pd.Series`` of the same length
      - a callable taking the DataFrame and returning a Series
    """
    result = df.copy()
    if callable(expression):
        result[column_name] = expression(result)
    else:
        result[column_name] = expression
    return result


def add_eval_column(
    df: pd.DataFrame,
    column_name: str,
    expression: str,
) -> pd.DataFrame:
    """Add a column computed via a pandas eval expression string."""
    result = df.copy()
    result[column_name] = result.eval(expression)
    return result


def apply_formula(
    df: pd.DataFrame,
    column_name: str,
    func,
) -> pd.DataFrame:
    """Apply a row-level function to create or overwrite a column.

    *func* receives each row as a ``pd.Series`` (axis=1).
    """
    result = df.copy()
    result[column_name] = result.apply(func, axis=1)
    return result


def concat_columns(
    df: pd.DataFrame,
    new_column: str,
    columns: list[str],
    separator: str = "",
) -> pd.DataFrame:
    """Create *new_column* by concatenating stringified *columns*."""
    result = df.copy()
    result[new_column] = result[columns].astype(str).agg(separator.join, axis=1)
    return result


def replace_in_column(
    df: pd.DataFrame,
    column: str,
    old: str,
    new: str,
    regex: bool = False,
) -> pd.DataFrame:
    """Replace occurrences of *old* with *new* in a string column."""
    result = df.copy()
    result[column] = result[column].str.replace(old, new, regex=regex)
    return result


# ---------------------------------------------------------------------------
# Regex parsing
# ---------------------------------------------------------------------------
def regex_extract(
    df: pd.DataFrame,
    column: str,
    pattern: str,
    output_columns: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Extract capture groups from *column* using *pattern* and add them as
    new columns.
    """
    result = df.copy()
    extracted = result[column].astype(str).str.extract(pattern, expand=True)

    if output_columns:
        for idx, col_name in enumerate(output_columns):
            if idx < extracted.shape[1]:
                result[col_name] = extracted.iloc[:, idx]
    else:
        for idx in range(extracted.shape[1]):
            col_name = extracted.columns[idx] if isinstance(extracted.columns[idx], str) and extracted.columns[idx] else f"regex_{idx+1}"
            result[col_name] = extracted.iloc[:, idx]

    return result


def regex_replace(
    df: pd.DataFrame,
    column: str,
    pattern: str,
    replacement: str,
    output_column: Optional[str] = None,
) -> pd.DataFrame:
    """Replace regex matches in a column."""
    result = df.copy()
    target = output_column or column
    result[target] = result[column].astype(str).str.replace(pattern, replacement, regex=True)
    return result


def regex_match(
    df: pd.DataFrame,
    column: str,
    pattern: str,
    output_column: str = "match",
) -> pd.DataFrame:
    """Boolean column indicating whether the pattern matches."""
    result = df.copy()
    result[output_column] = result[column].astype(str).str.contains(pattern, regex=True, na=False)
    return result


def regex_findall(
    df: pd.DataFrame,
    column: str,
    pattern: str,
    output_column: str = "matches",
) -> pd.DataFrame:
    """Find all pattern matches, joined as comma-separated string."""
    result = df.copy()
    result[output_column] = result[column].astype(str).str.findall(pattern).apply(
        lambda x: ", ".join(x) if isinstance(x, list) else ""
    )
    return result


def regex_count(
    df: pd.DataFrame,
    column: str,
    pattern: str,
    output_column: str = "count",
) -> pd.DataFrame:
    """Count pattern occurrences per row."""
    result = df.copy()
    result[output_column] = result[column].astype(str).str.count(pattern)
    return result


# ---------------------------------------------------------------------------
# CrossTab (pivot)
# ---------------------------------------------------------------------------
def crosstab_pivot(
    df: pd.DataFrame,
    group_by: Union[str, list[str]],
    header_column: str,
    value_column: str,
    agg_func: str = "sum",
) -> pd.DataFrame:
    """Pivot data so that unique values of *header_column* become new columns,
    filled with aggregated *value_column*.
    """
    table = pd.pivot_table(
        df,
        index=group_by,
        columns=header_column,
        values=value_column,
        aggfunc=agg_func,
        fill_value=0,
    ).reset_index()

    table.columns.name = None
    if isinstance(table.columns, pd.MultiIndex):
        table.columns = [
            "_".join(str(c) for c in col).rstrip("_") for col in table.columns
        ]
    return table


def crosstab_count(
    df: pd.DataFrame,
    row_field: str,
    column_field: str,
) -> pd.DataFrame:
    """Simple crosstab with counts."""
    result = pd.crosstab(df[row_field], df[column_field]).reset_index()
    result.columns = [str(c) for c in result.columns]
    return result


# ---------------------------------------------------------------------------
# Transpose
# ---------------------------------------------------------------------------
def transpose_dataframe(
    df: pd.DataFrame,
    header_column: Optional[str] = None,
) -> pd.DataFrame:
    """Transpose a DataFrame, optionally using a column as row headers."""
    work = df.copy()
    if header_column and header_column in work.columns:
        work = work.set_index(header_column)

    result = work.T.reset_index()
    result.columns = [str(c) for c in result.columns]

    if result.columns[0] == "index":
        result = result.rename(columns={"index": "field_name"})

    return result


def transpose_columns(
    df: pd.DataFrame,
    key_columns: list[str],
    value_columns: list[str],
    name_col: str = "Name",
    value_col: str = "Value",
) -> pd.DataFrame:
    """Unpivot (melt) *value_columns* into long format, keeping *key_columns*."""
    return df.melt(
        id_vars=key_columns,
        value_vars=value_columns,
        var_name=name_col,
        value_name=value_col,
    )


# ---------------------------------------------------------------------------
# Unique / Dedup
# ---------------------------------------------------------------------------
def unique_rows(
    df: pd.DataFrame,
    subset: Optional[list[str]] = None,
    keep: str = "first",
) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset, keep=keep).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Sample (first N / last N / skip N / random N)
# ---------------------------------------------------------------------------
def sample_rows(
    df: pd.DataFrame,
    mode: str = "first",
    n: int = 100,
    group_by: Optional[Union[str, list[str]]] = None,
) -> pd.DataFrame:
    """Return a subset of rows.

    Parameters
    ----------
    mode : str
        ``"first"`` / ``"first_n"`` -- first *n* rows.
        ``"last"`` / ``"last_n"``  -- last *n* rows.
        ``"skip_first"`` -- skip the first *n*, keep the rest.
        ``"random"`` / ``"random_n"`` -- random sample of *n* rows.
        ``"every_nth"`` -- every n-th row (1-indexed).
    """
    def _sample(frame: pd.DataFrame) -> pd.DataFrame:
        if mode in ("first", "first_n"):
            return frame.head(n)
        elif mode in ("last", "last_n"):
            return frame.tail(n)
        elif mode == "skip_first":
            return frame.iloc[n:]
        elif mode in ("random", "random_n"):
            return frame.sample(n=min(n, len(frame)))
        elif mode == "every_nth":
            return frame.iloc[::n]
        return frame.head(n)

    if group_by:
        return df.groupby(group_by, group_keys=False).apply(_sample).reset_index(drop=True)
    return _sample(df).reset_index(drop=True)


def sample_percentage(
    df: pd.DataFrame,
    percentage: float,
) -> pd.DataFrame:
    """Random sample by percentage (0-100)."""
    frac = percentage / 100.0
    return df.sample(frac=min(frac, 1.0)).reset_index(drop=True)


# ---------------------------------------------------------------------------
# Record ID
# ---------------------------------------------------------------------------
def add_record_id(
    df: pd.DataFrame,
    column_name: str = "RecordID",
    start: int = 1,
) -> pd.DataFrame:
    result = df.copy()
    result[column_name] = range(start, start + len(result))
    return result


# ---------------------------------------------------------------------------
# DateTime helpers
# ---------------------------------------------------------------------------
def parse_date(
    df: pd.DataFrame,
    column: str,
    fmt: str,
    output_column: Optional[str] = None,
) -> pd.DataFrame:
    result = df.copy()
    target = output_column or column
    result[target] = pd.to_datetime(result[column], format=fmt, errors="coerce")
    return result


def format_date(
    df: pd.DataFrame,
    column: str,
    fmt: str,
    output_column: Optional[str] = None,
) -> pd.DataFrame:
    result = df.copy()
    target = output_column or column
    result[target] = pd.to_datetime(result[column], errors="coerce").dt.strftime(fmt)
    return result


# ---------------------------------------------------------------------------
# Type conversion
# ---------------------------------------------------------------------------
def cast_columns(
    df: pd.DataFrame,
    type_map: dict[str, str],
) -> pd.DataFrame:
    """Cast columns to the specified pandas dtypes.

    *type_map*: ``{column: dtype_str}`` e.g. ``{"Amount": "float64"}``.
    """
    result = df.copy()
    for col, dtype in type_map.items():
        if col in result.columns:
            result[col] = result[col].astype(dtype, errors="ignore")
    return result


# ---------------------------------------------------------------------------
# Cleanse helper
# ---------------------------------------------------------------------------
def cleanse_columns(
    df: pd.DataFrame,
    columns: Optional[list[str]] = None,
    case: Optional[str] = None,
    strip_whitespace: bool = True,
    remove_nulls: bool = False,
    remove_empty_strings: bool = False,
) -> pd.DataFrame:
    """Clean string columns.

    Parameters
    ----------
    case : str or None
        ``"upper"``, ``"lower"``, ``"title"``, or None to leave unchanged.
    """
    result = df.copy()
    cols = columns or result.select_dtypes(include=["object", "string"]).columns.tolist()

    for c in cols:
        if c not in result.columns:
            continue
        if strip_whitespace:
            result[c] = result[c].astype(str).str.strip()
        if case == "upper":
            result[c] = result[c].str.upper()
        elif case == "lower":
            result[c] = result[c].str.lower()
        elif case == "title":
            result[c] = result[c].str.title()

    if remove_nulls:
        result = result.dropna()

    if remove_empty_strings:
        str_cols = result.select_dtypes(include=["object", "string"]).columns.tolist()
        for c in str_cols:
            if c in result.columns:
                result = result[result[c] != ""]

    return result.reset_index(drop=True)


# ---------------------------------------------------------------------------
# Imputation (missing value filling)
# ---------------------------------------------------------------------------
def impute_values(
    df: pd.DataFrame,
    columns: list[str],
    method: str = "mean",
    custom_value=None,
    group_by: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Fill missing values using the specified method.

    Parameters
    ----------
    method : str
        ``"mean"``, ``"median"``, ``"mode"``, ``"constant"``,
        ``"forward_fill"``, ``"backward_fill"``, ``"interpolate"``.
    """
    result = df.copy()

    for col in columns:
        if col not in result.columns:
            continue

        if method == "mean":
            if group_by:
                result[col] = result.groupby(group_by)[col].transform(lambda x: x.fillna(x.mean()))
            else:
                result[col] = result[col].fillna(result[col].mean())
        elif method == "median":
            if group_by:
                result[col] = result.groupby(group_by)[col].transform(lambda x: x.fillna(x.median()))
            else:
                result[col] = result[col].fillna(result[col].median())
        elif method == "mode":
            if group_by:
                result[col] = result.groupby(group_by)[col].transform(
                    lambda x: x.fillna(x.mode().iloc[0] if not x.mode().empty else x)
                )
            else:
                mode_val = result[col].mode()
                if not mode_val.empty:
                    result[col] = result[col].fillna(mode_val.iloc[0])
        elif method == "constant":
            try:
                fill_val = type(result[col].dropna().iloc[0])(custom_value) if not result[col].dropna().empty else custom_value
            except (ValueError, TypeError, IndexError):
                fill_val = custom_value
            result[col] = result[col].fillna(fill_val)
        elif method == "forward_fill":
            if group_by:
                result[col] = result.groupby(group_by)[col].ffill()
            else:
                result[col] = result[col].ffill()
        elif method == "backward_fill":
            if group_by:
                result[col] = result.groupby(group_by)[col].bfill()
            else:
                result[col] = result[col].bfill()
        elif method == "interpolate":
            result[col] = result[col].interpolate()

    return result


# ---------------------------------------------------------------------------
# Multi-Row Formula
# ---------------------------------------------------------------------------
def multi_row_shift(
    df: pd.DataFrame,
    source_column: str,
    output_column: str,
    row_offset: int = -1,
    operation: str = "value",
    group_by: Optional[list[str]] = None,
) -> pd.DataFrame:
    """Create a column using values from neighbouring rows.

    Parameters
    ----------
    row_offset : int
        Negative = previous rows (lag), positive = next rows (lead).
    operation : str
        ``"value"`` -- shifted value.
        ``"difference"`` -- current minus shifted.
        ``"percent_change"`` -- percentage change.
    """
    result = df.copy()

    if source_column not in result.columns:
        raise ValueError(f"Source column '{source_column}' not found")

    if group_by:
        grouped = result.groupby(group_by)[source_column]
    else:
        grouped = result[source_column]

    if operation == "value":
        result[output_column] = grouped.shift(-row_offset)
    elif operation == "difference":
        shifted = grouped.shift(-row_offset)
        result[output_column] = result[source_column] - shifted
    elif operation == "percent_change":
        result[output_column] = grouped.pct_change(periods=-row_offset)

    return result


def multi_row_formula(
    df: pd.DataFrame,
    column_name: str,
    func,
    num_rows: int = 1,
    group_by: Optional[Union[str, list[str]]] = None,
    default=None,
) -> pd.DataFrame:
    """Create or update a column using values from neighbouring rows.

    Parameters
    ----------
    func : callable
        Receives ``(current_row_value, list_of_previous_values)`` and returns
        the new value.
    """
    result = df.copy()

    def _apply(frame: pd.DataFrame) -> pd.Series:
        output = []
        source = frame[column_name].tolist() if column_name in frame.columns else [default] * len(frame)
        for i in range(len(source)):
            prev = []
            for offset in range(1, num_rows + 1):
                prev.append(source[i - offset] if i - offset >= 0 else default)
            output.append(func(source[i], prev))
        return pd.Series(output, index=frame.index)

    if group_by:
        result[column_name] = result.groupby(group_by, group_keys=False).apply(_apply).reset_index(drop=True)
    else:
        result[column_name] = _apply(result)

    return result


# ---------------------------------------------------------------------------
# Append Fields (cross join)
# ---------------------------------------------------------------------------
def append_fields(
    target: pd.DataFrame,
    source: pd.DataFrame,
) -> pd.DataFrame:
    """Cartesian (cross) join -- every row from *target* is paired with every
    row from *source*.  Use with care on large DataFrames.
    """
    target_copy = target.copy()
    source_copy = source.copy()
    target_copy["_cross_key"] = 1
    source_copy["_cross_key"] = 1
    merged = pd.merge(target_copy, source_copy, on="_cross_key", suffixes=("", "_appended"))
    return merged.drop(columns="_cross_key").reset_index(drop=True)


# ---------------------------------------------------------------------------
# Text to Columns (split delimited field)
# ---------------------------------------------------------------------------
def text_to_columns(
    df: pd.DataFrame,
    column: str,
    delimiter: str = ",",
    max_columns: Optional[int] = None,
    output_root: Optional[str] = None,
    drop_original: bool = False,
) -> pd.DataFrame:
    """Split a delimited string column into separate columns."""
    result = df.copy()
    root = output_root or column
    n_splits = (max_columns - 1) if max_columns else -1

    split_df = result[column].astype(str).str.split(delimiter, n=n_splits, expand=True)
    for idx in range(split_df.shape[1]):
        col_name = f"{root}_{idx + 1}" if split_df.shape[1] > 1 else root
        result[col_name] = split_df[idx].str.strip()

    if drop_original and column in result.columns and split_df.shape[1] > 1:
        result = result.drop(columns=[column])

    return result


# ---------------------------------------------------------------------------
# Find / Replace
# ---------------------------------------------------------------------------
def find_replace(
    df: pd.DataFrame,
    column: str,
    find: str,
    replace: str,
    use_regex: bool = False,
    case_sensitive: bool = True,
) -> pd.DataFrame:
    """Replace occurrences in a string column."""
    result = df.copy()
    result[column] = result[column].astype(str).str.replace(
        find, replace, regex=use_regex, case=case_sensitive,
    )
    return result


def find_replace_multiple(
    df: pd.DataFrame,
    column: str,
    replacements: list[dict],
    use_regex: bool = False,
    case_sensitive: bool = True,
) -> pd.DataFrame:
    """Apply multiple find/replace operations on a column.

    Parameters
    ----------
    replacements : list[dict]
        Each dict has ``"find"`` and ``"replace"`` keys.
    """
    result = df.copy()
    for repl in replacements:
        find_val = repl.get("find", "")
        replace_val = repl.get("replace", "")
        if not find_val:
            continue
        result[column] = result[column].astype(str).str.replace(
            find_val, replace_val, regex=use_regex, case=case_sensitive,
        )
    return result


# ---------------------------------------------------------------------------
# Conditional / If-Else helper
# ---------------------------------------------------------------------------
def conditional_column(
    df: pd.DataFrame,
    column_name: str,
    conditions: list[tuple],
    default=np.nan,
) -> pd.DataFrame:
    """Build a column using a list of ``(mask, value)`` pairs evaluated in
    order.  First matching condition wins.
    """
    result = df.copy()
    output = pd.Series(default, index=result.index)
    for mask, value in reversed(conditions):
        output = output.where(~mask, value)
    result[column_name] = output
    return result


# ---------------------------------------------------------------------------
# Generate Rows
# ---------------------------------------------------------------------------
def generate_rows(
    column_name: str,
    start: int,
    end: int,
    step: int = 1,
    dtype: str = "int32",
) -> pd.DataFrame:
    """Create a DataFrame with a single incrementing column."""
    values = list(range(start, end + 1, step))
    return pd.DataFrame({column_name: pd.array(values, dtype=dtype)})


# ---------------------------------------------------------------------------
# Rank
# ---------------------------------------------------------------------------
def rank_rows(
    df: pd.DataFrame,
    by: Union[str, list[str]],
    rank_column: str = "Rank",
    method: str = "ordinal",
    ascending: bool = True,
    group_by: Optional[Union[str, list[str]]] = None,
) -> pd.DataFrame:
    """Add a rank column based on one or more sort columns."""
    result = df.copy()
    if isinstance(by, str):
        by = [by]

    if group_by:
        result[rank_column] = (
            result.groupby(group_by)[by[0]]
            .rank(method=method, ascending=ascending)
            .astype(int)
        )
    else:
        result[rank_column] = result[by[0]].rank(method=method, ascending=ascending).astype(int)

    return result


# ---------------------------------------------------------------------------
# Running Total (cumulative sum)
# ---------------------------------------------------------------------------
def running_total(
    df: pd.DataFrame,
    columns: Union[str, list[str]],
    group_by: Optional[Union[str, list[str]]] = None,
    output_prefix: str = "Running_",
) -> pd.DataFrame:
    """Add cumulative-sum columns for one or more numeric fields."""
    result = df.copy()
    if isinstance(columns, str):
        columns = [columns]

    for col in columns:
        out_name = f"{output_prefix}{col}"
        if group_by:
            result[out_name] = result.groupby(group_by)[col].cumsum()
        else:
            result[out_name] = result[col].cumsum()
    return result


# ---------------------------------------------------------------------------
# Multi-sheet Excel writer
# ---------------------------------------------------------------------------
def write_multi_sheet_excel(
    filepath: str,
    sheet_dict: dict[str, pd.DataFrame],
) -> None:
    """Write multiple DataFrames to separate sheets in one Excel file."""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:
        for sheet_name, frame in sheet_dict.items():
            frame.to_excel(writer, sheet_name=sheet_name, index=False)
