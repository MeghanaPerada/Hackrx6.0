# src/utils/aikipedia_api.py
"""Aikipedia Workers API integration for PPTX image processing"""

import base64
import httpx
from typing import Optional, Dict, Any, Tuple
from pathlib import Path

from ..core.config import API_BASE_URL, USER_ID

class AikipediaAPI:
    """Client for Aikipedia Workers API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.timeout = 120.0
    
    async def upload_image(self, image_path: str, user_id: str = USER_ID) -> Optional[Dict[str, str]]:
        """
        Upload image to Aikipedia API and get public URL
        
        Args:
            image_path: Local path to image file
            user_id: User identifier for the upload
            
        Returns:
            Dict with 'url' and 'storage_path' keys, or None if failed
        """
        try:
            # Read and convert image to base64
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            base64_image = "data:image/png;base64," + base64.b64encode(image_data).decode()
            filename = Path(image_path).name
            
            payload = {
                "image_base64": base64_image,
                "filename": filename,
                "user_id": user_id
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/upload-image",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return {
                    "url": result.get("url"),
                    "storage_path": result.get("storage_path")
                }
                
        except Exception as e:
            print(f"❌ Error uploading image {image_path}: {e}")
            return None
    
    async def analyze_image(self, image_url: str, description_prompt: str, user_id: str = USER_ID) -> Optional[str]:
        """
        Analyze image using vision API
        
        Args:
            image_url: Public URL of the uploaded image
            description_prompt: Prompt for image analysis
            user_id: User identifier
            
        Returns:
            Detailed image description or None if failed
        """
        try:
            payload = {
                "message": description_prompt,
                "user_id": user_id,
                "image_url": image_url
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/chat",
                    json=payload
                )
                response.raise_for_status()
                
                result = response.json()
                return result.get("response", str(result))
                
        except Exception as e:
            print(f"❌ Error analyzing image {image_url}: {e}")
            return None
    
    async def delete_image(self, storage_path: str, user_id: str = USER_ID) -> bool:
        """
        Delete uploaded image from external storage
        
        Args:
            storage_path: Storage path returned from upload
            user_id: User identifier
            
        Returns:
            True if successful, False otherwise
        """
        try:
            payload = {
                "storage_path": storage_path,
                "user_id": user_id
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/delete-image",
                    json=payload
                )
                response.raise_for_status()
                return True
                
        except Exception as e:
            print(f"❌ Error deleting image {storage_path}: {e}")
            return False
    
    async def process_image_with_cleanup(self, image_path: str, description_prompt: str, user_id: str = USER_ID) -> Optional[str]:
        """
        Complete image processing workflow with automatic cleanup
        
        Args:
            image_path: Local path to image file
            description_prompt: Prompt for image analysis
            user_id: User identifier
            
        Returns:
            Image description or None if failed
        """
        upload_result = None
        try:
            # Step 1: Upload image
            upload_result = await self.upload_image(image_path, user_id)
            if not upload_result or not upload_result.get("url"):
                return None
            
            # Step 2: Analyze image
            description = await self.analyze_image(
                upload_result["url"], 
                description_prompt, 
                user_id
            )
            
            return description
            
        finally:
            # Step 3: Cleanup (always attempt, even if analysis failed)
            if upload_result and upload_result.get("storage_path"):
                await self.delete_image(upload_result["storage_path"], user_id)


# Default image description prompt for PPTX slides
DEFAULT_IMAGE_DESCRIPTION_PROMPT = """
Analyze this image from a PowerPoint slide and provide a detailed, factual description. Focus on:

1. **Text Content**: Transcribe any visible text, headings, labels, or captions exactly as they appear
2. **Visual Elements**: Describe charts, graphs, diagrams, photos, illustrations, or other visual components
3. **Data & Information**: If there are tables, charts, or data visualizations, describe the key information they convey
4. **Layout & Structure**: Describe how elements are arranged and organized
5. **Context Clues**: Note any indicators of the slide's purpose or topic

Provide a comprehensive but concise description that would help someone understand the slide's content without seeing it. Focus on factual, observable elements rather than interpretations.
"""

# Global API client instance
_api_client = None

def get_aikipedia_client() -> AikipediaAPI:
    """Get singleton Aikipedia API client"""
    global _api_client
    if _api_client is None:
        _api_client = AikipediaAPI()
    return _api_client