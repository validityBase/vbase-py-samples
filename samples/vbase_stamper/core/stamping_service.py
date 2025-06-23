"""Stamping Service for VBase API"""
import requests
from typing import Optional, Dict, Any, TypedDict
import logging

logger = logging.getLogger(__name__)
REQUEST_TIMEOUT = 30


class StampData(TypedDict, total=False):
    """Data structure for stamping request."""
    data: Optional[str]
    dataCid: Optional[str]
    collectionCid: Optional[str]
    storeStampedFiles: bool
    idempotent: bool
    idempotencyWindow: int


class VBaseClient:
    """Client for interacting with the VBase API for stamping files."""
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
            raise

        try:
            return response.json()
        except Exception as e:
            logger.error("Failed to parse JSON from stamp response: %s", response.text)
            raise e
