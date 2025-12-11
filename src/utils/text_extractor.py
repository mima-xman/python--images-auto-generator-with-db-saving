"""
Text Extraction Utilities
"""

import re
from typing import Dict, List, Optional


def extract_metadata(response_text: str) -> Dict[str, Optional[str]]:
    """
    Extract metadata using markers
    
    Args:
        response_text: AI response text with markers
        
    Returns:
        Dictionary with extracted metadata
    """
    try:
        def get_marker_content(text: str, marker: str) -> Optional[str]:
            pattern = rf'\[@{marker}-start\](.*?)\[@{marker}-end\]'
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            return match.group(1).strip() if match else None
        
        extracted = {
            "prompt": get_marker_content(response_text, "prompt"),
            "title": get_marker_content(response_text, "title"),
            "category": get_marker_content(response_text, "category"),
            "description": get_marker_content(response_text, "description"),
            "keywords": get_marker_content(response_text, "keywords")
        }
        
        # Convert keywords to list
        if extracted["keywords"]:
            extracted["keywords"] = [k.strip() for k in extracted["keywords"].split(",")]
        
        return extracted
    except Exception as e:
        print(f"❌ Error extracting info: {e}")
        return {
            "prompt": None,
            "title": None,
            "category": None,
            "description": None,
            "keywords": []
        }
