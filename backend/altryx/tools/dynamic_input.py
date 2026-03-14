from typing import Any

import os
import pandas as pd

from altryx.tools.base import BaseTool
from altryx.utils import read_csv_file, read_excel_sheet, read_all_files_in_directory


class DynamicInputTool(BaseTool):
    """Reads all files from a directory (or Google Drive folder) matching a
    pattern and stacks them into one DataFrame — like Alteryx's Dynamic Input.

    Can also accept a file list from the Directory tool via the 'file_list'
    input handle (optional).
    """
    tool_type = "dynamic_input"
    label = "Dynamic Input"
    category = "IO"
    inputs = ["file_list"]  # optional: connect Directory tool output
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        source = config.get("source", "local")

        if source == "google_drive":
            return self._read_google_drive(config)

        # If a file_list is connected from Directory tool, use those paths
        file_list_df = inputs.get("file_list")
        if file_list_df is not None and not file_list_df.empty and "FullPath" in file_list_df.columns:
            return self._read_from_file_list(file_list_df, config)

        # Otherwise, scan directory directly
        return self._read_from_directory(config)

    def _read_from_file_list(self, file_list_df: pd.DataFrame, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        """Read files from paths provided by the Directory tool."""
        reader_type = config.get("reader", "csv")
        add_filename = config.get("add_filename_column", True)

        frames = []
        for _, row in file_list_df.iterrows():
            path = row["FullPath"]
            if not os.path.isfile(path):
                continue

            try:
                df = self._read_single_file(path, reader_type, config)
                if add_filename:
                    df["FileName"] = os.path.basename(path)
                frames.append(df)
            except Exception:
                continue  # skip unreadable files

        if not frames:
            return {"output": pd.DataFrame()}
        return {"output": pd.concat(frames, ignore_index=True)}

    def _read_from_directory(self, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        """Scan a directory and read all matching files."""
        directory = config.get("directory_path", "")
        if not directory:
            raise ValueError("Directory path is required")

        file_pattern = config.get("file_pattern", "*.*")
        reader_type = config.get("reader", "csv")
        include_subdirs = config.get("include_subdirs", False)
        add_filename = config.get("add_filename_column", True)

        df = read_all_files_in_directory(
            directory,
            file_pattern=file_pattern,
            include_subdirs=include_subdirs,
            reader=reader_type,
            add_filename_column=add_filename,
        )
        return {"output": df}

    def _read_google_drive(self, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        """Download and read files from Google Drive folder."""
        from altryx.connectors.google_drive import GoogleDriveConnector

        credentials_json = config.get("credentials_json", "")
        folder_id = config.get("folder_id", "")
        file_pattern = config.get("file_pattern", "*.*")
        reader_type = config.get("reader", "csv")
        add_filename = config.get("add_filename_column", True)

        connector = GoogleDriveConnector(credentials_json)
        frames = connector.read_files(
            folder_id=folder_id,
            file_pattern=file_pattern,
            reader=reader_type,
            add_filename_column=add_filename,
        )

        if not frames:
            return {"output": pd.DataFrame()}
        return {"output": pd.concat(frames, ignore_index=True)}

    def _read_single_file(self, path: str, reader_type: str, config: dict[str, Any]) -> pd.DataFrame:
        """Read a single file based on reader type."""
        if reader_type == "csv":
            delimiter = config.get("delimiter", ",")
            return read_csv_file(path, delimiter=delimiter)
        elif reader_type == "excel":
            sheet = config.get("sheet_name", 0)
            return read_excel_sheet(path, sheet_name=sheet)
        elif reader_type == "parquet":
            return pd.read_parquet(path)
        elif reader_type == "json":
            return pd.read_json(path)
        else:
            return read_csv_file(path)

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "source": {"type": "select", "options": ["local", "google_drive"], "default": "local"},
            "directory_path": {"type": "text", "label": "Directory Path", "placeholder": "/path/to/files"},
            "file_pattern": {"type": "text", "label": "File Pattern", "default": "*.*", "placeholder": "*.csv"},
            "reader": {"type": "select", "options": ["csv", "excel", "parquet", "json"], "default": "csv"},
            "delimiter": {"type": "text", "label": "CSV Delimiter", "default": ","},
            "sheet_name": {"type": "text", "label": "Sheet Name (Excel)", "default": "Sheet1"},
            "include_subdirs": {"type": "checkbox", "label": "Include subdirectories", "default": False},
            "add_filename_column": {"type": "checkbox", "label": "Add FileName column", "default": True},
            "credentials_json": {"type": "text", "label": "Google Service Account JSON path"},
            "folder_id": {"type": "text", "label": "Google Drive Folder ID"},
        }
