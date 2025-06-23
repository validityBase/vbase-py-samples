"""Data source interface and implementation for local file system data storage."""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional
import json


class AbstractDataSource(ABC):
    """Abstract base class for data sources."""
    @abstractmethod
    def load_users(self) -> Dict: ...
    """Load user configurations from the data source."""
    
    @abstractmethod
    def load_collections(self, user_id: str) -> List[Dict]: ...
    """Load collections for a specific user from the data source."""
    
    @abstractmethod
    def get_files_for_collection(self, collection_path: Path) -> List[Path]: ...
    """Get files for a specific collection from the data source."""


class LocalFileFolderDataSource(AbstractDataSource):
    """Local file system data source implementation."""
    def __init__(self, users_root: Path):
        self.users_root = users_root
        self.user_configs = {}

    def load_users(self) -> Dict:
        """Load user configurations from the local file system."""
        users_config = {"users": {}}
        for user_dir in self.users_root.iterdir():
            if user_dir.is_dir():
                user_config_path = user_dir / "user_config.json"
                if user_config_path.exists():
                    with open(user_config_path) as f:
                        meta = json.load(f)
                    collections_dir = user_dir / "collections"
                    collections = {}
                    if collections_dir.exists():
                        for collection_folder in collections_dir.iterdir():
                            if collection_folder.is_dir():
                                collection_config_path = collection_folder / "collection_config.json"
                                collection_cid = None
                                if collection_config_path.exists():
                                    with open(collection_config_path) as cf:
                                        config = json.load(cf)
                                        collection_cid = config.get("collection_cid")
                                collections[collection_folder.name] = {"collection_cid": collection_cid}
                    uncategorized = user_dir / "uncategorized"
                    if uncategorized.exists():
                        collections["uncategorized"] = {"collection_cid": None}
                    users_config["users"][user_dir.name] = {
                        "api_key": meta.get("api_key"),
                        "collections": collections
                    }
        self.user_configs = users_config
        return users_config

    def load_collections(self, user_id: str) -> List[Dict]:
        """Load collections for a specific user."""
        collections = []
        user_path = self.users_root / user_id
        collections_path = user_path / "collections"
        if collections_path.exists():
            for item in collections_path.iterdir():
                if item.is_dir():
                    config_path = item / "collection_config.json"
                    collection_cid = None
                    if config_path.exists():
                        with open(config_path) as f:
                            config = json.load(f)
                            collection_cid = config.get("collection_cid")
                    collections.append({
                        "collection_path": item,
                        "collection_name": item.name,
                        "collection_cid": collection_cid
                    })
        uncategorized_path = user_path / "uncategorized"
        if uncategorized_path.exists():
            collections.append({
                "collection_path": uncategorized_path,
                "collection_name": "uncategorized",
                "collection_cid": None
            })
        return collections

    def get_files_for_collection(self, collection_path: Path) -> List[Path]:
        """Get files for a specific collection."""
        return [f for f in collection_path.iterdir() if f.is_file()]
