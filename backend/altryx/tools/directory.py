from typing import Any

import os
import pandas as pd

from altryx.tools.base import BaseTool
from altryx.config import UPLOAD_DIR


class DirectoryTool(BaseTool):
    """Lists files in a directory as a DataFrame — like Alteryx's Directory tool.
    Output columns: FileName, FullPath, Extension, SizeBytes, ModifiedDate.
    """
    tool_type = "directory"
    label = "Directory"
    category = "IO"
    inputs: list[str] = []
    outputs = ["output"]

    def execute(self, inputs: dict[str, pd.DataFrame], config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        source = config.get("source", "local")

        if source == "google_drive":
            return self._list_google_drive(config)
        elif source == "uploads":
            return self._list_local_dir(str(UPLOAD_DIR), config)
        return self._list_local(config)

    def _list_local(self, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        directory = config.get("directory_path", "").strip()
        if not directory:
            raise ValueError("Directory path is required. Enter an absolute path on the server filesystem.")
        # Expand ~ to home directory
        directory = os.path.expanduser(directory)
        if not os.path.isdir(directory):
            raise ValueError(
                f"Directory not found: '{directory}'. "
                f"This path must exist on the server running the backend. "
                f"Available sample data: /home/user/altryx-clone/sample-data. "
                f"Uploaded files: {UPLOAD_DIR}"
            )
        return self._list_local_dir(directory, config)

    def _list_local_dir(self, directory: str, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        file_pattern = config.get("file_pattern", "*")
        include_subdirs = config.get("include_subdirs", False)
        collect_full_path = config.get("collect_full_path", True)

        import glob as glob_mod

        if include_subdirs:
            search = os.path.join(directory, "**", file_pattern)
            files = glob_mod.glob(search, recursive=True)
        else:
            search = os.path.join(directory, file_pattern)
            files = glob_mod.glob(search)

        # Filter out directories, keep only files
        files = [f for f in files if os.path.isfile(f)]

        records = []
        for f in files:
            stat = os.stat(f)
            records.append({
                "FileName": os.path.basename(f),
                "FullPath": os.path.abspath(f) if collect_full_path else f,
                "Directory": os.path.dirname(os.path.abspath(f)),
                "Extension": os.path.splitext(f)[1].lstrip("."),
                "SizeBytes": stat.st_size,
                "ModifiedDate": pd.Timestamp.fromtimestamp(stat.st_mtime).isoformat(),
            })

        if not records:
            raise ValueError(
                f"No files found matching pattern '{file_pattern}' in '{directory}'. "
                f"Check the path and pattern."
            )

        return {"output": pd.DataFrame(records)}

    def _list_google_drive(self, config: dict[str, Any]) -> dict[str, pd.DataFrame]:
        from altryx.connectors.google_drive import GoogleDriveConnector

        credentials_json = config.get("credentials_json", "")
        folder_id = config.get("folder_id", "")
        include_subdirs = config.get("include_subdirs", False)

        connector = GoogleDriveConnector(credentials_json)
        files = connector.list_files(folder_id, recursive=include_subdirs)

        return {"output": pd.DataFrame(files)}

    def get_config_schema(self) -> dict[str, Any]:
        return {
            "source": {"type": "select", "options": ["local", "uploads", "google_drive"], "default": "local"},
            "directory_path": {"type": "text", "label": "Directory Path", "placeholder": "/path/to/directory"},
            "file_pattern": {"type": "text", "label": "File Pattern", "default": "*", "placeholder": "*.csv"},
            "include_subdirs": {"type": "checkbox", "label": "Include subdirectories", "default": False},
            "collect_full_path": {"type": "checkbox", "label": "Include full path", "default": True},
            "credentials_json": {"type": "text", "label": "Google Service Account JSON path"},
            "folder_id": {"type": "text", "label": "Google Drive Folder ID"},
        }
