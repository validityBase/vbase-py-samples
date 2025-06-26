"""VBase Processing Pipeline for Stamping Files"""
import json
from .datasource import AbstractDataSource, NOT_IN_COLLECTION
from .apiclient import ApiClient
from typing import List, Dict
from pathlib import Path


class Pipeline:
    """Pipeline for processing and stamping files in vBase collections."""
    def __init__(self, data_source: AbstractDataSource, stamping_client: ApiClient):
        """Initialize the processing pipeline with a data source and a stamping client."""
        self.data_source = data_source
        self.stamping_client = stamping_client
        self.stamped_files = []

    def preview(self, current_user: str) -> List[Dict]:
        """Preview the files that will be processed for the current user."""
        collections = self.data_source.load_collections(current_user)
        preview_list = []
        for collection in collections:
            collection_path = collection["collection_path"]
            collection_name = collection["collection_name"]
            collection_cid = collection.get("collection_cid")
            files = self.data_source.get_files_for_collection(collection_path)
            for file_path in files:
                preview_list.append({
                    "file": file_path.name,
                    "collection": collection_name,
                    "collection_cid": collection_cid,
                    "path": str(file_path),
                    "user": current_user
                })
        return preview_list
    
    def log_entry(self, file_path: Path, collection_name: str, user: str, msg: str):
        """Create a log entry."""
        entry =  {
            "file": file_path.name,
            "collection": collection_name,
            "path": str(file_path),
            "user": user,
            "msg": msg
        }
        print(f"{entry['file']} -> Collection: {entry['collection']} | Msg: {entry['msg']}")
        return entry
    
    def run(self, current_user: str):
        """Run the processing pipeline for the current user."""
        self.stamped_files = []
        collections = self.data_source.load_collections(current_user)
        for collection in collections:
            collection_path = collection.get("collection_path")
            collection_name = collection.get("collection_name")
            collection_cid = collection.get("collection_cid")
            files = self.data_source.get_files_for_collection(collection_path)
            for file_path in files:
                with open(file_path, "rb") as f:
                    input_files = {"file": f}
                    data = {
                        "storeStampedFiles": "true",
                        "idempotent": "true",
                        "idempotencyWindow": "3600",
                    }
                    if collection_cid:
                        data["collectionCid"] = collection_cid
                        msg = f"Stamping file {file_path.name} in collection {collection_name} with CID {collection_cid}"
                    else:
                        msg = f"Stamping file {file_path.name} without collection CID"
                        
                    entry = self.log_entry(file_path, collection_name, current_user, msg)
                    self.stamped_files.append(entry)
                        
                    result = self.stamping_client.stamp(input_data=data, input_files=input_files)
                    entry = self.log_entry(file_path, collection_name, current_user, result)
                    self.stamped_files.append(entry)
                    

    def preview_configuration(self, current_user: str) -> Dict:
        """Preview the configuration for the current user."""
        return {
            "active_user": current_user,
            "collections": self.data_source.load_collections(current_user)
        }
    
    def write_log(self, path: Path):
        """Write the stamped files log to a JSON file."""
        with open(path, "w") as f:
            json.dump(self.stamped_files, f, indent=2)

    def print_summary(self):
        """Print a summary of the stamped files."""
        print("\n=== Summary of Stamped Files ===")
        for entry in self.stamped_files:
            print(f"{entry['file']} -> Collection: {entry['collection']} | Response: {entry['msg']}")
