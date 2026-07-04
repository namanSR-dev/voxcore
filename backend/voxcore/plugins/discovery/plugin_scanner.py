"""
plugins/discovery/plugin_scanner.py

Scans configured directories for plugin manifests and loads their metadata.
"""
from typing import List, Any

class PluginScanner:
    """
    Discovers installed plugins dynamically from disk.
    """
    def __init__(self, search_paths: List[str]) -> None:
        pass

    def discover(self) -> List[Any]:
        """
        Scans directories, finding valid plugin packages.
        """
        pass

    def _parse_manifest(self, file_path: str) -> Any:
        pass
