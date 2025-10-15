"""Open edX content library hierarchy management"""
import logging
import requests
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class OpenEdXHierarchyManager:
    """Manages collections and content organization in Open edX"""
    
    def __init__(self, library_id: str, api_url: str, cookies: Dict[str, str]):
        self.library_id = library_id
        self.api_url = api_url.rstrip('/')
        self.cookies = cookies
        self.headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'USE-JWT-COOKIE': 'true',
            'X-CSRFToken': cookies.get('csrftoken', ''),
            'Referer': f'{api_url}/',
            'Origin': api_url
        }
    
    def delete_all_blocks(self) -> int:
        """Delete all blocks in library"""
        blocks = self._get_all_blocks()
        deleted = 0
        for block in blocks:
            if self._delete_block(block['id']):
                deleted += 1
        logger.info(f"Deleted {deleted} blocks")
        return deleted
    
    def create_collection(self, name: str, description: str = "") -> Dict[str, Any]:
        """Create a collection (folder) in the library"""
        url = f"{self.api_url}/api/libraries/v2/{self.library_id}/collections/"
        payload = {"title": name, "description": description}
        
        try:
            resp = requests.post(url, json=payload, cookies=self.cookies, headers=self.headers, timeout=30)
            if resp.status_code in [200, 201]:
                result = resp.json()
                logger.info(f"Created collection: {name}")
                return result
            else:
                logger.error(f"Collection creation failed: {resp.status_code} - {resp.text[:200]}")
                return {}
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
            return {}
    
    def add_block_to_collection(self, block_id: str, collection_key: str) -> bool:
        """Add a block to a collection"""
        url = f"{self.api_url}/api/libraries/v2/blocks/{block_id}/collections/"
        payload = {"collections": [collection_key]}
        
        try:
            resp = requests.patch(url, json=payload, cookies=self.cookies, headers=self.headers, timeout=30)
            return resp.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error adding block to collection: {e}")
            return False
    
    def publish_library(self) -> bool:
        """Publish library to make content visible"""
        url = f"{self.api_url}/api/libraries/v2/{self.library_id}/commit/"
        try:
            resp = requests.post(url, cookies=self.cookies, headers=self.headers, timeout=30)
            if resp.status_code in [200, 201]:
                logger.info("Library published successfully")
                return True
            return False
        except Exception as e:
            logger.error(f"Publish error: {e}")
            return False
    
    def _get_all_blocks(self) -> List[Dict[str, Any]]:
        """Get all blocks in library"""
        url = f"{self.api_url}/api/libraries/v2/{self.library_id}/blocks/"
        try:
            resp = requests.get(url, cookies=self.cookies, headers=self.headers, timeout=30)
            if resp.status_code == 200:
                return resp.json().get('results', [])
        except Exception as e:
            logger.error(f"Error getting blocks: {e}")
        return []
    
    def _delete_block(self, block_id: str) -> bool:
        """Delete a single block"""
        url = f"{self.api_url}/api/libraries/v2/blocks/{block_id}/"
        try:
            resp = requests.delete(url, cookies=self.cookies, headers=self.headers, timeout=30)
            return resp.status_code in [200, 204]
        except Exception as e:
            logger.error(f"Error deleting block {block_id}: {e}")
            return False
