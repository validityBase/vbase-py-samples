"""Stamping Service for VBase API"""
import logging
from typing import Any, Dict, Optional, TypedDict

import requests

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 30


class StampData(TypedDict, total=False):
    """Data structure for the stamping API request payload.

    Naming convention:
    - 'dataCid' refers to the CID (Content Identifier) of the input data.
    - 'collectionCid' refers to the CID of the associated collection.
    """
    data: Optional[str]
    dataCid: Optional[str]
    collectionCid: Optional[str]
    storeStampedFiles: bool
    idempotent: bool
    idempotencyWindow: int


class ApiClient:
    """Api Client for interacting with the VBase API for stamping files."""
    def __init__(self, base_url: str, api_token: str):
        self.base_url = base_url.rstrip("/")
        self.api_token = api_token
        self.stamp_url = f"{self.base_url}/api/v1/stamp/"

    def stamp(self, input_data: Optional[StampData] = None, input_files: Optional[Dict[str, Any]] = None) -> Dict:
        """ Send a stamping request to the VBase API."""
        headers = {
            "Authorization": f"Bearer {self.api_token}"
        }
        if input_files is None:
            input_files = {}

        try:
            response = requests.post(
                self.stamp_url,
                data=input_data,
                files=input_files,
                headers=headers,
                timeout=REQUEST_TIMEOUT
            )
            response.raise_for_status()
        except requests.RequestException as e:
            logger.error("Request to VBase API failed: %s", e)
            logger.error("Response: %s", response.text if 'response' in locals() else 'No response')
            
            curl_cmd = self._build_curl(self.stamp_url, headers, input_data, input_files)
            logger.error("Try this with curl:\n%s", curl_cmd)
            raise

        try:
            return response.json()
        except Exception as e:
            logger.error("Failed to parse JSON from stamp response: %s", response.text)
            raise e

    def _build_curl(self, url: str, headers: dict, data: dict, files: dict) -> str:
        curl_parts = [f"curl -X POST '{url}'"]

        # Add headers
        for k, v in headers.items():
            curl_parts.append(f"-H '{k}: {v}'")

        # Add form fields
        for k, v in data.items():
            curl_parts.append(f"-F '{k}={v}'")

        # Add files
        for k, file_value in files.items():
            if isinstance(file_value, tuple):
                # format: (filename, fileobj, ...)
                filename = file_value[0]
            elif hasattr(file_value, 'name'):
                # file object directly
                filename = file_value.name
            else:
                filename = 'unknown'

            curl_parts.append(f"-F '{k}=@{filename}'")

        return " \\\n  ".join(curl_parts)